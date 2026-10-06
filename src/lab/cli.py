"""Rich interactive CLI for the Deep Agents lab harness.

    python -m lab.cli --baseline      # or --subagents / --skill
    lab --subagents --session a1b2c3d4

Slash commands: /quit /new /mode-baseline /mode-subagents /mode-skill
                /sessions /resume [id] /skills /help /clear
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
from pathlib import Path

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .session import (
    DATA_DIR,
    MODES,
    AgentSession,
    SessionStore,
    list_auto_skills,
    short_id,
)

MODEL_ID = os.getenv("LAB_MODEL", "unknown")


# --------------------------------------------------------------------------- status
class StatusBar:
    """One-line footer shown live while a turn runs and as a static line when idle."""

    def __init__(self, session: dict, label: str = "ready"):
        self.session_id = session["id"]
        self.mode = session["mode"]
        self.turn = int(session.get("turn_count", 0))
        self.total_tokens = int(session.get("total_tokens", 0))
        self.last = None
        self.label = label

    def apply(self, turn) -> None:
        self.turn = turn.turn
        self.total_tokens += turn.total_tokens
        self.last = turn
        self.label = "error" if turn.error else "ready"

    def render(self) -> Text:
        t = Text()
        t.append(f" {self.mode} ", style="bold white on blue")
        t.append(f"  session {self.session_id}", style="dim")
        t.append(f"  ·  turn {self.turn}", style="bold")
        t.append(f"  ·  session tokens {self.total_tokens:,}", style="cyan")
        if self.last is not None:
            t.append(
                f"  ·  last {self.last.input_tokens:,} in / {self.last.output_tokens:,} out "
                f"/ {self.last.total_tokens:,} tok",
                style="dim",
            )
            t.append(
                f"  ·  tools {self.last.tool_calls}  subagents {self.last.subagent_calls} "
                f" skills {self.last.skills_read}  {self.last.seconds}s",
                style="dim",
            )
        style = "red" if self.label == "error" else "yellow"
        t.append(f"  ·  {self.label}", style=style)
        t.append(f"  ·  {MODEL_ID}", style="dim")
        return t


def create_session(store: SessionStore, data_dir: Path, args: argparse.Namespace,
                   mode: str, title: str = "", sid: str | None = None) -> dict:
    """Create a session row: direct (work in --workdir) or copied under --data-dir."""
    sid = sid or short_id()
    if args.workdir:
        workdir = Path(args.workdir).expanduser().resolve()
        return store.create_session(mode, workdir, title=title, sid=sid, direct=True)
    workspace_dir = data_dir / "sessions" / sid
    session = store.create_session(mode, workspace_dir, title=title, sid=sid)
    if args.workspace:
        src = Path(args.workspace)
        if src.exists():
            shutil.copytree(src, workspace_dir / "workspace", dirs_exist_ok=True)
    return session


# --------------------------------------------------------------------------- CLI
class Cli:
    def __init__(self, console: Console, store: SessionStore, sess: AgentSession,
                 data_dir: Path, args: argparse.Namespace):
        self.console = console
        self.store = store
        self.sess = sess
        self.data_dir = data_dir
        self.args = args
        self.last = None
        self._suppress_next_status = False

    # -- session factory ----------------------------------------------------
    def _make_session(self, mode: str, title: str = "") -> AgentSession:
        session = create_session(self.store, self.data_dir, self.args, mode, title=title)
        sess = AgentSession(self.store, session, self.data_dir, model=self.args.model_obj,
                            recursion_limit=self.args.recursion_limit, stream=not self.args.no_stream)
        self._print_warnings(sess)
        return sess

    def _print_warnings(self, sess: AgentSession) -> None:
        for w in sess.warnings:
            self.console.print(f"[yellow]warning:[/] {w}")

    # -- banner -------------------------------------------------------------
    def _banner(self) -> Panel:
        s = self.store.get_session(self.sess.session_id)
        where = "[green]direct[/] " if self.sess.direct else ""
        body = Text.from_markup(
            f"[bold]mode[/] {self.sess.mode}   [bold]session[/] {self.sess.session_id}\n"
            f"[bold]model[/] {MODEL_ID}   [bold]recursion[/] {self.args.recursion_limit}\n"
            f"[bold]workspace[/] {where}{self.sess.work_path}\n"
            f"[dim]slash: /quit /new /sessions /resume [id] /skills "
            f"/mode-baseline /mode-subagents /mode-skill /help[/]"
        )
        return Panel(body, title="[bold blue]Deep Agents CLI[/]", border_style="blue",
                     title_align="left", subtitle=(s["title"] or None))

    # -- main loop ----------------------------------------------------------
    def run(self, replay: bool = False) -> None:
        self.status = StatusBar(self.store.get_session(self.sess.session_id))
        last = self.store.last_turn(self.sess.session_id)
        if last:
            self.status.turn = last["turn"]
            self.status.total_tokens = self.store.get_session(self.sess.session_id)["total_tokens"]
        self.console.print(self._banner())
        if replay:
            self._replay()
        while True:
            if not self._suppress_next_status:
                self.console.print(self.status.render())
            self._suppress_next_status = False
            try:
                raw = self.console.input("[bold cyan]›[/] ").strip()
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[dim]bye[/]")
                break
            if not raw:
                continue
            if raw.startswith("/"):
                if self._handle_slash(raw):
                    break
                continue
            try:
                self._run_turn(raw)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]turn interrupted[/]")

    # -- turn ---------------------------------------------------------------
    def _run_turn(self, text: str) -> None:
        self.console.print(Panel(Text(text), title="[cyan]you[/]", title_align="left",
                                 border_style="cyan"))
        streamed = Text()

        def view():
            # answer and status live in the SAME region, so streaming never reprints the status
            if streamed.plain:
                return Group(
                    Panel(streamed, title="[green]assistant[/]", title_align="left",
                          border_style="green"),
                    self.status.render(),
                )
            return self.status.render()

        self.status.label = "thinking"

        def on_chunk(tok: str) -> None:
            streamed.append(tok)

        with Live(self.status.render(), console=self.console, refresh_per_second=12,
                  vertical_overflow="visible", get_renderable=view):
            result = self.sess.send(text, on_chunk=on_chunk if not self.args.no_stream else None)
            self.status.apply(result)
        self.console.print()

        if not streamed.plain and result.assistant_text:
            self.console.print(Panel(Markdown(result.assistant_text), title="[green]assistant[/]",
                                     title_align="left", border_style="green"))
        if result.error:
            self.console.print(Panel(result.error, title="[red]error[/]", border_style="red"))
        self.last = result
        self._suppress_next_status = True

    # -- slash commands -----------------------------------------------------
    def _handle_slash(self, raw: str) -> bool:
        try:
            parts = shlex.split(raw)
        except ValueError:
            parts = raw.split()
        cmd, rest = parts[0].lower(), parts[1:]
        arg = rest[0] if rest else ""

        if cmd in ("/quit", "/exit"):
            self.console.print("[dim]bye[/]")
            return True
        if cmd == "/help":
            self.console.print(self._help_panel())
        elif cmd == "/clear":
            self.console.clear()
        elif cmd == "/new":
            self.sess.cleanup()
            title = " ".join(rest)
            self.sess = self._make_session(self.sess.mode, title=title)
            self.last = None
            self.status = StatusBar(self.store.get_session(self.sess.session_id))
            self.console.clear()
            self.console.print(self._banner())
            self.console.print("[green]new session[/]")
        elif cmd in ("/mode-baseline", "/mode-subagents", "/mode-skill"):
            mode = cmd.replace("/mode-", "").replace("-", "_")
            mode = {"skill": "skill"}.get(mode, mode)
            self.sess.set_mode(mode)
            self.status.mode = mode
            self.console.print(f"[green]mode → {mode}[/]")
        elif cmd == "/sessions":
            self._print_sessions()
        elif cmd == "/resume":
            self._cmd_resume(arg)
        elif cmd == "/skills":
            self._print_skills()
        else:
            self.console.print(f"[red]unknown command:[/] {cmd}  (try /help)")
        return False

    def _cmd_resume(self, arg: str) -> None:
        if not arg:
            self._print_sessions()
            arg = Prompt.ask("session id (empty to cancel)", default="").strip()
        if not arg:
            return
        session = self.store.get_session(arg)
        if not session:
            self.console.print(f"[red]no such session:[/] {arg}")
            return
        self.sess.cleanup()
        self.sess = AgentSession(self.store, session, self.data_dir, model=self.args.model_obj,
                                 recursion_limit=self.args.recursion_limit,
                                 stream=not self.args.no_stream)
        self.console.clear()
        self.console.print(self._banner())
        self._print_warnings(self.sess)
        self._replay()

    # -- rendering helpers --------------------------------------------------
    def _replay(self) -> None:
        messages = self.store.get_messages(self.sess.session_id)
        if not messages:
            self.console.print("[dim](empty session)[/]")
            return
        self.console.print("[dim]── replay ──[/]")
        for m in messages:
            content = m.content if isinstance(m.content, str) else str(m.content)
            if m.type == "human":
                self.console.print(Panel(Text(content), title="[cyan]you[/]", title_align="left",
                                         border_style="cyan"))
            elif m.type == "ai":
                if content.strip():
                    self.console.print(Panel(Markdown(content), title="[green]assistant[/]",
                                             title_align="left", border_style="green"))
                for tc in getattr(m, "tool_calls", []) or []:
                    self.console.print(f"  [dim]· tool {tc['name']}({_brief(tc.get('args'))})[/]")
            elif m.type == "tool":
                self.console.print(f"  [dim]· result {_brief(content)}[/]")
        self.console.print("[dim]── end replay ──[/]")
        session = self.store.get_session(self.sess.session_id)
        last = self.store.last_turn(self.sess.session_id)
        self.status = StatusBar(session)
        if last:
            self.status.turn = last["turn"]
            self.status.total_tokens = session["total_tokens"]

    def _print_sessions(self) -> None:
        rows = self.store.list_sessions()
        table = Table(title="sessions", title_style="bold", show_lines=False)
        for col in ("id", "title", "mode", "turns", "tokens", "updated"):
            table.add_column(col)
        for s in rows:
            mark = " [green]←[/]" if s["id"] == self.sess.session_id else ""
            table.add_row(s["id"] + mark, (s["title"] or "")[:40], s["mode"],
                          str(s["turn_count"]), f"{s['total_tokens']:,}", s["updated_at"][:19])
        self.console.print(table)

    def _print_skills(self) -> None:
        skills = list_auto_skills()
        if not skills:
            self.console.print("[yellow]no skills in skills/auto[/] (run `python -m lab.curator`)")
            return
        loaded = self.sess.mode == "skill"
        table = Table(title=f"skills/auto  (mode={self.sess.mode}, loaded={loaded})")
        for col in ("name", "description", "lines", "used now"):
            table.add_column(col)
        for s in skills:
            table.add_row(s.name, s.description[:70], str(s.lines), "yes" if loaded else "no")
        self.console.print(table)

    def _help_panel(self) -> Panel:
        return Panel(
            Text.from_markup(
                "[bold]/quit[/]              exit\n"
                "[bold]/new [title][/]       new session (clears the screen)\n"
                "[bold]/sessions[/]          list sessions\n"
                "[bold]/resume [id][/]       resume and replay a session\n"
                "[bold]/mode-baseline[/]     switch to the default agent\n"
                "[bold]/mode-subagents[/]    switch to the multi-agent condition\n"
                "[bold]/mode-skill[/]        switch to the auto-skill condition\n"
                "[bold]/skills[/]            list skills in skills/auto\n"
                "[bold]/clear[/]             clear the screen\n"
                "[bold]/help[/]              this help"
            ),
            title="commands", border_style="blue", title_align="left",
        )


def _brief(value, limit: int = 90) -> str:
    text = value if isinstance(value, str) else str(value)
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


# --------------------------------------------------------------------------- entry
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="lab", description="Interactive Deep Agents CLI.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--baseline", dest="mode", action="store_const", const="baseline",
                   help="default single agent (no skills)")
    g.add_argument("--subagents", dest="mode", action="store_const", const="subagents",
                   help="multi-agent condition")
    g.add_argument("--skill", dest="mode", action="store_const", const="skill",
                   help="load curator-generated skills from skills/auto")
    ap.set_defaults(mode="baseline")
    ap.add_argument("--session", help="resume this session id on launch")
    ap.add_argument("--db", help="SQLite path (default <data-dir>/sessions.db)")
    ap.add_argument("--data-dir", help=f"session data dir (default {DATA_DIR})")
    ap.add_argument("--workspace", help="seed a new session's workspace from this directory (copy)")
    ap.add_argument("--workdir", "--dir", dest="workdir", metavar="DIR",
                    help="work directly in DIR: the agent reads and writes it in place (no copy)")
    ap.add_argument("--recursion-limit", type=int, default=60)
    ap.add_argument("--no-stream", action="store_true", help="wait for the full answer")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode not in MODES:
        args.mode = "baseline"
    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    db_path = Path(args.db) if args.db else data_dir / "sessions.db"
    console = Console()
    if args.workspace and args.workdir:
        console.print("[red]--workspace and --workdir are mutually exclusive[/]")
        return 1
    if args.workdir and not Path(args.workdir).expanduser().is_dir():
        console.print(f"[red]--workdir is not a directory:[/] {args.workdir}")
        return 1
    store = SessionStore(db_path)
    args.model_obj = None  # build_agent falls back to make_model()

    if args.session:
        session = store.get_session(args.session)
        if not session:
            console.print(f"[red]no such session:[/] {args.session}")
            return 1
        sess = AgentSession(store, session, data_dir, model=None,
                            recursion_limit=args.recursion_limit, stream=not args.no_stream)
    else:
        session = create_session(store, data_dir, args, args.mode, sid=short_id())
        sess = AgentSession(store, session, data_dir, model=None,
                            recursion_limit=args.recursion_limit, stream=not args.no_stream)

    cli = Cli(console, store, sess, data_dir, args)
    cli._print_warnings(sess)
    try:
        cli.run(replay=bool(args.session))
    finally:
        sess.cleanup()
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

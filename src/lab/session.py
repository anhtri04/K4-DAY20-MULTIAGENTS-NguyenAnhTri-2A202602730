"""Interactive session storage (SQLite) and multi-turn agent session for the CLI.

Two pieces:

* ``SessionStore``  - a thin SQLite layer: sessions, messages (the exact agent transcript,
  serialised with ``messages_to_dict``) and turns (per-turn metrics for the status line).
* ``AgentSession``  - one chat session: a persistent sandbox folder, an agent rebuilt from
  ``build_agent`` when the mode changes, and ``send`` which runs one turn by replaying the
  stored history plus the new user message.

Nothing here is graded: this module only reads the harness (``build_agent``, ``make_model``)
and never edits provided files.
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    messages_from_dict,
    messages_to_dict,
)

from .agent import build_agent
from .model import make_model
from .tasks import ROOT

DATA_DIR = ROOT / ".lab_cli"
AUTO_SKILLS_DIR = ROOT / "skills" / "auto"

# condition name -> (build_agent mode, use_skills)
MODES = {
    "baseline": ("single", False),
    "subagents": ("subagents", False),
    "skill": ("single", True),
}
MODE_LABELS = {
    "baseline": "baseline",
    "subagents": "subagents",
    "skill": "skill",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def short_id() -> str:
    return uuid.uuid4().hex[:8]


# --------------------------------------------------------------------------- store
class SessionStore:
    """SQLite persistence for chat sessions, transcripts and turn metrics."""

    def __init__(self, db_path: Path | str = DATA_DIR / "sessions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                mode TEXT NOT NULL,
                workspace_dir TEXT NOT NULL,
                direct INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                turn_count INTEGER NOT NULL DEFAULT 0,
                total_input_tokens INTEGER NOT NULL DEFAULT 0,
                total_output_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                turn INTEGER NOT NULL,
                position INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                turn INTEGER NOT NULL,
                user_text TEXT NOT NULL DEFAULT '',
                assistant_text TEXT NOT NULL DEFAULT '',
                input_tokens INTEGER NOT NULL DEFAULT 0,
                output_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                tool_calls INTEGER NOT NULL DEFAULT 0,
                subagent_calls INTEGER NOT NULL DEFAULT 0,
                skills_read INTEGER NOT NULL DEFAULT 0,
                seconds REAL NOT NULL DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id);
            CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, turn);
            """
        )
        # migration for databases created before the `direct` column existed
        cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(sessions)").fetchall()}
        if "direct" not in cols:
            self.conn.execute("ALTER TABLE sessions ADD COLUMN direct INTEGER NOT NULL DEFAULT 0")
        self.conn.commit()

    # -- sessions -----------------------------------------------------------
    def create_session(self, mode: str, workspace_dir: Path | str, title: str = "",
                       sid: str | None = None, direct: bool = False) -> dict:
        sid = sid or short_id()
        now = utc_now()
        self.conn.execute(
            "INSERT INTO sessions (id, title, mode, workspace_dir, direct, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sid, title, mode, str(workspace_dir), int(direct), now, now),
        )
        self.conn.commit()
        return self.get_session(sid)

    def get_session(self, sid: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        return dict(row) if row else None

    def list_sessions(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]

    def last_turn(self, sid: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM turns WHERE session_id = ? ORDER BY turn DESC LIMIT 1", (sid,)
        ).fetchone()
        return dict(row) if row else None

    def update_session(self, sid: str, **fields) -> None:
        allowed = {"title", "mode", "updated_at", "turn_count",
                   "total_input_tokens", "total_output_tokens", "total_tokens"}
        clean = {k: v for k, v in fields.items() if k in allowed}
        if not clean:
            return
        clean.setdefault("updated_at", utc_now())
        sets = ", ".join(f"{k} = ?" for k in clean)
        self.conn.execute(f"UPDATE sessions SET {sets} WHERE id = ?", (*clean.values(), sid))
        self.conn.commit()

    # -- messages -----------------------------------------------------------
    def add_messages(self, sid: str, turn: int, messages: list[BaseMessage]) -> None:
        pos = self.conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM messages WHERE session_id = ?", (sid,)
        ).fetchone()[0]
        rows = []
        for m in messages:
            if isinstance(m, BaseMessage) and m.type == "system":
                continue
            payload = json.dumps(messages_to_dict([m])[0], ensure_ascii=False)
            rows.append((sid, turn, pos, m.type, _content_text(m), payload))
            pos += 1
        if rows:
            self.conn.executemany(
                "INSERT INTO messages (session_id, turn, position, role, content, payload) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                rows,
            )
            self.conn.commit()

    def get_messages(self, sid: str) -> list[BaseMessage]:
        rows = self.conn.execute(
            "SELECT payload FROM messages WHERE session_id = ? ORDER BY id", (sid,)
        ).fetchall()
        out: list[BaseMessage] = []
        for r in rows:
            out.extend(messages_from_dict([json.loads(r["payload"])]))
        return out

    # -- turns --------------------------------------------------------------
    def add_turn(self, sid: str, **fields) -> None:
        cols = {
            "user_text": "", "assistant_text": "", "input_tokens": 0, "output_tokens": 0,
            "total_tokens": 0, "tool_calls": 0, "subagent_calls": 0, "skills_read": 0,
            "seconds": 0.0, "error": None,
        }
        cols.update({k: v for k, v in fields.items() if k in cols})
        self.conn.execute(
            "INSERT INTO turns (session_id, turn, user_text, assistant_text, input_tokens, "
            "output_tokens, total_tokens, tool_calls, subagent_calls, skills_read, seconds, error, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sid, fields["turn"], cols["user_text"], cols["assistant_text"], cols["input_tokens"],
             cols["output_tokens"], cols["total_tokens"], cols["tool_calls"], cols["subagent_calls"],
             cols["skills_read"], cols["seconds"], cols["error"], utc_now()),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


# --------------------------------------------------------------------------- helpers
def _content_text(message: BaseMessage) -> str:
    """Best-effort plain text of a message (content may be a list of blocks)."""
    content = message.content
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, ensure_ascii=False)
    except TypeError:
        return str(content)


def sum_usage(usage: UsageMetadataCallbackHandler) -> dict:
    totals = {"input": 0, "output": 0, "total": 0}
    for meta in usage.usage_metadata.values():
        totals["input"] += meta.get("input_tokens", 0)
        totals["output"] += meta.get("output_tokens", 0)
        totals["total"] += meta.get("total_tokens", 0)
    return totals


def tool_events(messages: list[BaseMessage], seen_calls: set, seen_results: set) -> list[dict]:
    """Diff a message list into tool-call / tool-result events not emitted yet.

    ``seen_calls`` / ``seen_results`` are caller-owned sets so the same full history can be
    scanned repeatedly (as the ``values`` stream grows) without emitting duplicates.
    """
    events: list[dict] = []
    for m in messages:
        if isinstance(m, AIMessage):
            for tc in m.tool_calls or []:
                key = tc.get("id") or f"{tc.get('name')}|{tc.get('args')}"
                if key in seen_calls:
                    continue
                seen_calls.add(key)
                events.append({"kind": "tool_call", "name": tc.get("name") or "tool",
                               "args": tc.get("args") or {}})
        elif m.type == "tool":
            key = getattr(m, "tool_call_id", None) or f"{getattr(m, 'name', None)}|{_content_text(m)}"
            if key in seen_results:
                continue
            seen_results.add(key)
            events.append({"kind": "tool_result", "name": getattr(m, "name", None) or "tool",
                           "content": _content_text(m)})
    return events


def count_skill_reads(messages: list[BaseMessage]) -> int:
    names = set()
    for m in messages:
        if not isinstance(m, AIMessage):
            continue
        for tc in m.tool_calls or []:
            if tc.get("name") != "read_file":
                continue
            fp = str((tc.get("args") or {}).get("file_path", ""))
            if "skills/" in fp:
                names.add(fp.split("skills/", 1)[1].split("/", 1)[0])
    return len(names)


@dataclass
class TurnResult:
    turn: int
    user_text: str
    assistant_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_calls: int = 0
    subagent_calls: int = 0
    skills_read: int = 0
    seconds: float = 0.0
    error: str | None = None
    new_messages: list[BaseMessage] = field(default_factory=list)


@dataclass
class SkillInfo:
    name: str
    description: str
    lines: int
    path: Path


_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def list_auto_skills() -> list[SkillInfo]:
    """List the skills the curator wrote in skills/auto/<name>/SKILL.md."""
    skills: list[SkillInfo] = []
    if not AUTO_SKILLS_DIR.exists():
        return skills
    for folder in sorted(p for p in AUTO_SKILLS_DIR.iterdir() if (p / "SKILL.md").exists()):
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        name, desc = folder.name, ""
        m = _FRONTMATTER.match(text.strip() + "\n")
        if m:
            nm = re.search(r"^name:\s*(.+)$", m.group(1), re.M)
            dm = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
            name = nm.group(1).strip() if nm else name
            desc = dm.group(1).strip() if dm else ""
        skills.append(SkillInfo(name=name, description=desc,
                                lines=len(text.strip().splitlines()), path=folder / "SKILL.md"))
    return skills


# --------------------------------------------------------------------------- agent session
class AgentSession:
    """One interactive chat session backed by a persistent sandbox and the lab harness."""

    def __init__(self, store: SessionStore, session: dict, data_dir: Path | str = DATA_DIR,
                 model=None, recursion_limit: int = 60, stream: bool = True):
        self.store = store
        self.data_dir = Path(data_dir)
        self.session_id = session["id"]
        self.mode = session["mode"]
        self.sandbox = Path(session["workspace_dir"])
        self.model = model
        self.recursion_limit = recursion_limit
        self.stream = stream
        self.direct = bool(session.get("direct"))
        self.turn = int(session.get("turn_count", 0))
        self.agent = None
        self.warnings: list[str] = []
        self._created_workspace_link = False
        self._created_skills_dir: Path | None = None
        self._ensure_workspace()
        self._build_agent()

    # -- setup --------------------------------------------------------------
    @property
    def work_path(self) -> Path:
        """The directory the agent actually edits (the selected dir in direct mode)."""
        return self.sandbox if self.direct else self.sandbox / "workspace"

    def _ensure_workspace(self) -> None:
        self.sandbox.mkdir(parents=True, exist_ok=True)
        link = self.sandbox / "workspace"
        if not self.direct:
            link.mkdir(parents=True, exist_ok=True)
            return
        # direct mode: agent root is the selected dir; `workspace/` must resolve back inside it
        if link.is_symlink():
            return
        if link.exists() and not link.is_dir():
            raise ValueError(f"cannot use {self.sandbox}: a non-directory 'workspace' entry exists")
        if link.is_dir():
            self.warnings.append(
                f"{self.sandbox} already has a real 'workspace/' folder; the agent will work inside it")
            return
        link.symlink_to(".")
        self._created_workspace_link = True

    def _sync_skills(self) -> None:
        dst = self.sandbox / "skills"
        if dst.exists():
            if self.direct:
                self.warnings.append(f"direct mode: using the existing {dst} (skills/auto not copied)")
                return
            shutil.rmtree(dst)
        if AUTO_SKILLS_DIR.exists():
            for skill in sorted(p for p in AUTO_SKILLS_DIR.iterdir() if (p / "SKILL.md").exists()):
                shutil.copytree(skill, dst / skill.name, dirs_exist_ok=True)
            if self.direct:
                self._created_skills_dir = dst

    def cleanup(self) -> None:
        """Remove artifacts this session created in direct mode (never touches real files)."""
        if self._created_skills_dir is not None and self._created_skills_dir.exists():
            shutil.rmtree(self._created_skills_dir, ignore_errors=True)
        link = self.sandbox / "workspace"
        if self._created_workspace_link and link.is_symlink():
            link.unlink(missing_ok=True)

    def _build_agent(self) -> None:
        mode, use_skills = MODES[self.mode]
        if use_skills:
            self._sync_skills()
        self.agent = build_agent(self.sandbox, mode=mode, use_skills=use_skills, model=self.model)

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError(f"unknown mode: {mode}")
        self.mode = mode
        self.store.update_session(self.session_id, mode=mode)
        self._build_agent()

    # -- one turn -----------------------------------------------------------
    def send(self, text: str, on_chunk=None, on_event=None) -> TurnResult:
        """Run one turn: replay stored history + ``text``, persist and return metrics.

        ``on_chunk`` streams answer tokens; ``on_event`` streams structured tool activity as
        ``{"kind": "tool_call"|"tool_result", ...}`` so the CLI can show what the agent is doing.
        """
        history = self.store.get_messages(self.session_id)
        user = HumanMessage(content=text)
        inputs = history + [user]
        usage = UsageMetadataCallbackHandler()
        turn = self.turn + 1
        result = TurnResult(turn=turn, user_text=text)
        seen_calls: set = set()
        seen_results: set = set()

        def emit_events(messages) -> None:
            if on_event is None:
                return
            for event in tool_events(messages, seen_calls, seen_results):
                on_event(event)

        t0 = time.perf_counter()
        final_state = None
        try:
            config = {"callbacks": [usage], "recursion_limit": self.recursion_limit}
            if self.stream and (on_chunk is not None or on_event is not None):
                for mode, data in self.agent.stream(
                    {"messages": inputs}, config=config, stream_mode=["messages", "values"]
                ):
                    if mode == "messages":
                        chunk, meta = data
                        if (on_chunk is not None and isinstance(chunk, AIMessage)
                                and meta.get("langgraph_node") == "model" and chunk.content):
                            on_chunk(str(chunk.content))
                    else:
                        final_state = data
                        emit_events(data.get("messages", []))
            else:
                final_state = self.agent.invoke({"messages": inputs}, config=config)
                emit_events(final_state.get("messages", []))
        except Exception as exc:  # noqa: BLE001
            result.error = f"{type(exc).__name__}: {exc}"

        result.seconds = round(time.perf_counter() - t0, 1)
        totals = sum_usage(usage)
        result.input_tokens, result.output_tokens, result.total_tokens = (
            totals["input"], totals["output"], totals["total"])

        messages = (final_state or {}).get("messages", [])
        if messages and len(messages) >= len(inputs):
            result.new_messages = messages[len(inputs):]

        ai_messages = [m for m in result.new_messages if isinstance(m, AIMessage)]
        for m in ai_messages:
            for tc in m.tool_calls or []:
                result.tool_calls += 1
                if tc.get("name") == "task":
                    result.subagent_calls += 1
        result.skills_read = count_skill_reads(result.new_messages)
        for m in reversed(ai_messages):
            if isinstance(m.content, str) and m.content.strip():
                result.assistant_text = m.content
                break

        # persist user + new messages + turn metrics
        self.store.add_messages(self.session_id, turn, [user])
        if result.new_messages:
            self.store.add_messages(self.session_id, turn, result.new_messages)
        self.store.add_turn(
            self.session_id, turn=turn, user_text=text, assistant_text=result.assistant_text,
            input_tokens=result.input_tokens, output_tokens=result.output_tokens,
            total_tokens=result.total_tokens, tool_calls=result.tool_calls,
            subagent_calls=result.subagent_calls, skills_read=result.skills_read,
            seconds=result.seconds, error=result.error,
        )
        self.turn = turn
        session = self.store.get_session(self.session_id)
        updates = {
            "turn_count": turn,
            "total_input_tokens": (session["total_input_tokens"] + result.input_tokens),
            "total_output_tokens": (session["total_output_tokens"] + result.output_tokens),
            "total_tokens": (session["total_tokens"] + result.total_tokens),
        }
        if not session["title"] and text.strip():
            updates["title"] = text.strip().splitlines()[0][:60]
        self.store.update_session(self.session_id, **updates)
        return result

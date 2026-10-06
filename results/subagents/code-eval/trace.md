### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by exploring the workspace to understand the codebase.

### Tool call: ls
{"path": "workspace"}

### Tool call: glob
{"pattern": "workspace/**/*.py"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md"}

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: execute
{"command": "ls -la /workspace && find /workspace -type f | head -50"}

### Tool call: execute
{"command": "cd /workspace && python -m pytest tests -q 2>&1 | tail -20"}

### Tool result
[stderr] ls: cannot access '/workspace': No such file or directory

Exit code: 2
[Command failed with exit code 2]

### Tool result
[stderr] /bin/sh: line 1: cd: /workspace: No such file or directory

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "pwd && ls -la"}

### Tool result
/tmp/lab-sandbox-_k1ypc0o
total 0
drwx------  3 anhtri04 anhtri04  60 Oct  6 16:19 .
drwxrwxrwt 27 root     root     740 Oct  6 16:19 ..
drwxr-xr-x  4 anhtri04 anhtri04 120 Oct  6 13:41 workspace

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "ls -la workspace workspace/bookings workspace/tests && python -V"}

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -30"}

### Tool result
workspace:
total 8
drwxr-xr-x 4 anhtri04 anhtri04 120 Oct  6 13:41 .
drwx------ 3 anhtri04 anhtri04  60 Oct  6 16:19 ..
-rw-r--r-- 1 anhtri04 anhtri04  54 Oct  6 13:41 CHANGELOG.md
-rw-r--r-- 1 anhtri04 anhtri04 118 Oct  6 13:41 README.md
drwxr-xr-x 3 anhtri04 anhtri04 160 Oct  6 13:44 bookings
drwxr-xr-x 3 anhtri04 anhtri04  80 Oct  6 13:44 tests

workspace/bookings:
total 20
drwxr-xr-x 3 anhtri04 anhtri04 160 Oct  6 13:44 .
drwxr-xr-x 4 anhtri04 anhtri04 120 Oct  6 13:41 ..
-rw-r--r-- 1 anhtri04 anhtri04  22 Oct  6 13:41 __init__.py
drwxr-xr-x 2 anhtri04 anhtri04 140 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04 333 Oct  6 13:41 billing.py
-rw-r--r-- 1 anhtri04 anhtri04 211 Oct  6 13:41 calendar_export.py
-rw-r--r-- 1 anhtri04 anhtri04 467 Oct  6 13:41 schedule.py
-rw-r--r-- 1 anhtri04 anhtri04 513 Oct  6 13:41 timeutil.py

workspace/tests:
total 4
drwxr-xr-x 3 anhtri04 anhtri04  80 Oct  6 13:44 .
drwxr-xr-x 4 anhtri04 anhtri04 120 Oct  6 13:41 ..
drwxr-xr-x 2 anhtri04 anhtri04  60 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04 371 Oct  6 13:41 test_bookings.py
Python 3.14.7

[Command succeeded with exit code 0]

### Tool result

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
________________________ test_billable_blocks_rounds_up ________________________

    def test_billable_blocks_rounds_up():
>       assert billable_blocks(20) == 2
E       assert 1 == 2
E        +  where 1 = billable_blocks(20)

~/ai20k/K4-DAY20-MULTIAGENTS-NguyenAnhTri-2A202602730/tasks/code-eval/workspace/tests/test_bookings.py:10: AssertionError
=========================== short test summary info ============================
FAILED tests/test_bookings.py::test_total_minutes_mixed_formats - ValueError:...
FAILED tests/test_bookings.py::test_billable_blocks_rounds_up - assert 1 == 2
2 failed, 1 passed in 0.02s

[Command succeeded with exit code 0]

### Tool call: glob
{"pattern": "**/*"}

### Tool call: execute
{"command": "ls -la /tmp/lab-sandbox-_k1ypc0o; ls -la ~ 2>/dev/null | head -30"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-314.pyc', '/workspace/bookings/__pycache__/billing.cpython-314.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-314.pyc', '/workspace/bookings/__pycache__/schedule.cpython-314.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-314.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-314-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool result
total 0
drwx------  3 anhtri04 anhtri04  60 Oct  6 16:19 .
drwxrwxrwt 27 root     root     740 Oct  6 16:20 ..
drwxr-xr-x  5 anhtri04 anhtri04 140 Oct  6 16:20 workspace
total 0
drwx------  3 anhtri04 anhtri04  60 Oct  6 16:19 .
drwxrwxrwt 27 root     root     740 Oct  6 16:20 ..
drwxr-xr-x  5 anhtri04 anhtri04 140 Oct  6 16:20 workspace

[Command succeeded with exit code 0]

### Assistant
Now I understand the codebase. Let me examine the bugs and fix each module.

### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n_HOURS_MINUTES_RE = re.compile(r\"(\\d+)h(?:(\\d+)m)?\")\n_MINUTES_RE = re.compile(r\"(\\d+)m\")\n_CLOCK_RE = re.compile(r\"(\\d+):(\\d{1,2})\")\n_BARE_MINUTES_RE = re.compile(r\"(\\d+)\")\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n    stripped = text.strip()\n\n    m = _HOURS_MINUTES_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2) or 0)\n\n    m = _MINUTES_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1))\n\n    m = _CLOCK_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n\n    m = _BARE_MINUTES_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1))\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(f\"minutes must be >= 0, got {minutes!r}\")\n    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    return math.ceil(minutes / block)\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations):\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        return [slot]\n    return [*slots, slot]\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool result
Updated file /workspace/bookings/billing.py

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5 && python - <<'PY'\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.calendar_export import slot_end\n\ncases = {\"1h30m\":90, \"2h\":120, \"45m\":45, \"1:30\":90, \"45\":45, \" 1h30m \":90, \"0m\":0, \"0:00\":0, \"10h\":600, \"1:5\":65, \"90\":90, \"0\":0}\nfor k,v in cases.items():\n    got = parse_duration(k)\n    assert got==v, (k,got,v)\n    print(repr(k), got)\nfor bad in [\"\", \"abc\", \"1h30\", \"h\", \"1:2:3\", \"1h30x\", \"-5\", \"1.5h\", None, 45, \"1:\", \":30\"]:\n    try:\n        parse_duration(bad); print(\"NO RAISE\", repr(bad))\n    except ValueError as e:\n        pass\ntry:\n    parse_duration(bad)\nexcept ValueError:\n    pass\nprint(\"bill\", [billable_blocks(x) for x in (0,1,15,16,20,30,45,60)], billable_blocks(16, block=10))\ntry: billable_blocks(-1)\nexcept ValueError as e: print(\"neg ok:\", e)\nprint(\"add\", add_slot(\"a\"), add_slot(\"b\"), add_slot(\"c\", [\"x\"]))\nsrc=[\"x\"]; out=add_slot(\"y\", src); print(src, out)\nprint(\"total\", total_minutes([\"1h30m\",\"2h\",\"45\",\"1:30\"]))\nprint(\"slot_end\", slot_end(600, \"1h30m\"))\nPY"}

### Tool result
...                                                                      [100%]
3 passed in 0.00s
'1h30m' 90
'2h' 120
'45m' 45
'1:30' 90
'45' 45
' 1h30m ' 90
'0m' 0
'0:00' 0
'10h' 600
'1:5' 65
'90' 90
'0' 0
bill [0, 1, 1, 2, 2, 2, 3, 4] 2
neg ok: minutes must be >= 0, got -1
add ['a'] ['b'] ['x', 'c']
['x'] ['x', 'y']
total 345
slot_end 690

[Command succeeded with exit code 0]

### Assistant
Tests pass. Now let me add spec-coverage tests (without touching existing test files) and record the changes in the changelog.

### Tool call: write_file
{"content": "\"\"\"Tests for the documented behaviour of the bookings package.\n\nThese cover the cases named in the docstrings of ``bookings.timeutil``,\n``bookings.billing``, ``bookings.schedule`` and ``bookings.calendar_export``.\n\"\"\"\nimport pytest\n\nfrom bookings.billing import billable_blocks\nfrom bookings.calendar_export import slot_end\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\n\n\n@pytest.mark.parametrize(\n    (\"text\", \"expected\"),\n    [\n        (\"1h30m\", 90),\n        (\"2h\", 120),\n        (\"45m\", 45),\n        (\"1:30\", 90),\n        (\"45\", 45),\n        (\"0m\", 0),\n        (\"0:00\", 0),\n        (\" 1h30m \", 90),\n        (\"\\t2h\\n\", 120),\n    ],\n)\ndef test_parse_duration_supported_formats(text, expected):\n    assert parse_duration(text) == expected\n\n\n@pytest.mark.parametrize(\"text\", [\"\", \"abc\", \"1h30\", \"1h30x\", \"1:2:3\", \"-5\", None, 45])\ndef test_parse_duration_rejects_bad_input(text):\n    with pytest.raises(ValueError):\n        parse_duration(text)\n\n\n@pytest.mark.parametrize(\n    (\"minutes\", \"expected\"),\n    [(0, 0), (1, 1), (15, 1), (16, 2), (20, 2), (30, 2), (31, 3), (45, 3)],\n)\ndef test_billable_blocks_rounds_up(minutes, expected):\n    assert billable_blocks(minutes) == expected\n\n\ndef test_billable_blocks_custom_block_size():\n    assert billable_blocks(16, block=10) == 2\n\n\ndef test_billable_blocks_rejects_negative_minutes():\n    wi

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n", "new_string": "## Unreleased\n- `parse_duration` now supports every documented format (\"1h30m\", \"2h\", \"45m\", \"1:30\", \"45\").\n- `billable_blocks` rounds partial blocks up instead of using banker's rounding and rejects negative minutes.\n- `add_slot` no longer shares a mutable default list between calls and no longer mutates its input.\n"}

### Tool result
Updated file /workspace/tests/test_edge_cases.py

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5"}

### Tool result

tests/test_edge_cases.py:73: AssertionError
=========================== short test summary info ============================
FAILED tests/test_edge_cases.py::test_total_minutes_handles_every_supported_format
1 failed, 34 passed in 0.04s

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "workspace/tests/test_edge_cases.py", "old_string": "    assert total_minutes([\"1h30m\", \"2h\", \"45m\", \"1:30\", \"45\"]) == 360", "new_string": "    assert total_minutes([\"1h30m\", \"2h\", \"45m\", \"1:30\", \"45\"]) == 390"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/tests/test_edge_cases.py'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5"}

### Tool result
...................................                                      [100%]
35 passed in 0.02s

[Command succeeded with exit code 0]

### Tool call: task
{"subagent_type": "reviewer", "description": "Independently verify the bookings package fix.\n\nCONTEXT\nSandbox root: /tmp/lab-sandbox-_k1ypc0o (shell starts there; all paths below are relative to it and never start with '/').\nPackage under repair: `workspace/bookings/` with files `__init__.py`, `billing.py`, `calendar_export.py`, `schedule.py`, `timeutil.py`.\nTests: `workspace/tests/test_bookings.py` (pre-existing, MUST NOT be modified) and `workspace/tests/test_edge_cases.py` (newly added).\n`workspace/CHANGELOG.md` has an \"Unreleased\" section that was updated.\n\nTASK REQUIREMENTS (the docstrings are the specification)\n1. `bookings.timeutil.parse_duration(text)` must return whole minutes (int) for: \"1h30m\"->90, \"2h\"->120, \"45m\"->45, \"1:30\"->90, \"45\"->45 (bare number = minutes); surrounding whitespace ignored; anything unsupported raises ValueError.\n2. `bookings.billing.billable_blocks(minutes, block=15)` must always round UP (16 min / 15-min blocks -> 2), `minutes` must be >= 0 and a negative value raises ValueError.\n3. `bookings.schedule.add_slot(slot, slots=...)` must return a NEW list with `slot` appended and must never share state between separate calls.\n4. `bookings.schedule.total_minutes(durations)` = sum of parse_duration over the list.\n5. `bookings.calendar_export.slot_end(start_minute, duration_text)` = start_minute + parse_duration(duration_text).\n6. The whole test suite must pass: `cd workspace && python -m pytest tests -q`.\n\nWHAT I WANT Y

### Tool result
## Verdict: **PASS** — the fix satisfies every stated requirement and the whole suite is green.

### 1. Test suite (exact output)
```
$ cd workspace && python -m pytest tests -q
...................................                                      [100%]
35 passed in 0.03s
EXIT=0
```
- `tests/test_bookings.py` alone: `3 passed`
- `tests/test_edge_cases.py` alone: `32 passed`
- Also green with `-p no:cacheprovider` (no warnings-as-errors triggered).

Integrity check: `test_bookings.py` mtime `13:41` (same as untouched `bookings/__init__.py` and `calendar_export.py`), whereas the repaired files and `test_edge_cases.py` are `16:20` — consistent with "pre-existing test untouched". No VCS in the sandbox to diff further.

### 2. Spec-by-spec verification (all PASS)
| Req | Probe | Result |
|---|---|---|
| 1 | `"1h30m"→90, "2h"→120, "45m"→45, "1:30"→90, "45"→45, "0"→0, "0m"→0, "1h"→60, "0:15"→15, "23:59"→1439, `" 1h30m "`→90, `"\t1h\n"`→60` | all correct, all return `int` |
| 1 | `"", "   ", "\t\n", "abc", "1h30", "1:2:3", "1h30x", "-5", "1.5", "h", "m", ":", "+5", "1,5", "5m1h", "1:2:3:4", "1H30M", "1h-30m"` | all raise `ValueError` |
| 1 | non-str: `None, 45, 45.0, [], {}, (), b"45m", True, object()` | all raise `ValueError` |
| 2 | `0→0,1→1,14→1,15→1,16→2,29→2,30→2,31→3,45→3,59→4,60→4,61→5,90→6,91→7,1000→67` | exact match to hand-computed round-up table |
| 2 | `block=10: 16→2`; `(1,1)→1,(1,2)→1,(0,7)→0,(31,30)→2,(61,60)→2`; floats `16.5→2, 0.5→1, 0.0→0, 1.0000001→2, 14.999→1`

### Assistant
The reviewer flagged two low-severity items I can address: float precision in the rounding and a long line in my test file.

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes, block=15):", "new_string": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes, block=15):"}

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    return math.ceil(minutes / block)", "new_string": "    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    # Integer-safe round-up; math.ceil(minutes / block) would go through\n    # float and could round down for very large values.\n    return -(-minutes // block)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool result
Error: parallel file mutations to the same path are not allowed.

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    return math.ceil(minutes / block)", "new_string": "    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    # Integer-safe round-up; math.ceil(minutes / block) would go through\n    # float and could round down for very large values.\n    return -(-minutes // block)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_edge_cases.py", "limit": 40, "offset": 25}

### Tool result
@@ lines 1-17 of 17 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    if minutes < 0:
        raise ValueError(f"minutes must be >= 0, got {minutes!r}")
    if block <= 0:
        raise ValueError(f"block must be > 0, got {block!r}")
    # Integer-safe round-up; math.ceil(minutes / block) would go through
    # float and could round down for very large values.
    return -(-minutes // block)

### Tool result
@@ lines 26-65 of 77 | next offset 65 @@
    ],
)
def test_parse_duration_supported_formats(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "1h30", "1h30x", "1:2:3", "-5", None, 45])
def test_parse_duration_rejects_bad_input(text):
    with pytest.raises(ValueError):
        parse_duration(text)


@pytest.mark.parametrize(
    ("minutes", "expected"),
    [(0, 0), (1, 1), (15, 1), (16, 2), (20, 2), (30, 2), (31, 3), (45, 3)],
)
def test_billable_blocks_rounds_up(minutes, expected):
    assert billable_blocks(minutes) == expected


def test_billable_blocks_custom_block_size():
    assert billable_blocks(16, block=10) == 2


def test_billable_blocks_rejects_negative_minutes():
    with pytest.raises(ValueError):
        billable_blocks(-1)


def test_add_slot_does_not_share_state():
    assert add_slot("a") == ["a"]
    assert add_slot("b") == ["b"]


def test_add_slot_does_not_mutate_the_input_list():
    slots = ["a"]
    result = add_slot("b", slots)
    assert slots == ["a"]
    assert result == ["a", "b"]


### Tool call: edit_file
{"file_path": "workspace/tests/test_edge_cases.py", "new_string": "@pytest.mark.parametrize(\n    \"text\", [\"\", \"abc\", \"1h30\", \"1h30x\", \"1:2:3\", \"-5\", None, 45]\n)", "old_string": "@pytest.mark.parametrize(\"text\", [\"\", \"abc\", \"1h30\", \"1h30x\", \"1:2:3\", \"-5\", None, 45])"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/tests/test_edge_cases.py'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -3 && python - <<'PY'\nfrom bookings.billing import billable_blocks as b\nprint(b(2**53+1, 1), 2**53+1)\nprint([b(x) for x in (0,1,15,16,20,30,45,60,61)], b(16, block=10), b(16.5, block=10))\ntry: b(-1)\nexcept ValueError as e: print(\"ValueError:\", e)\nPY\npython -m pyflakes workspace 2>/dev/null || python -m flake8 --max-line-length=79 workspace 2>/dev/null || echo \"(no linter available)\""}

### Tool result
...................................                                      [100%]
35 passed in 0.02s
9007199254740993 9007199254740993
[0, 1, 1, 2, 2, 2, 3, 4, 5] 2 2.0
ValueError: minutes must be >= 0, got -1
(no linter available)

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && awk 'length > 79 {print FILENAME\":\"FNR\": \"length}' bookings/*.py tests/*.py; echo \"--- long lines checked ---\"; python -m pytest tests -q 2>&1 | tail -2"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool result
--- long lines checked ---
...................................                                      [100%]
35 passed in 0.02s

[Command succeeded with exit code 0]

### Tool result
@@ lines 1-41 of 41 @@
"""Time helpers for the bookings package."""
import re

_HOURS_MINUTES_RE = re.compile(r"(\d+)h(?:(\d+)m)?")
_MINUTES_RE = re.compile(r"(\d+)m")
_CLOCK_RE = re.compile(r"(\d+):(\d{1,2})")
_BARE_MINUTES_RE = re.compile(r"(\d+)")


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    if not isinstance(text, str):
        raise ValueError(f"bad duration: {text!r}")
    stripped = text.strip()

    m = _HOURS_MINUTES_RE.fullmatch(stripped)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2) or 0)

    m = _MINUTES_RE.fullmatch(stripped)
    if m:
        return int(m.group(1))

    m = _CLOCK_RE.fullmatch(stripped)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))

    m = _BARE_MINUTES_RE.fullmatch(stripped)
    if m:
        return int(m.group(1))

    raise ValueError(f"bad duration: {text!r}")

### Tool result
@@ lines 1-18 of 18 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=None):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    if slots is None:
        return [slot]
    return [*slots, slot]

### Assistant
All fixed and verified. Final state: **35 tests pass** (`3` pre-existing + `32` new edge-case tests), and an independent review agent confirmed every documented behaviour with adversarial probes.

## Summary of changes

**`workspace/bookings/timeutil.py`** — `parse_duration` only understood `"1h30m"` and raised `ValueError` for everything else, contradicting its docstring. Rewrote it with four module-level compiled patterns to cover all documented formats (`"2h"`, `"45m"`, `"1:30"`, bare `"45"` minutes), stripping surrounding whitespace and still raising `ValueError` for unsupported or non-string input.

**`workspace/bookings/billing.py`** — `billable_blocks` used `round()`, which does banker's rounding (`20/15 -> 1`) instead of always rounding up, and never rejected negative minutes. Now it raises `ValueError` for `minutes < 0` (and for a non-positive `block`) and rounds up with integer-safe arithmetic (`-(-minutes // block)`), avoiding the float-precision loss of `math.ceil(minutes / block)`.

**`workspace/bookings/schedule.py`** — `add_slot` had a mutable default argument (`slots=[]`) that was mutated and returned, so calls shared state. It now uses `slots=None` and returns a new list (`[*slots, slot]`), leaving the caller's list untouched.

**`workspace/tests/test_edge_cases.py`** (new; existing test files untouched) — parametrised tests for every documented duration format, rejection of bad input, round-up billing (including custom block sizes), and `add_slot` state isol
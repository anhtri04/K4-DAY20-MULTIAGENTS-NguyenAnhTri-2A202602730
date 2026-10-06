### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by reading the skill files that could apply to this task.

### Tool call: read_file
{"file_path": "/skills/bugfix-regression-changelog/SKILL.md", "limit": 1000}

### Tool call: read_file
{"file_path": "/skills/output-schema-and-normalization/SKILL.md", "limit": 1000}

### Tool result
@@ lines 1-13 of 13 @@
---
name: bugfix-regression-changelog
description: Use when a task asks you to fix bugs in code and record or verify the changes.
---
- For each distinct bug fixed, add a focused regression test that would fail on the old behavior and pass on the new behavior.
- Put regression tests in the required location or module and follow the project's existing test conventions.
- Run the full test suite from the project root, not just the new tests.
- Record every fix in the changelog file under the required heading.
- Use the required bullet format exactly, such as `type(scope): short description`.
- Keep one bullet per fix and ensure the required minimum number of entries exists.
- Verify the changelog heading is present and the entries render correctly.
- Do not replace regression coverage with tests that only assert the new behavior without covering the original bug.
- Final check: required test file exists, full suite passes, and changelog contains every fix.

### Tool result
@@ lines 1-13 of 13 @@
---
name: output-schema-and-normalization
description: Use when producing structured output such as JSON, CSV, or logs that must follow explicit naming, sorting, or schema conventions.
---
- Read the output contract for every field: case, separators, canonical values, units, timestamp format, and null handling.
- Normalize identifiers exactly as specified, including case conversion, separator replacement, and whitespace trimming.
- Apply the specified sort order completely; when multiple keys are required, sort by them in the stated order.
- Include every required top-level metadata, version, or generator field, even if it seems redundant.
- Validate the final artifact against the spec: parse it, check keys, types, allowed values, sort order, and row counts.
- Do not rely on input order or default library sorting; make the required order explicit in code.
- If the spec provides an example, match its structure and normalization exactly.
- Re-open the final file after writing and inspect the metadata block, first record, and last record.
- Keep temporary generation scripts out of the final deliverable workspace unless the task requires them.

### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/bookings"}

### Tool call: ls
{"path": "/workspace/tests"}

### Tool call: read_file
{"file_path": "/workspace/README.md"}

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

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

### Tool call: read_file
{"file_path": "/workspace/bookings/__init__.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "/workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

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
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

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
{"command": "cd /workspace && python -m pytest tests -q 2>&1 | tail -40"}

### Tool call: ls
{"path": "/"}

### Tool result
[stderr] /bin/sh: line 1: cd: /workspace: No such file or directory

Exit code: 1
[Command failed with exit code 1]

### Tool result
['/skills/', '/workspace/']

### Tool call: execute
{"command": "pwd && ls && cd workspace && python -m pytest tests -q 2>&1 | tail -40"}

### Tool result
/tmp/lab-sandbox-ebjga4jw
skills
workspace
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

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
FAILED tests/test_bookings.py::test_t

### Tool call: execute
{"command": "cd workspace && ls -la && ls -la tests bookings && python -c \"import sys; print(sys.version)\""}

### Tool call: glob
{"pattern": "**/*", "path": "/tmp/lab-sandbox-ebjga4jw"}

### Tool result
total 8
drwxr-xr-x 5 anhtri04 anhtri04 140 Oct  6 16:28 .
drwx------ 4 anhtri04 anhtri04  80 Oct  6 16:28 ..
drwxr-xr-x 3 anhtri04 anhtri04 120 Oct  6 16:28 .pytest_cache
-rw-r--r-- 1 anhtri04 anhtri04  54 Oct  6 13:41 CHANGELOG.md
-rw-r--r-- 1 anhtri04 anhtri04 118 Oct  6 13:41 README.md
drwxr-xr-x 3 anhtri04 anhtri04 160 Oct  6 13:44 bookings
drwxr-xr-x 3 anhtri04 anhtri04  80 Oct  6 13:44 tests
bookings:
total 20
drwxr-xr-x 3 anhtri04 anhtri04 160 Oct  6 13:44 .
drwxr-xr-x 5 anhtri04 anhtri04 140 Oct  6 16:28 ..
-rw-r--r-- 1 anhtri04 anhtri04  22 Oct  6 13:41 __init__.py
drwxr-xr-x 2 anhtri04 anhtri04 140 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04 333 Oct  6 13:41 billing.py
-rw-r--r-- 1 anhtri04 anhtri04 211 Oct  6 13:41 calendar_export.py
-rw-r--r-- 1 anhtri04 anhtri04 467 Oct  6 13:41 schedule.py
-rw-r--r-- 1 anhtri04 anhtri04 513 Oct  6 13:41 timeutil.py

tests:
total 4
drwxr-xr-x 3 anhtri04 anhtri04  80 Oct  6 13:44 .
drwxr-xr-x 5 anhtri04 anhtri04 140 Oct  6 16:28 ..
drwxr-xr-x 2 anhtri04 anhtri04  60 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04 371 Oct  6 13:41 test_bookings.py
3.14.7 (main, Aug 10 2026, 07:46:56) [GCC 16.1.1 20260728]

[Command succeeded with exit code 0]

### Tool result
No files found

### Assistant
Now let me look at the full test output and understand each function's contract:

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | head -30"}

### Tool result
FF.                                                                      [100%]
=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

~/ai20k/K4-DAY20-MULTIAGENTS-NguyenAnhTri-2A202602730/tasks/code-eval/workspace/tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.

[Command succeeded with exit code 0]

### Assistant
Three distinct bugs confirmed. Let me fix each source file.

### Tool call: write_file
{"file_path": "/workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n_HOURS_MINUTES_RE = re.compile(r\"(\\d+)h(\\d+)m\")\n_HOURS_RE = re.compile(r\"(\\d+)h\")\n_MINUTES_RE = re.compile(r\"(\\d+)m\")\n_CLOCK_RE = re.compile(r\"(\\d+):(\\d+)\")\n_BARE_MINUTES_RE = re.compile(r\"(\\d+)\")\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n\n    Raises:\n        ValueError: if `text` does not match any supported format.\n    \"\"\"\n    duration = text.strip()\n\n    match = _HOURS_MINUTES_RE.fullmatch(duration)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    match = _HOURS_RE.fullmatch(duration)\n    if match:\n        return int(match.group(1)) * 60\n\n    match = _MINUTES_RE.fullmatch(duration)\n    if match:\n        return int(match.group(1))\n\n    match = _CLOCK_RE.fullmatch(duration)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n\n    match = _BARE_MINUTES_RE.fullmatch(duration)\n    if match:\n        return int(match.group(1))\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool call: write_file
{"file_path": "/workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n\n    Raises:\n        ValueError: if `minutes` is negative.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(f\"minutes must be >= 0, got {minutes!r}\")\n    return math.ceil(minutes / block)\n"}

### Tool call: write_file
{"file_path": "/workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable, Sequence\n\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot: str, slots: Sequence[str] | None = None) -> list[str]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*(slots or []), slot]\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool result
Updated file /workspace/bookings/billing.py

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool call: edit_file
{"file_path": "/workspace/bookings/calendar_export.py", "old_string": "def slot_end(start_minute, duration_text):\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)", "new_string": "def slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/calendar_export.py'

### Assistant
Now the regression tests (new file, leaving `tests/test_bookings.py` untouched):

### Tool call: write_file
{"content": "\"\"\"Regression tests for the bugs fixed in the bookings package.\"\"\"\nimport pytest\n\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot\nfrom bookings.timeutil import parse_duration\n\n\ndef test_parse_duration_hours_only():\n    assert parse_duration(\"2h\") == 120\n\n\ndef test_parse_duration_minutes_only():\n    assert parse_duration(\"45m\") == 45\n\n\ndef test_parse_duration_clock_format():\n    assert parse_duration(\"1:30\") == 90\n\n\ndef test_parse_duration_bare_number_is_minutes():\n    assert parse_duration(\"45\") == 45\n\n\ndef test_parse_duration_ignores_surrounding_whitespace():\n    assert parse_duration(\"  1h30m  \") == 90\n\n\ndef test_parse_duration_rejects_unknown_format():\n    with pytest.raises(ValueError):\n        parse_duration(\"soon\")\n\n\ndef test_billable_blocks_rounds_partial_block_up():\n    assert billable_blocks(16) == 2\n\n\ndef test_billable_blocks_leaves_exact_multiple_unchanged():\n    assert billable_blocks(30) == 2\n\n\ndef test_billable_blocks_rejects_negative_minutes():\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n\n\ndef test_add_slot_keeps_separate_calls_independent():\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n\n\ndef test_add_slot_does_not_mutate_the_given_slots():\n    slots = [\"a\"]\n    assert add_slot(\"b\", slots) == [\"a\", \"b\"]\n    assert slots == [\"a\"]\n", "file_path": "/workspace/tests/test_regressions.py

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5"}

### Tool result
..............                                                           [100%]
14 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Let me verify the regression tests actually fail against the old (buggy) code:

### Tool call: execute
{"command": "set -e; rm -rf /tmp/oldcheck; mkdir -p /tmp/oldcheck/bookings; cp -r workspace/bookings/*.py /tmp/oldcheck/bookings/; cp -r workspace/tests /tmp/oldcheck/tests; cd /tmp/oldcheck\ncat > bookings/timeutil.py <<'EOF'\n\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\"\"\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))\nEOF\ncat > bookings/billing.py <<'EOF'\n\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes, block=15):\n    return round(minutes / block)\nEOF\ncat > bookings/schedule.py <<'EOF'\n\"\"\"Schedule helpers.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations):\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot, slots=[]):\n    slots.append(slot)\n    return slots\nEOF\npython -m pytest tests/test_regressions.py -q 2>&1 | tail -12"}

### Tool result

tests/test_regressions.py:55: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressions.py::test_parse_duration_hours_only - ValueError...
FAILED tests/test_regressions.py::test_parse_duration_minutes_only - ValueErr...
FAILED tests/test_regressions.py::test_parse_duration_clock_format - ValueErr...
FAILED tests/test_regressions.py::test_parse_duration_bare_number_is_minutes
FAILED tests/test_regressions.py::test_billable_blocks_rounds_partial_block_up
FAILED tests/test_regressions.py::test_billable_blocks_rejects_negative_minutes
FAILED tests/test_regressions.py::test_add_slot_keeps_separate_calls_independent
FAILED tests/test_regressions.py::test_add_slot_does_not_mutate_the_given_slots
8 failed, 3 passed in 0.03s

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "rm -rf /tmp/oldcheck && echo cleaned"}

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

### Tool result
cleaned

[Command succeeded with exit code 0]

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: edit_file
{"file_path": "/workspace/CHANGELOG.md", "old_string": "## Unreleased\n\n## 1.4.2", "new_string": "## Unreleased\n- fix(timeutil): parse \"2h\", \"45m\", \"1:30\" and bare-minute duration formats\n- fix(billing): always round billable blocks up and reject negative minutes\n- fix(schedule): stop add_slot from sharing and mutating its default slots list\n\n## 1.4.2"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -3 && python - <<'EOF'\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.calendar_export import slot_end\n\nfor text, expected in [(\"1h30m\", 90), (\"2h\", 120), (\"45m\", 45), (\"1:30\", 90), (\"45\", 45), (\" 1h \", 60), (\"0\", 0)]:\n    got = parse_duration(text)\n    assert got == expected, (text, got, expected)\nfor bad in [\"\", \"abc\", \"1h30\", \"1h30m45s\", \"h\", \"1:\"]:\n    try:\n        parse_duration(bad)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f\"no ValueError for {bad!r}\")\nassert billable_blocks(0) == 0 and billable_blocks(16) == 2 and billable_blocks(45) == 3\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError(\"negative minutes accepted\")\nassert add_slot(\"a\") == [\"a\"] and add_slot(\"b\") == [\"b\"]\nbase = [\"x\"]; assert add_slot(\"y\", base) == [\"x\", \"y\"] and base == [\"x\"]\nassert total_minutes([\"1h30m\", \"2h\", \"45\", \"1:30\"]) == 345\nassert slot_end(60, \"1h30m\") == 150\nprint(\"docstring behaviour OK\")\nEOF\nls -la . bookings tests"}

### Tool result
..............                                                           [100%]
14 passed in 0.01s
docstring behaviour OK
.:
total 8
drwxr-xr-x 5 anhtri04 anhtri04 140 Oct  6 16:28 .
drwx------ 4 anhtri04 anhtri04  80 Oct  6 16:28 ..
drwxr-xr-x 3 anhtri04 anhtri04 120 Oct  6 16:28 .pytest_cache
-rw-r--r-- 1 anhtri04 anhtri04 286 Oct  6 16:29 CHANGELOG.md
-rw-r--r-- 1 anhtri04 anhtri04 118 Oct  6 13:41 README.md
drwxr-xr-x 3 anhtri04 anhtri04 160 Oct  6 13:44 bookings
drwxr-xr-x 3 anhtri04 anhtri04 100 Oct  6 16:28 tests

bookings:
total 20
drwxr-xr-x 3 anhtri04 anhtri04  160 Oct  6 13:44 .
drwxr-xr-x 5 anhtri04 anhtri04  140 Oct  6 16:28 ..
-rw-r--r-- 1 anhtri04 anhtri04   22 Oct  6 13:41 __init__.py
drwxr-xr-x 2 anhtri04 anhtri04  140 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04  514 Oct  6 16:28 billing.py
-rw-r--r-- 1 anhtri04 anhtri04  228 Oct  6 16:28 calendar_export.py
-rw-r--r-- 1 anhtri04 anhtri04  575 Oct  6 16:28 schedule.py
-rw-r--r-- 1 anhtri04 anhtri04 1248 Oct  6 16:28 timeutil.py

tests:
total 8
drwxr-xr-x 3 anhtri04 anhtri04  100 Oct  6 16:28 .
drwxr-xr-x 5 anhtri04 anhtri04  140 Oct  6 16:28 ..
drwxr-xr-x 2 anhtri04 anhtri04   60 Oct  6 13:44 __pycache__
-rw-r--r-- 1 anhtri04 anhtri04  371 Oct  6 13:41 test_bookings.py
-rw-r--r-- 1 anhtri04 anhtri04 1343 Oct  6 16:28 test_regressions.py

[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

### Tool result
@@ lines 1-9 of 9 @@
# Changelog

## Unreleased
- fix(timeutil): parse "2h", "45m", "1:30" and bare-minute duration formats
- fix(billing): always round billable blocks up and reject negative minutes
- fix(schedule): stop add_slot from sharing and mutating its default slots list

## 1.4.2
- initial import

### Assistant
All 14 tests pass (the 3 visible ones plus 11 new regression tests), and the docstring contracts are verified end-to-end.

**Bugs fixed**

1. `bookings/timeutil.py` — `parse_duration` only matched `"1h30m"`, so `"2h"`, `"45m"`, `"1:30"` and bare `"45"` all raised `ValueError`. It now full-matches each documented format in turn (hours+minutes, hours, minutes, clock, bare minutes) and raises `ValueError` for anything else; whitespace is still stripped.
2. `bookings/billing.py` — `billable_blocks` used `round()` (which even rounded down and used banker's rounding), so a partial block wasn't billed as a full block. It now always rounds up with `math.ceil`, and rejects negative `minutes` with `ValueError` as the docstring requires.
3. `bookings/schedule.py` — `add_slot(slot, slots=[])` used a mutable default argument: it mutated the caller's list and leaked state between calls (`add_slot("a")` then `add_slot("b")` returned `["a","b"]`). The default is now `None` and the function builds and returns a new list without touching the input.

Also added consistent type hints (`parse_duration`, `billable_blocks`, `total_minutes`, `add_slot`, `slot_end` in `bookings/calendar_export.py`) and `Raises:` notes, following the package's existing docstring style.

**Files changed**

- `workspace/bookings/timeutil.py`
- `workspace/bookings/billing.py`
- `workspace/bookings/schedule.py`
- `workspace/bookings/calendar_export.py` (type hints only, behaviour unchanged)
- `workspace/tests/test_regress
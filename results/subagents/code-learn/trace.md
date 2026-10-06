### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by exploring the workspace to understand the structure.

### Tool call: ls
{"path": "workspace"}

### Tool call: glob
{"pattern": "workspace/**/*.py"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py', '/workspace/tests/test_report.py']

### Tool call: read_file
{"file_path": "workspace/inventory/__init__.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/export.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py"}

### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md"}

### Tool result
@@ lines 1-1 @@
System reminder: File exists but has empty contents

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 0.3.1
- initial import

### Tool call: ls
{"path": "/"}

### Tool call: glob
{"pattern": "workspace/**/*"}

### Tool result
['/workspace/']

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/__init__.cpython-314.pyc', '/workspace/inventory/__pycache__/export.cpython-314.pyc', '/workspace/inventory/__pycache__/pricing.cpython-314.pyc', '/workspace/inventory/__pycache__/report.cpython-314.pyc', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py', '/workspace/tests/__pycache__/test_report.cpython-314-pytest-9.1.1.pyc', '/workspace/tests/test_report.py']

### Tool call: execute
{"command": "ls -la /workspace/ /workspace/inventory/ /workspace/tests/ && python -V && python -m pytest --version"}

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -30"}

### Tool result
[stderr] ls: cannot access '/workspace/': No such file or directory
[stderr] ls: cannot access '/workspace/inventory/': No such file or directory
[stderr] ls: cannot access '/workspace/tests/': No such file or directory

Exit code: 2
[Command failed with exit code 2]

### Tool result

    def parse_price(text):
        """Convert a price string to a Decimal.
    
        Supported formats:
          "$1,299.50" -> Decimal("1299.50")
          "  12 "     -> Decimal("12")
          "1299.5"    -> Decimal("1299.5")
          "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
        """
        cleaned = text.strip().replace("$", "")
>       return Decimal(cleaned)
               ^^^^^^^^^^^^^^^^
E       decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

inventory/pricing.py:15: InvalidOperation
________________________ test_discount_rounding_half_up ________________________

    def test_discount_rounding_half_up():
>       assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")
E       AssertionError: assert Decimal('9.04') == Decimal('9.05')
E        +  where Decimal('9.04') = apply_discount(Decimal('10.05'), 10)
E        +    where Decimal('10.05') = Decimal('10.05')
E        +  and   Decimal('9.05') = Decimal('9.05')

~/ai20k/K4-DAY20-MULTIAGENTS-NguyenAnhTri-2A202602730/tasks/code-learn/workspace/tests/test_report.py:19: AssertionError
=========================== short test summary info ============================
FAILED tests/test_report.py::test_total_value_thousands_separator - decimal.I...
FAILED tests/test_report.py::test_discount_rounding_half_up - AssertionError:...
2 failed, 4 passed in 0.02s

[Command succeeded with exit code 0]

### Tool call: glob
{"pattern": "*.md"}

### Tool call: glob
{"pattern": "*.{cfg,toml,ini,yaml,yml,txt,json}"}

### Tool call: execute
{"command": "pwd; ls -a; ls -a .."}

### Tool result
['/workspace/.pytest_cache/README.md', '/workspace/CHANGELOG.md', '/workspace/README.md']

### Tool result
No files found

### Tool result
/tmp/lab-sandbox-f73apic3
.
..
workspace
.
..
.9adbdebfefe5ff9f-00000000.so
.9adbdff9f2e4ffd7-00000000.so
.9adbe8bbfffbedb7-00000000.so
.ICE-unix
.X0-lock
.X11-unix
.XIM-unix
.bcdbdf5ef4f5f62e-00000001.so
.bcdbdf9ebebdfa2f-00000001.so
.bcdbe5beb587b77d-00000001.so
.font-unix
checkup-db-1000
gitkraken
hsperfdata_anhtri04
lab-sandbox-f73apic3
mcp-i6vNlU
node-compile-cache
opencode
org.chromium.Chromium.fIeeVg
pyright-16855-QByXOGx6hfbl
pytest-of-anhtri04
python-languageserver-cancellation
sddm-auth-19a954bb-8303-4bfe-aea0-6d063f4ca801
systemd-private-91f4e9032b3746a08c87e75767042d40-NetworkManager.service-orULnX
systemd-private-91f4e9032b3746a08c87e75767042d40-bluetooth.service-6xIkOb
systemd-private-91f4e9032b3746a08c87e75767042d40-intel_lpmd.service-PV4UL0
systemd-private-91f4e9032b3746a08c87e75767042d40-polkit.service-snSLS2
systemd-private-91f4e9032b3746a08c87e75767042d40-power-profiles-daemon.service-h4xCYF
systemd-private-91f4e9032b3746a08c87e75767042d40-systemd-logind.service-hhQYwV
systemd-private-91f4e9032b3746a08c87e75767042d40-upower.service-eEvHin
tmux-1000
vscode-ah-b80ec397cceb

[Command succeeded with exit code 0]

### Assistant
No conventions file exists in the sandbox, so I'll follow standard idiomatic conventions. Now let me fix the three modules.

### Tool call: write_file
{"file_path": "workspace/inventory/pricing.py", "content": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import ROUND_HALF_UP, Decimal\n\nCENTS = Decimal(\"0.01\")\n\n\ndef parse_price(text: str) -> Decimal:\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    negative = cleaned.startswith(\"(\") and cleaned.endswith(\")\")\n    if negative:\n        cleaned = cleaned[1:-1].strip()\n    value = Decimal(cleaned)\n    return -value if negative else value\n\n\ndef apply_discount(price: Decimal, percent: Decimal) -> Decimal:\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)\n"}

### Tool call: write_file
{"file_path": "workspace/inventory/export.py", "content": "\"\"\"Export helpers.\"\"\"\nfrom collections.abc import Mapping\nfrom typing import Any\n\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item: Mapping[str, Any]) -> str:\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    price = parse_price(item[\"price\"])\n    qty = item[\"qty\"]\n    return f\"{name},{price:.2f},{qty}\"\n"}

### Tool call: write_file
{"file_path": "workspace/inventory/report.py", "content": "\"\"\"Inventory reports.\"\"\"\nfrom collections.abc import Iterable, Mapping\nfrom decimal import Decimal\nfrom typing import Any\n\nfrom .pricing import apply_discount, parse_price\n\n\ndef total_value(items: Iterable[Mapping[str, Any]]) -> Decimal:\n    \"\"\"Total value of `items` after per-item discounts.\n\n    Each item is a dict: {\"name\": str, \"price\": str, \"qty\": int, \"discount\": percent (optional)}.\n    \"\"\"\n    total = Decimal(\"0\")\n    for item in items:\n        price = parse_price(item[\"price\"])\n        price = apply_discount(price, item.get(\"discount\", 0))\n        total += price * item[\"qty\"]\n    return total\n\n\ndef low_stock(items: Iterable[Mapping[str, Any]], threshold: int = 5) -> list[str]:\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=str.casefold)\n"}

### Tool result
Updated file /workspace/inventory/pricing.py

### Tool result
Updated file /workspace/inventory/export.py

### Tool result
Updated file /workspace/inventory/report.py

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "old_string": "def apply_discount(price: Decimal, percent: Decimal) -> Decimal:", "new_string": "def apply_discount(price: Decimal, percent: int | Decimal) -> Decimal:"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5"}

### Tool call: execute
{"command": "cd workspace && python - <<'EOF'\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.export import to_csv_row\nfrom inventory.report import low_stock, total_value\n\nprint(parse_price(\"$1,299.50\"), parse_price(\"  12 \"), parse_price(\"1299.5\"), parse_price(\"(12.00)\"))\nprint(parse_price(\"($1,299.50)\"), parse_price(\"( 12.00 )\"))\nprint(apply_discount(Decimal(\"10.05\"), 10), apply_discount(Decimal(\"10.04\"), 10), apply_discount(Decimal(\"100.00\"), 15), apply_discount(Decimal(\"10.00\"), 0))\nprint(low_stock([{\"name\":\"pen\",\"qty\":2},{\"name\":\"ink\",\"qty\":9},{\"name\":\"Zeta\",\"qty\":0},{\"name\":\"apple\",\"qty\":1}]))\nprint(low_stock([{\"name\":\"pen\",\"qty\":5},{\"name\":\"ink\",\"qty\":4}]))\nprint(low_stock([{\"name\":\"a\",\"qty\":1}], threshold=0))\nprint(repr(to_csv_row({\"name\":\"pen\",\"price\":\"2.5\",\"qty\":4})))\nprint(repr(to_csv_row({\"name\":'a,b',\"price\":\"2.5\",\"qty\":4})))\nprint(repr(to_csv_row({\"name\":'say \"hi\"',\"price\":\"$1,299.50\",\"qty\":4})))\nprint(total_value([{\"name\":\"laptop\",\"price\":\"$1,299.50\",\"qty\":2},{\"name\":\"x\",\"price\":\"(12.00)\",\"qty\":1}]))\nEOF"}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Tool result
1299.50 12 1299.5 -12.00
-1299.50 -12.00
9.05 9.04 85.00 10.00
['apple', 'pen', 'Zeta']
['ink']
[]
'pen,2.50,4'
'"a,b",2.50,4'
'"say ""hi""",1299.50,4'
2587.00

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n\n## 0.3.1", "new_string": "## Unreleased\n- `parse_price`: support thousands separators and accounting-style negative prices.\n- `apply_discount`: round half up to 2 decimals instead of banker's rounding.\n- `low_stock`: keep only quantities strictly below the threshold and sort names case-insensitively.\n- `to_csv_row`: quote names containing a comma or a double quote (RFC 4180).\n\n## 0.3.1"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Assistant
Now let me have an independent reviewer verify the result against the docstring spec and conventions.

### Tool call: task
{"description": "Independently review a bug fix in the `inventory` package under the sandbox folder `workspace/` (all paths are relative to the sandbox root; the shell starts in the sandbox root). Do NOT modify any file; this is a verification-only task. Read files with the read_file tool and run code with the execute tool (e.g. `cd workspace && python -m pytest tests -q`).\n\nContext / requirements:\n- The package is `workspace/inventory/` with modules `__init__.py` (empty), `pricing.py`, `report.py`, `export.py`. Tests live in `workspace/tests/test_report.py` and MUST NOT be modified.\n- The docstrings are the specification; every public function must do exactly what its docstring says.\n- Fixes that were just applied (verify each is correct and complete):\n  1. `pricing.parse_price`: must handle \"$1,299.50\" -> Decimal(\"1299.50\"), \"  12 \" -> Decimal(\"12\"), \"1299.5\" -> Decimal(\"1299.5\"), \"(12.00)\" -> Decimal(\"-12.00\") (accounting parentheses = negative).\n  2. `pricing.apply_discount`: Decimal result rounded to 2 dp with ROUND_HALF_UP (0.005 -> 0.01), e.g. apply_discount(Decimal(\"10.05\"), 10) == Decimal(\"9.05\").\n  3. `report.total_value`: total value of items after per-item discounts; item = {\"name\": str, \"price\": str, \"qty\": int, \"discount\": optional percent}.\n  4. `report.low_stock`: names of items whose qty is STRICTLY BELOW threshold (default 5), names sorted alphabetically ignoring case.\n  5. `export.to_csv_row`: \"name,price,qty\" with pr

### Tool result
## Verdict: PASS — all 5 required fixes verified correct and complete; no defect reproducible against the docstrings/spec. (A few out-of-spec notes below.)

### Commands run and results

| # | Command | Result |
|---|---|---|
| 1 | `cd workspace && python -m pytest tests -q` | `...... [100%] 6 passed in 0.01s`, EXIT=0 |
| 2 | `cd workspace; PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -v -p no:cacheprovider` | 6/6 PASSED (all 6 tests in `tests/test_report.py`), rootdir `workspace`, Python 3.14.7 / pytest 9.1.1. Tests imported the local sources (`inventory.pricing.__file__` → `…/workspace/inventory/pricing.py`), not an installed copy. |
| 3 | `cd workspace && python - <<'PY' … PY` heredoc edge-case matrix | results below |
| 4 | `cd workspace; python - <<'PY' … PY` heredoc 20,000-case property test vs. an exact `fractions.Fraction` half-away-from-zero reference | `apply_discount property mismatches: 0` |
| 5 | source/token inspection (AST + raw bytes) | line lengths, annotations, imports, whitespace |

### Requirement-by-requirement verification (all executed, not read-only)

1. **`parse_price`** — `"$1,299.50"→1299.50`, `"  12 "→12`, `"1299.5"→1299.5`, `"(12.00)"→-12.00`, plus `"  (12.00)  "`, `"($1,299.50)"`, `"$(1,299.50)"`, `"$0.00"`, `"$ 12.00"`, `"-12.00"`, `"1,234,567.89"`: **all OK**.
2. **`apply_discount`** — `10.05,10 → 9.05` ✔; `0.005→0.01`, `-0.005→-0.01`, `1.005→1.01`, `2.675→2.68`, `100,0→100.00`, `100,100→0.00`, `percent` as `Decimal("10")` ✔; 20k randomized

### Assistant
The reviewer found no spec violations. Let me verify the bytecode cache was refreshed by my test runs (so no stale pre-fix bytecode lingers) and do a final confirmation run.

### Tool call: execute
{"command": "cd workspace && ls -l --time-style=+%H:%M:%S inventory/*.py inventory/__pycache__/*.pyc && python -m pytest tests -q 2>&1 | tail -3"}

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool result
-rw-r--r-- 1 anhtri04 anhtri04    0 13:41:38 inventory/__init__.py
-rw-r--r-- 1 anhtri04 anhtri04  214 13:44:03 inventory/__pycache__/__init__.cpython-314.pyc
-rw-r--r-- 1 anhtri04 anhtri04  761 13:44:03 inventory/__pycache__/export.cpython-314.pyc
-rw-r--r-- 1 anhtri04 anhtri04 1261 13:44:03 inventory/__pycache__/pricing.cpython-314.pyc
-rw-r--r-- 1 anhtri04 anhtri04 1329 13:44:03 inventory/__pycache__/report.cpython-314.pyc
-rw-r--r-- 1 anhtri04 anhtri04  601 15:53:11 inventory/export.py
-rw-r--r-- 1 anhtri04 anhtri04 1049 15:53:14 inventory/pricing.py
-rw-r--r-- 1 anhtri04 anhtri04  947 15:53:11 inventory/report.py
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Tool result
@@ lines 1-31 of 31 @@
"""Price utilities for the inventory package."""
from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")


def parse_price(text: str) -> Decimal:
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "").replace(",", "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1].strip()
    value = Decimal(cleaned)
    return -value if negative else value


def apply_discount(price: Decimal, percent: int | Decimal) -> Decimal:
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)

### Assistant
The stale `.pyc` files (13:44, pre-fix) were never refreshed. Python still invalidates them by source mtime, but I'll remove these generated caches to eliminate any stale-code confusion.

### Tool call: delete
{"file_path": "workspace/inventory/__pycache__"}

### Tool call: delete
{"file_path": "workspace/tests/__pycache__"}

### Tool result
Deleted /workspace/inventory/__pycache__

### Tool result
Deleted /workspace/tests/__pycache__

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -3 && python - <<'EOF'\nfrom decimal import Decimal\nfrom inventory import pricing, report, export\nprint(pricing.__file__, report.__file__, export.__file__)\nEOF"}

### Tool result
......                                                                   [100%]
6 passed in 0.01s
/tmp/lab-sandbox-f73apic3/workspace/inventory/pricing.py /tmp/lab-sandbox-f73apic3/workspace/inventory/report.py /tmp/lab-sandbox-f73apic3/workspace/inventory/export.py

[Command succeeded with exit code 0]

### Assistant
Done. Test suite: **6 passed**.

## What I changed and why

**`workspace/inventory/pricing.py`**
- `parse_price`: now strips `$` **and** thousands separators, and handles the accounting style `(12.00)` → `Decimal("-12.00")` (parentheses negate, inner whitespace tolerated). Previously `"$1,299.50"` raised `decimal.InvalidOperation` and parentheses were ignored.
- `apply_discount`: `quantize(..., rounding=ROUND_HALF_UP)` instead of the default banker's rounding, so `apply_discount(Decimal("10.05"), 10)` is `9.05` (was `9.04`), as the docstring's "round half up" rule requires.

**`workspace/inventory/report.py`**
- `low_stock`: comparison changed from `<=` to strict `<` (docstring says "strictly below"), and the names are now `sorted(..., key=str.casefold)` so the result is alphabetical ignoring case (was unsorted input order).

**`workspace/inventory/export.py`**
- `to_csv_row`: names containing a comma or a double quote are now wrapped in double quotes with inner quotes doubled (RFC 4180), e.g. `a,b` → `"a,b"`, `say "hi"` → `"say ""hi"""`.

**`workspace/CHANGELOG.md`**
- Added the four fixes under `## Unreleased`.

Also added type annotations / explicit imports and removed the generated `__pycache__` folders (they held stale pre-fix bytecode). No files under `tests/` were touched.

Verification: an independent reviewer re-ran the suite plus ~20k randomized property cases against an exact half-up reference and found no docstring or spec violations; the only notes were out-of-sc
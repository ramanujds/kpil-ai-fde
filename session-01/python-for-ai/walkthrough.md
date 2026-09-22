# Walkthrough: Ticket Triage Toolkit

**Day 1 | Block 3: Python for AI | Lab 2: Environment Setup**

> Goal: build a small, working Python toolkit two ways -- without uv, then with uv -- and
> feel the difference. About 20 to 25 minutes.

This walkthrough assumes you have already completed the base setup in
`session-01/notes/02-setting-up-our-env.md` (Python 3.10+, uv, VS Code, Git). If `uv --version`
does not work yet, do that first.

Solutions exist on a separate `solutions` branch. Do not check it out until you have tried
each `TODO` yourself -- struggling for a minute or two is where the learning happens.

---

## Part A: Without uv

1. Open a terminal in `exercise/without-uv/`.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. Install the one dependency:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example env file and keep the default:

   ```bash
   cp .env.example .env             # Windows: copy .env.example .env
   ```

5. Try running the script now, before filling in any `TODO`:

   ```bash
   python ticket_toolkit.py
   ```

   It will error or print `None` -- expected, since every function currently ends in
   `pass`. That is your starting point.

Notice what you just did: created an environment, activated it, installed from a
lockfile-less `requirements.txt`, and now have to remember to `deactivate` when you are
done. Keep that count of steps in mind for Part B.

---

## Part B: With uv

1. Open a **second terminal** in `exercise/with-uv/` (leave Part A's terminal as it is,
   for comparison).
2. Sync the project's one dependency. uv reads `pyproject.toml`, creates `.venv`
   automatically, and installs into it:

   ```bash
   uv sync
   ```

3. Copy the example env file:

   ```bash
   cp .env.example .env             # Windows: copy .env.example .env
   ```

4. Run the script directly -- no activation step:

   ```bash
   uv run ticket_toolkit.py
   ```

Same starting error as Part A (the `TODO`s are not filled in yet), but notice there was no
`activate` / `deactivate` pair to remember, and `uv sync` would also be exactly what a
teammate runs after `git clone` to reproduce your environment.

---

## Part C: Fill In the TODOs

The code is identical in both folders, so make your changes in **one** folder first (pick
either), get it working, then copy `ticket_toolkit.py` over to the other so both run
end to end.

### 1. `load_tickets` -- file handling and exceptions

Read the file, and make sure a missing or broken file does not crash the program:

```python
def load_tickets(path: Path) -> list[dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Could not find {path}")
        return []
    except json.JSONDecodeError:
        print(f"{path} is not valid JSON")
        return []
```

**Why it matters:** every real integration you build from Day 3 onward reads *something*
external -- a file, an API response. The file is not always there and the JSON is not
always valid. Handling that here is the same habit you will need for API errors later.

### 2. `filter_by_status` -- list comprehension

```python
def filter_by_status(tickets: list[dict], status: str) -> list[dict]:
    return [t for t in tickets if t["status"].lower() == status.lower()]
```

### 3. `count_by_priority` -- dict as a counter

```python
def count_by_priority(tickets: list[dict]) -> dict:
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for t in tickets:
        counts[t["priority"]] += 1
    return counts
```

### 4. `format_ticket_summary` -- f-strings

```python
def format_ticket_summary(ticket: dict) -> str:
    return (
        f"[{ticket['id']}] {ticket['priority'].upper()} - "
        f"{ticket['category']} @ {ticket['site']} "
        f"({ticket['days_open']} days open)"
    )
```

### 5. `top_priority_report` -- composing what you already wrote

```python
def top_priority_report(tickets: list[dict], limit: int = REPORT_LIMIT) -> list[str]:
    open_tickets = filter_by_status(tickets, "Open")
    ranked = sorted(open_tickets, key=lambda t: PRIORITY_ORDER[t["priority"]])
    return [format_ticket_summary(t) for t in ranked[:limit]]
```

**Why it matters:** notice this function does not know or care *how* filtering or
formatting work -- it just calls the other functions by name. That is exactly how an
agent will later call your `TOOLS` entries: by name, without knowing the internals.

---

## Part D: Run and Compare

In each folder, run the script the way that track expects:

```bash
# without-uv/ (venv still active)
python ticket_toolkit.py

# with-uv/
uv run ticket_toolkit.py
```

Both should print the same JSON list of the top 5 open, highest-priority tickets. Then
try changing `REPORT_LIMIT` in `.env` to `3` in both folders and re-run -- confirm the
output shrinks in both.

| | Without uv | With uv |
|---|---|---|
| Commands to get running | `venv` + `activate` + `pip install` | `uv sync` |
| Remember to activate/deactivate | Yes | No |
| Reproducible for a teammate | `requirements.txt` (no lockfile) | `uv.lock` (exact versions) |
| Run the script | `python ticket_toolkit.py` | `uv run ticket_toolkit.py` |

---

## Part E: Look at the TOOLS Registry

Open the bottom of `ticket_toolkit.py` and look at `TOOLS`. You are not calling anything
through it yet -- but try this in a Python shell (`python` or `uv run python`) from either
folder:

```python
from ticket_toolkit import TOOLS, load_tickets, TICKETS_FILE

tickets = load_tickets(TICKETS_FILE)
for name, (fn, description) in TOOLS.items():
    print(name, "-", description)

# Call one "tool" by name, the way an agent eventually will:
fn, _ = TOOLS["count_by_priority"]
print(fn(tickets))
```

That `TOOLS["count_by_priority"]` lookup-then-call is the mechanism underneath every
agent framework you will meet on Day 5. Nothing new to learn there -- just this same
dict, at a larger scale.

---

## If You Get Stuck

| Symptom | Likely fix |
|---|---|
| `ModuleNotFoundError: dotenv` | Re-run `pip install -r requirements.txt` (without-uv) or `uv sync` (with-uv) |
| `python ticket_toolkit.py` uses the wrong Python | Confirm `.venv` is activated (`which python`) |
| Script prints `None` everywhere | A `TODO` still ends in `pass` -- Python functions return `None` by default |
| `KeyError` on a ticket field | Check your f-string / dict keys match `tickets.json` exactly (case-sensitive) |
| Output does not shrink after editing `REPORT_LIMIT` | Confirm `.env` was copied from `.env.example` in that folder, not just edited in one |

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*

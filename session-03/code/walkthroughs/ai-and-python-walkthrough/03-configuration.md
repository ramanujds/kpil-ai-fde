# Step 3 — Configuration

> Back to index · Previous: Environment Setup · Next: Building the Request

## Goal

Create `config.py`, which reads the API address, key and model name from environment
variables, and `.env.example`, a template that shows which settings exist.

## Why this matters

Three values change between "Ollama on my laptop" and "OpenAI in the cloud": the base URL,
the API key and the model name. If those are typed into the calling code, switching
providers means editing code, and one careless commit can publish a key.

Reading them from **environment variables** fixes both problems. The code never contains a
secret, and changing providers means changing a `.env` file that Git ignores. The defaults in
`config.py` describe a local Ollama, so the project runs with **no `.env` at all** for the
common classroom case, and a real key is only ever needed for a hosted provider.

## 1. Imports

```python
import os

from dotenv import load_dotenv
```

`os` reads environment variables. `load_dotenv` reads a `.env` file into them.

## 2. Load the `.env` file

```python
# Reads a file named .env in this folder (if it exists) and puts each line
# into the environment. If there is no .env file, nothing happens.
load_dotenv()
```

If there is no `.env` file, this quietly does nothing. If a variable is already set in your
terminal, the terminal's value wins over the file's value.

## 3. Read the three settings

```python
# os.getenv(name, default): use the environment value, else the default.
# The defaults describe a local Ollama, so the examples work with no .env at all.
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3:8b")
```

`os.getenv(name, default)` returns the environment value, or the default when it is not set.

## 4. Add the docstring

Put the explanation at the top of the file. It is documentation, not logic:

```python
"""
Configuration: the three settings every LLM call needs.

  LLM_BASE_URL  where the API lives (your laptop for Ollama, a cloud address for OpenAI)
  LLM_API_KEY   the secret that proves who you are (Ollama ignores it, OpenAI requires it)
  LLM_MODEL     which model should answer

They come from environment variables, so the SAME code runs against Ollama
or OpenAI just by changing values in the .env file. No key is ever written
inside a .py file, so nothing secret can end up in Git.
"""
```

## 5. Create `.env.example`

```text
# Copy this file to .env and edit the copy. Never commit .env.
#
# The code talks to any "OpenAI-compatible" chat endpoint.
# Pick ONE of the two setups below.

# --- Option A: Ollama running on your own machine (free, no key needed) ---
# Install Ollama, then run once:  ollama pull llama3:8b
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3:8b

# --- Option B: OpenAI (needs a real key from your provider account) ---
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_API_KEY=paste-your-key-here
# LLM_MODEL=gpt-4o-mini
```

This is a **template**. You commit it so others can see which settings exist, and copy it to
`.env` (which Git ignores) only when they need to change something. Lines starting with `#`
are comments, so Option B is switched off until you remove the `#` characters.

## Try it

With no `.env` file, the defaults apply:

```bash
uv run python -c "import config; print(config.BASE_URL, config.MODEL)"
```

```text
http://localhost:11434/v1 llama3:8b
```

Override one setting for a single run (macOS or Linux):

```bash
LLM_MODEL=mistral uv run python -c "import config; print(config.MODEL)"
```

```text
mistral
```

On Windows PowerShell:

```powershell
$env:LLM_MODEL="mistral"; uv run python -c "import config; print(config.MODEL)"
```

Now try the file route. Copy the template, edit one value, and rerun the first command:

```bash
cp .env.example .env
```

On Windows PowerShell use `Copy-Item .env.example .env`. If your folder is a Git
repository, confirm Git will ignore it:

```bash
git check-ignore .env
```

Expect it to print `.env`.

## Checkpoint

<details>
<summary>Full <code>config.py</code></summary>

```python
"""
Configuration: the three settings every LLM call needs.

  LLM_BASE_URL  where the API lives (your laptop for Ollama, a cloud address for OpenAI)
  LLM_API_KEY   the secret that proves who you are (Ollama ignores it, OpenAI requires it)
  LLM_MODEL     which model should answer

They come from environment variables, so the SAME code runs against Ollama
or OpenAI just by changing values in the .env file. No key is ever written
inside a .py file, so nothing secret can end up in Git.
"""

import os

from dotenv import load_dotenv

# Reads a file named .env in this folder (if it exists) and puts each line
# into the environment. If there is no .env file, nothing happens.
load_dotenv()

# os.getenv(name, default): use the environment value, else the default.
# The defaults describe a local Ollama, so the examples work with no .env at all.
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3:8b")
```

</details>

<details>
<summary>Full <code>.env.example</code></summary>

```text
# Copy this file to .env and edit the copy. Never commit .env.
#
# The code talks to any "OpenAI-compatible" chat endpoint.
# Pick ONE of the two setups below.

# --- Option A: Ollama running on your own machine (free, no key needed) ---
# Install Ollama, then run once:  ollama pull llama3:8b
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3:8b

# --- Option B: OpenAI (needs a real key from your provider account) ---
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_API_KEY=paste-your-key-here
# LLM_MODEL=gpt-4o-mini
```

</details>

This matches the reference project's `config.py` and `.env.example` exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'dotenv'` | Ran plain `python` instead of `uv run python`, or skipped `uv sync` | Use `uv run python ...` from the project folder |
| Edits to `.env` have no effect | The `.env` file is not next to `config.py`, or the same variable is already set in your terminal | Keep `.env` in the project folder, and remember a terminal variable overrides the file |
| Settings look right but the key still fails later | A trailing space or quotes copied into the `.env` value | Write `LLM_API_KEY=abc123` with nothing extra |
| `git check-ignore .env` prints nothing | `.gitignore` is missing the `.env` line | Add it back before putting any real key in `.env` |

Next: **Step 4 — Building the Request**.

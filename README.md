# House of Servicing — Service Portal

A Streamlit marketplace that turns the Servicing team's scattered Excel/VBA
macros into a centralized catalog of Python services. Each service has its
own page inside the portal that explains what it does, exposes a
**file-in → process → file-out** flow, and tracks usage.

---

## Table of contents
1. [Why this portal](#why-this-portal)
2. [Quick start](#quick-start)
3. [Project structure](#project-structure)
4. [How the app is organized](#how-the-app-is-organized)
5. [Use-case framework](#use-case-framework)
6. [Service catalog schema](#service-catalog-schema)
7. [Tutorial — add a new use case end to end](#tutorial--add-a-new-use-case-end-to-end)
8. [Configuration & theming](#configuration--theming)
9. [Deployment notes (Domino, proxies)](#deployment-notes-domino-proxies)
10. [Runtime data files](#runtime-data-files)

---

## Why this portal
The team maintains many `.xlsm` macros that:
- live on individual workstations,
- are duplicated and forked over email,
- lack visibility (nobody knows who owns what, or how much time it saves).

The portal solves three problems:
- **Centralize** all tools behind a single URL.
- **Industrialize** each macro into a versioned Python service.
- **Measure** usage (open counter per service + dashboard).

Each service exposes a **dedicated page** describing:
- 🎯 What it does (purpose)
- 📥 Input(s) it expects
- 📤 Output(s) it produces
- 💎 Value & benefits
- 🚀 A live runner: upload a file → run → download the result

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Open the URL printed by Streamlit (default `http://localhost:8501`).

The home page shows the marketplace. Click any tile → you land on the
service's dedicated page. Scroll to **🚀 Run this service**, optionally
download a sample input, upload a file and click **▶︎ Run processing**.

---

## Project structure

```
HouseofServicing/
├── app.py                          # Streamlit entry point (UI + routing)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore
├── .streamlit/
│   └── config.toml                 # Theme (also forced in CSS for hosts that ignore it)
├── data/
│   ├── services.json               # Service catalog metadata (committed)
│   └── counts.json                 # Per-service open counts (runtime, persistent — see Deployment)
├── samples/                        # Sample input files, one per use case
│   ├── iso_addresses_sample.csv
│   ├── self_care_triage_sample.csv
│   ├── authority_letter_sample.csv
│   ├── mt103_sample.txt
│   └── pain001_sample.xml
└── use_cases/                      # ⭐ One folder per use case
    ├── __init__.py
    ├── registry.py                 # service_id → processor module mapping
    ├── iso_addresses/
    │   ├── __init__.py
    │   └── processor.py
    ├── self_care_triage/
    │   ├── __init__.py
    │   └── processor.py
    ├── authority_letter/
    │   ├── __init__.py
    │   └── processor.py
    └── mt103_proof_of_payment/
        ├── __init__.py
        └── processor.py
```

---

## How the app is organized

**`app.py`** is split into focused functions:

| Function | Role |
|---|---|
| `inject_styles()` | All CSS, including the forced dark theme. |
| `load_services()` / `load_counts()` | Persistence helpers for the JSON files in `data/`. |
| `open_service(id)` / `go_back()` | Internal navigation — uses `st.query_params["service"]` to route within the portal. |
| `render_card(service, counts)` | The marketplace tile (logo, status, counter, "Open service" button). |
| `page_marketplace(services)` | Home view: hero, intro, metrics, search & filters, grid of cards. |
| `page_service_detail(service)` | Per-service page: hero, What it does / Inputs / Outputs / Value, runner. |
| `_render_run_section(service)` | The upload → process → download block. Looks up the processor via the registry. |
| `page_dashboard(services)` | Catalog KPIs and charts (incl. most-opened services). |
| `page_about()` | About page. |
| `main()` | Sidebar nav + router. If `?service=<id>` is set and we're on Marketplace, render the detail page; otherwise render the selected page. |

The dark theme is **injected via CSS** so it works even when the host
ignores `.streamlit/config.toml` (e.g. Domino).

---

## Use-case framework

Everything specific to one tool lives in `use_cases/<your_uc>/`. The app
only knows the **processor interface** — no other coupling.

### Processor contract
Each `use_cases/<your_uc>/processor.py` must expose:

```python
INPUT_FORMATS      : list[str]    # accepted upload extensions, no dot
INPUT_DESCRIPTION  : str          # shown on the service page
OUTPUT_FILENAME    : str          # default download filename
OUTPUT_MIME        : str          # MIME type for the download
OUTPUT_DESCRIPTION : str          # shown on the service page
SAMPLE_FILE        : str | None   # path (relative to project root) to a sample, or None

def process(file_bytes: bytes, filename: str) -> tuple[bytes, str, str]:
    """Return (output_bytes, output_filename, mime_type).

    Raise ValueError("...") with a clear message if the input is invalid;
    the message is shown to the user as a red error.
    """
```

### Registry
`use_cases/registry.py` maps each `service id` (from `data/services.json`)
to the processor module:

```python
from .iso_addresses import processor as iso_addresses
# ...

PROCESSORS = {
    "iso-addresses": iso_addresses,
    "self-care-triage": self_care_triage,
    "authority-letter": authority_letter,
    "mt103-proof-of-payment": mt103_proof_of_payment,
}
```

A service with no entry in the registry shows a "no processor connected
yet" message on its run section — useful for stubbing services before the
analyst has migrated the macro.

---

## Service catalog schema

`data/services.json` is a list of objects. Each object drives both the
tile in the marketplace and the dedicated service page.

```json
{
  "id": "iso-addresses",
  "name": "ISO-Structured Addresses",
  "category": "Data Management",
  "icon": "📮",
  "status": "live",
  "owner": "Data Team",
  "frequency": "Daily",
  "time_saved_h": 3,
  "tags": ["iso", "addresses", "normalization", "pilot"],
  "origin_macro": "ADRESSE_ISO.xlsm",
  "description": "Short tile description shown on the marketplace card.",
  "purpose": "Longer paragraph shown in the 'What it does' block.",
  "inputs":  ["Bullet 1", "Bullet 2"],
  "outputs": ["Bullet 1", "Bullet 2"],
  "benefits": ["Bullet 1", "Bullet 2"]
}
```

Field reference:

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable identifier. Used by the URL (`?service=<id>`), the registry and `counts.json`. |
| `name` | string | Display name. |
| `category` | string | Used for the colored accent and filters. Add the color in `CATEGORY_THEMES` (`app.py`) if it's new. |
| `icon` | string | Emoji or any short text shown as the logo. |
| `status` | `live` / `beta` / `dev` | `dev` disables the "Open service" button. |
| `owner` | string | Team responsible. |
| `frequency` | string | `Daily` / `Weekly` / `Monthly` / `Ad hoc`. |
| `time_saved_h` | number | Estimated hours saved per run. Aggregated in the dashboard. |
| `tags` | string[] | Free-text tags shown on the card and searchable. |
| `origin_macro` | string | Name of the original `.xlsm` file. |
| `description` | string | One-liner shown on the tile. |
| `purpose` | string | Paragraph shown in the "What it does" section. |
| `inputs` | string[] | Bullet list shown in the Input(s) section. |
| `outputs` | string[] | Bullet list shown in the Output(s) section. |
| `benefits` | string[] | Bullet list shown in the Value & benefits section. |

---

## Tutorial — add a new use case end to end

Goal: industrialize the `IBAN_CHECK.xlsm` macro into a portal service
called **IBAN Validator**.

### 1. Pick an id and create the folder

Use a short snake-case id; it will appear in the URL and in JSON.

```bash
mkdir -p use_cases/iban_validator samples
touch use_cases/iban_validator/__init__.py
```

### 2. Write the processor

Create `use_cases/iban_validator/processor.py`:

```python
"""IBAN Validator processor.

Reads a list of IBANs and returns a file flagging which ones are valid.
"""

from io import BytesIO
import re
import pandas as pd

INPUT_FORMATS = ["xlsx", "xls", "csv"]
INPUT_DESCRIPTION = "Excel/CSV file with an `iban` column."
OUTPUT_FILENAME = "iban_validation_result.xlsx"
OUTPUT_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
OUTPUT_DESCRIPTION = "Excel file with `is_valid` and `country_code` columns added."
SAMPLE_FILE = "samples/iban_validator_sample.csv"

IBAN_RE = re.compile(r"^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$")

def _check(iban):
    iban = re.sub(r"\s+", "", str(iban)).upper()
    if not IBAN_RE.match(iban):
        return False, ""
    # Light mod-97 check
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(int(c, 36)) if c.isalpha() else c for c in rearranged)
    return int(digits) % 97 == 1, iban[:2]

def _read(file_bytes, filename):
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    return pd.read_excel(BytesIO(file_bytes))

def process(file_bytes, filename):
    df = _read(file_bytes, filename)
    if "iban" not in df.columns:
        raise ValueError("Input file must contain an 'iban' column.")
    results = [_check(x) for x in df["iban"]]
    df["is_valid"] = [r[0] for r in results]
    df["country_code"] = [r[1] for r in results]
    out = BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue(), OUTPUT_FILENAME, OUTPUT_MIME
```

### 3. Create a sample input

`samples/iban_validator_sample.csv`:

```csv
client,iban
Alice,DE89370400440532013000
Bob,FR1420041010050500013M02606
Eve,XX00BAD0
```

### 4. Register the processor

Edit `use_cases/registry.py`:

```python
from .iban_validator import processor as iban_validator

PROCESSORS = {
    # ...existing entries...
    "iban-validator": iban_validator,
}
```

### 5. Add the service to the catalog

Append an entry to `data/services.json`:

```json
{
  "id": "iban-validator",
  "name": "IBAN Validator",
  "category": "Compliance & Controls",
  "icon": "🏦",
  "status": "live",
  "owner": "Compliance Team",
  "frequency": "Daily",
  "time_saved_h": 2,
  "tags": ["iban", "validation", "compliance"],
  "origin_macro": "IBAN_CHECK.xlsm",
  "description": "Validates a list of IBANs and flags invalid ones.",
  "purpose": "Run a syntactic and mod-97 check on each IBAN to flag invalid ones before they reach the payment system.",
  "inputs":  ["Excel/CSV file with an `iban` column", "Optional: a `client` column for traceability"],
  "outputs": ["Excel file with `is_valid` and `country_code` columns added"],
  "benefits": ["Catches bad IBANs upstream of the payment chain", "Reduces rejected transactions"]
}
```

If the category color is new, add it in `CATEGORY_THEMES` in `app.py`:

```python
CATEGORY_THEMES = {
    # ...
    "Compliance & Controls": "#dc2626",  # already present in the default themes
}
```

### 6. Test locally

```bash
# Unit-style sanity check via the registry
python - <<'PY'
import sys; sys.path.insert(0, '.')
from use_cases.registry import PROCESSORS
from pathlib import Path
p = PROCESSORS["iban-validator"]
out, name, mime = p.process(Path(p.SAMPLE_FILE).read_bytes(), Path(p.SAMPLE_FILE).name)
print(name, len(out), mime)
PY

# Full app
streamlit run app.py
```

Open the marketplace → click **IBAN Validator** → download the sample →
upload it → click **▶︎ Run processing** → download the result.

### 7. Commit

```bash
git add use_cases/iban_validator samples/iban_validator_sample.csv \
        use_cases/registry.py data/services.json
git commit -m "Add IBAN Validator use case"
```

That's the whole loop. No app code needs to change to add a new use case
— the registry + JSON entry are enough.

---

## Configuration & theming

- **Contact email**: change `CONTACT_EMAIL` near the top of `app.py`.
  It propagates to the hero, the sidebar and the About page.
- **Category colors**: edit the `CATEGORY_THEMES` dict in `app.py`.
- **Dark theme**: forced in CSS via `inject_styles()`. Edit the
  `background-color` / `color` rules there to rebrand.
- **Logo / page title**: change `st.set_page_config(...)` at the top of
  `app.py`.

---

## Deployment notes (Domino, proxies)

The portal is a plain Streamlit app and runs anywhere Streamlit runs.
Two things to know if you deploy on Domino (or a similar managed host):

### 1. The dark theme is forced in CSS
`.streamlit/config.toml` is **not always read** by the host (different
working directory, host theme overrides, etc.). That's why the dark
theme is also forced in CSS inside `app.py` (`inject_styles()`). Don't
remove that block unless you confirm `config.toml` is picked up.

### 2. Keep the open counter across restarts
By default, click counts are written to `data/counts.json`. On Domino,
the **project workspace is ephemeral**: when the app stops and restarts,
the working directory is reset to the latest git state, so `counts.json`
is lost.

Point the counter at a persistent location via the **`HOS_COUNTS_FILE`**
environment variable:

```bash
# Example: store counts in a Domino dataset (persistent across runs)
export HOS_COUNTS_FILE=/domino/datasets/local/<your-dataset>/counts.json

# Or on any container host with a persistent volume:
export HOS_COUNTS_FILE=/mnt/persistent/houseofservicing/counts.json

streamlit run app.py
```

In Domino, set it under **App Settings → Environment Variables** so it's
applied to every run. Make sure the chosen path lives on a Domino
Dataset (or another persistent mount) — files written under the project
checkout are wiped at each restart.

If `HOS_COUNTS_FILE` is not set, the file falls back to `data/counts.json`,
which is fine for local development but ephemeral on Domino.

For higher volumes (multi-user concurrent writes, dashboards across many
services), swap the JSON file for a real DB (SQLite, Postgres) — the
`load_counts` / `increment_count` helpers in `app.py` are the only two
places to change.

---

## Runtime data files

| File | Created by | Committed? |
|---|---|---|
| `data/services.json` | You (catalog) | ✅ Yes |
| `counts.json` (path set by `HOS_COUNTS_FILE`, defaults to `data/counts.json`) | "Open service" clicks | ❌ Gitignored |

If you want to seed counts in a fresh deployment, commit a starter
version of `counts.json` and remove it from `.gitignore`.

"""Self-Care Request Triage processor.

Reads incoming client requests, labels them self-care vs. agent-required, and
suggests a routing action.
"""

from io import BytesIO

import pandas as pd

INPUT_FORMATS = ["xlsx", "xls", "csv"]
INPUT_DESCRIPTION = (
    "Excel/CSV file with at least `subject` and `body` columns describing each request."
)
OUTPUT_FILENAME = "self_care_triage_result.xlsx"
OUTPUT_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
OUTPUT_DESCRIPTION = (
    "Excel file enriched with a `triage_label`, a `suggested_action` and a `confidence` score."
)
SAMPLE_FILE = "samples/self_care_triage_sample.csv"

SELF_CARE_KEYWORDS = [
    "password",
    "reset password",
    "update address",
    "change phone",
    "download statement",
    "balance",
    "subscribe",
    "unsubscribe",
    "open hours",
    "branch",
    "iban",
]
URGENT_KEYWORDS = ["fraud", "complaint", "dispute", "legal", "urgent"]


def _triage(text):
    text = text.lower()
    if any(k in text for k in URGENT_KEYWORDS):
        return "requires-agent", "Escalate to a human agent", 0.95
    matches = [k for k in SELF_CARE_KEYWORDS if k in text]
    if matches:
        return (
            "self-care",
            f"Suggest self-service: {matches[0]}",
            min(0.6 + 0.1 * len(matches), 0.95),
        )
    return "requires-agent", "Route to the standard queue", 0.5


def _read(file_bytes, filename):
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    return pd.read_excel(BytesIO(file_bytes))


def process(file_bytes, filename):
    df = _read(file_bytes, filename)
    for col in ("subject", "body"):
        if col not in df.columns:
            df[col] = ""

    triaged = [
        _triage(f"{s} {b}")
        for s, b in zip(df["subject"].astype(str), df["body"].astype(str))
    ]
    df["triage_label"] = [t[0] for t in triaged]
    df["suggested_action"] = [t[1] for t in triaged]
    df["confidence"] = [round(t[2], 2) for t in triaged]

    out = BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue(), OUTPUT_FILENAME, OUTPUT_MIME

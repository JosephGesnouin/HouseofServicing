"""Authority Letter Generator processor.

Generates one printable HTML authority letter per input row and bundles them
into a ZIP archive.
"""

from datetime import date
from io import BytesIO
from zipfile import ZipFile

import pandas as pd

INPUT_FORMATS = ["xlsx", "xls", "csv"]
INPUT_DESCRIPTION = (
    "Excel/CSV file with columns: `client_name`, `client_address`, "
    "`authority_scope`, `signatory`."
)
OUTPUT_FILENAME = "authority_letters.zip"
OUTPUT_MIME = "application/zip"
OUTPUT_DESCRIPTION = (
    "ZIP archive containing one printable HTML authority letter per input row."
)
SAMPLE_FILE = "samples/authority_letter_sample.csv"

REQUIRED_COLUMNS = ["client_name", "client_address", "authority_scope", "signatory"]

TEMPLATE = """<html><body style="font-family:Georgia,serif;max-width:680px;margin:40px auto;color:#0f172a;">
<h2 style="text-align:center;letter-spacing:.04em;">AUTHORITY LETTER</h2>
<p>Date: {date}</p>
<p>From: <strong>{client_name}</strong><br/>{client_address}</p>
<p>I, the undersigned, hereby authorize the bearer of this letter to act on my
behalf for the following scope:</p>
<blockquote style="border-left:4px solid #2563eb;padding:8px 12px;color:#334155;
background:#f8fafc;">{scope}</blockquote>
<p>This authorization is granted in accordance with the applicable terms and
conditions of the institution.</p>
<p style="margin-top:60px;">Signed,<br/><strong>{signatory}</strong></p>
</body></html>
"""


def _slug(s):
    return "".join(c if c.isalnum() else "_" for c in str(s))[:40]


def _read(file_bytes, filename):
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    return pd.read_excel(BytesIO(file_bytes))


def process(file_bytes, filename):
    df = _read(file_bytes, filename)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s): {', '.join(missing)}. "
            f"Expected: {', '.join(REQUIRED_COLUMNS)}."
        )

    buf = BytesIO()
    with ZipFile(buf, "w") as zf:
        for i, row in df.iterrows():
            html = TEMPLATE.format(
                date=date.today().isoformat(),
                client_name=row["client_name"],
                client_address=str(row["client_address"]).replace("\n", "<br/>"),
                scope=row["authority_scope"],
                signatory=row["signatory"],
            )
            name = f"authority_letter_{i + 1:03d}_{_slug(row['client_name'])}.html"
            zf.writestr(name, html)
    return buf.getvalue(), OUTPUT_FILENAME, OUTPUT_MIME

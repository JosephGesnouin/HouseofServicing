"""MT103 / XML to Proof of Payment processor.

Parses a SWIFT MT103 message or a pain.001-style XML payment file and renders
a printable HTML proof of payment.
"""

import re
import xml.etree.ElementTree as ET

INPUT_FORMATS = ["txt", "xml"]
INPUT_DESCRIPTION = "SWIFT MT103 message (.txt) or pain.001-style XML payment file."
OUTPUT_FILENAME = "proof_of_payment.html"
OUTPUT_MIME = "text/html"
OUTPUT_DESCRIPTION = "Printable HTML proof of payment summarizing the key fields."
SAMPLE_FILE = "samples/mt103_sample.txt"

MT103_FIELDS = {
    "20": "Transaction reference",
    "23B": "Bank operation code",
    "32A": "Value date / Currency / Amount",
    "50K": "Ordering customer",
    "52A": "Ordering institution",
    "57A": "Account with institution",
    "59": "Beneficiary",
    "70": "Remittance information",
    "71A": "Charges",
}

XML_FIELDS = [
    ("MsgId", "Message ID"),
    ("EndToEndId", "End-to-end ID"),
    ("InstdAmt", "Amount"),
    ("Cdtr", "Creditor"),
    ("Dbtr", "Debtor"),
    ("RmtInf", "Remittance"),
]

TEMPLATE = """<html><body style="font-family:Arial,sans-serif;max-width:720px;margin:40px auto;color:#0f172a;">
<h2 style="border-bottom:2px solid #2563eb;padding-bottom:6px;">Proof of Payment</h2>
<p style="color:#64748b;">Generated from {source} payment message</p>
<table style="width:100%;border-collapse:collapse;margin-top:20px;">
{rows}
</table>
<p style="margin-top:40px;color:#64748b;font-size:.85rem;">
This document summarizes the payment data extracted from the original message.
It is provided for information purposes.
</p>
</body></html>
"""


def _parse_mt103(text):
    fields = {}
    for match in re.finditer(r":(\d{2}[A-Z]?):([^\n]+(?:\n(?![:\-]).+)*)", text):
        code, value = match.group(1), match.group(2).strip()
        fields[code] = value
    return fields


def _parse_xml(content):
    fields = {}
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}") from e
    for tag, label in XML_FIELDS:
        for el in root.iter():
            local = el.tag.split("}", 1)[-1]
            if local == tag:
                text = " ".join(t.strip() for t in el.itertext() if t.strip())
                if text:
                    fields[label] = text
                    break
    return fields


def process(file_bytes, filename):
    content = file_bytes.decode("utf-8", errors="ignore")
    if filename.lower().endswith(".xml"):
        fields = _parse_xml(content)
        source = "XML"
    else:
        raw = _parse_mt103(content)
        fields = {MT103_FIELDS.get(k, k): v for k, v in raw.items()}
        source = "MT103"

    if not fields:
        raise ValueError("No payment fields could be extracted from the file.")

    rows = "".join(
        f"<tr><td style='padding:6px 10px;border:1px solid #e2e8f0;font-weight:600;width:35%;'>{k}</td>"
        f"<td style='padding:6px 10px;border:1px solid #e2e8f0;white-space:pre-wrap;'>{v}</td></tr>"
        for k, v in fields.items()
    )
    html = TEMPLATE.format(source=source, rows=rows)
    return html.encode("utf-8"), OUTPUT_FILENAME, OUTPUT_MIME

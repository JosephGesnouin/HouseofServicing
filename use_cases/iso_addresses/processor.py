"""ISO-Structured Addresses processor.

Parses free-form addresses, splits them into ISO-style fields and produces a
draft customer email.
"""

import re
from io import BytesIO

import pandas as pd

INPUT_FORMATS = ["xlsx", "xls", "csv"]
INPUT_DESCRIPTION = (
    "Excel/CSV file with at least an `address` column (free-form). "
    "Optional columns: `name`, `country`."
)
OUTPUT_FILENAME = "iso_addresses_result.xlsx"
OUTPUT_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
OUTPUT_DESCRIPTION = (
    "Excel file with structured columns (street, number, postal_code, city, country), "
    "an `is_iso_compliant` flag and a `customer_email` draft per row."
)
SAMPLE_FILE = "samples/iso_addresses_sample.csv"


def _parse(address):
    if not isinstance(address, str):
        return {}
    parts = [p.strip() for p in address.split(",") if p.strip()]
    result = {}
    for p in parts:
        m = re.match(r"^(\d{4,5})\s+(.+)$", p)
        if m:
            result["postal"] = m.group(1)
            result["city"] = m.group(2)
            break
    if len(parts) >= 3:
        result["country"] = parts[-1]
    if parts:
        first = parts[0]
        m = re.match(r"^(\d+[A-Za-z]?)\s+(.+)$", first)
        if m:
            result["number"], result["street"] = m.group(1), m.group(2)
        else:
            m = re.match(r"^(.+?)\s+(\d+[A-Za-z]?)$", first)
            if m:
                result["street"], result["number"] = m.group(1), m.group(2)
            else:
                result["street"] = first
    return result


def _is_compliant(p):
    return all(p.get(k) for k in ("number", "street", "postal", "city"))


def _build_email(name, parsed, compliant):
    name = name or "Customer"
    if compliant:
        return (
            f"Dear {name},\n\n"
            "We have standardized your address to ISO format:\n"
            f"{parsed.get('number', '')} {parsed.get('street', '')}\n"
            f"{parsed.get('postal', '')} {parsed.get('city', '')}\n"
            f"{parsed.get('country', '')}\n\n"
            "No action is required on your side.\n\n"
            "Best regards,\nThe Servicing Team"
        )
    return (
        f"Dear {name},\n\n"
        "We could not automatically standardize your address. "
        "Could you please confirm the following:\n"
        "- Street name and number\n- Postal code and city\n- Country\n\n"
        "Thank you,\nThe Servicing Team"
    )


def _read(file_bytes, filename):
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    return pd.read_excel(BytesIO(file_bytes))


def process(file_bytes, filename):
    df = _read(file_bytes, filename)
    if "address" not in df.columns:
        raise ValueError("Input file must contain an 'address' column.")

    parsed_list = [_parse(a) for a in df["address"].astype(str)]
    df["street"] = [p.get("street", "") for p in parsed_list]
    df["number"] = [p.get("number", "") for p in parsed_list]
    df["postal_code"] = [p.get("postal", "") for p in parsed_list]
    df["city"] = [p.get("city", "") for p in parsed_list]
    df["country"] = [
        p.get("country") or (df.iloc[i].get("country", "") if "country" in df.columns else "")
        for i, p in enumerate(parsed_list)
    ]
    df["is_iso_compliant"] = [_is_compliant(p) for p in parsed_list]

    names = df["name"] if "name" in df.columns else [None] * len(df)
    df["customer_email"] = [
        _build_email(n, p, c)
        for n, p, c in zip(names, parsed_list, df["is_iso_compliant"])
    ]

    out = BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue(), OUTPUT_FILENAME, OUTPUT_MIME

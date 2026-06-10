"""Maps each service id (data/services.json) to its processor module.

A processor module must expose:
- INPUT_FORMATS:        list[str]   accepted upload extensions (no dot)
- INPUT_DESCRIPTION:    str         human-readable description of expected input
- OUTPUT_FILENAME:      str         default download filename
- OUTPUT_MIME:          str         MIME type for the download
- OUTPUT_DESCRIPTION:   str         human-readable description of what comes back
- SAMPLE_FILE:          str | None  path (relative to project root) to a sample input
- process(file_bytes: bytes, filename: str) -> tuple[bytes, str, str]
      Returns (output_bytes, output_filename, mime).
      Raise ValueError with a helpful message on bad input.
"""

from .authority_letter import processor as authority_letter
from .iso_addresses import processor as iso_addresses
from .mt103_proof_of_payment import processor as mt103_proof_of_payment
from .self_care_triage import processor as self_care_triage

PROCESSORS = {
    "iso-addresses": iso_addresses,
    "self-care-triage": self_care_triage,
    "authority-letter": authority_letter,
    "mt103-proof-of-payment": mt103_proof_of_payment,
}


def get_processor(service_id):
    return PROCESSORS.get(service_id)

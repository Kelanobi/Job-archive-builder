import re
from dataclasses import dataclass
from pathlib import Path

import fitz

from .errors import CustomerNotFound, DCLNotFound

_DCL_TERMS = ("despatch checklist", "dispatch checklist", "dcl")
_NEXT_FIELDS = (
    "contracts", "project substation name", "project name", "date", "revision",
    "rev", "customer order number", "order", "po number",
)


@dataclass(frozen=True)
class DCLData:
    pdf_path: Path
    order_number: str
    customer_name: str


def _revision(path: Path) -> int:
    matches = re.findall(r"(?:rev(?:ision)?\s*[-_()]?\s*)(\d+)", path.stem, re.I)
    return int(matches[-1]) if matches else -1


def find_candidates(dcl_folder: Path, job_number: str) -> list[Path]:
    try:
        pdfs = [p for p in Path(dcl_folder).iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    except OSError as exc:
        raise DCLNotFound("DCL not found.") from exc
    preferred = [p for p in pdfs if any(term in p.name.lower() for term in _DCL_TERMS)]
    candidates = preferred or pdfs
    def key(path: Path):
        try:
            modified = path.stat().st_mtime
        except OSError:
            modified = 0
        return (job_number in path.stem, _revision(path), modified)
    return sorted(candidates, key=key, reverse=True)


def _first_page(path: Path):
    with fitz.open(path) as document:
        if document.needs_pass or document.page_count < 1:
            raise ValueError("Unreadable PDF")
        page = document[0]
        return page.get_text("text"), page.get_text("words", sort=True)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t\r\n|;")


def _extract_order(text: str) -> str | None:
    match = re.search(r"\bOrder\s*:\s*([0-9]+)\b", text, re.I)
    return match.group(1) if match else None


def _extract_customer_text(text: str) -> str | None:
    flat = re.sub(r"[\t\r\n]+", " ", text)
    stops = "|".join(re.escape(field) for field in _NEXT_FIELDS)
    match = re.search(rf"\bCustomer\s*:\s*(.+?)(?=\s+(?:{stops})\s*:|$)", flat, re.I)
    if not match:
        return None
    value = _normalise(match.group(1))
    return value or None


def _extract_customer_words(words: list[tuple]) -> str | None:
    # Locate the Customer label, then collect words to its right on the same row.
    for index, word in enumerate(words):
        token = str(word[4]).strip()
        if token.lower().rstrip(":") != "customer":
            continue
        x_end, y_top, y_bottom = float(word[2]), float(word[1]), float(word[3])
        row = []
        for other in words[index + 1:]:
            text = str(other[4]).strip()
            if float(other[0]) + 1 < x_end:
                continue
            if abs(float(other[1]) - y_top) > max(5.0, y_bottom - y_top):
                continue
            if text.lower().rstrip(":") in _NEXT_FIELDS:
                break
            row.append((float(other[0]), text))
        value = _normalise(" ".join(text for _, text in sorted(row)))
        if value:
            return value
    return None


def parse_dcl(path: Path, expected_job: str) -> DCLData:
    text, words = _first_page(Path(path))
    order = _extract_order(text)
    if order != expected_job:
        raise ValueError("DCL order mismatch")
    customer = _extract_customer_text(text) or _extract_customer_words(words)
    if not customer:
        raise CustomerNotFound("Customer name not found in DCL.")
    return DCLData(Path(path), order, customer)


def select_and_parse(dcl_folder: Path, job_number: str) -> DCLData:
    candidates = find_candidates(dcl_folder, job_number)
    if not candidates:
        raise DCLNotFound("DCL not found.")
    saw_valid_order = False
    for path in candidates:
        try:
            return parse_dcl(path, job_number)
        except CustomerNotFound:
            saw_valid_order = True
        except Exception:
            continue
    if saw_valid_order:
        raise CustomerNotFound("Customer name not found in DCL.")
    raise DCLNotFound("DCL not found.")


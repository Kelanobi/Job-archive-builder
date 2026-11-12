from pathlib import Path

import fitz
import pytest

from app.dcl_parser import find_candidates, parse_dcl, select_and_parse
from app.errors import DCLNotFound


def make_pdf(path: Path, order="50591150", customer="ZHEJIANG XINDIAN ELECTRIC Co., Ltd"):
    doc = fitz.open()
    page = doc.new_page(width=842, height=595)
    page.insert_text((40, 50), "Despatch Checklist (DCL)")
    page.insert_text((40, 85), f"Order:{order}    PO Number:PDM-SY-260519    Customer:{customer}")
    page.insert_text((40, 110), "Contracts:Bradley, Joseph    Project Substation Name:Surab")
    doc.save(path)
    doc.close()


def test_extracts_customer_and_validates_order(tmp_path):
    pdf = tmp_path / "50591150 - Despatch Checklist (Rev03).pdf"
    make_pdf(pdf)
    data = parse_dcl(pdf, "50591150")
    assert data.customer_name == "ZHEJIANG XINDIAN ELECTRIC Co., Ltd"
    with pytest.raises(ValueError):
        parse_dcl(pdf, "12345678")


def test_prefers_highest_revision_and_falls_back_from_mismatch(tmp_path):
    good = tmp_path / "50591150 DCL Rev02.pdf"
    bad = tmp_path / "50591150 DCL Rev03.pdf"
    make_pdf(good)
    make_pdf(bad, order="99999999")
    assert find_candidates(tmp_path, "50591150")[0] == bad
    assert select_and_parse(tmp_path, "50591150").pdf_path == good


def test_rejects_only_mismatched_documents(tmp_path):
    make_pdf(tmp_path / "50591150 DCL Rev01.pdf", order="11111111")
    with pytest.raises(DCLNotFound):
        select_and_parse(tmp_path, "50591150")


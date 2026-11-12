from pathlib import Path

from app.shortcut_manager import safe_filename, shortcut_paths


def test_safe_filename_preserves_customer_punctuation():
    assert safe_filename("ACME & Sons, Ltd.") == "ACME & Sons, Ltd"
    assert safe_filename('A/B:C*D?E"F<G>H|I') == "ABCDEFGHI"


def test_friend_layout_places_shortcut_inside_named_job_folder(tmp_path):
    folder, shortcut = shortcut_paths(tmp_path, "50591150", "ACME & Sons, Ltd", True)
    assert folder == tmp_path / "50591150 - ACME & Sons, Ltd"
    assert shortcut == folder / "50591150 - ACME & Sons, Ltd.lnk"


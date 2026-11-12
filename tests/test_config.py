import config


def test_archive_configuration():
    assert str(config.ARCHIVE_DIR) == r"C:\Users\kelvin.obi\OneDrive - Ralliant\Job files"
    assert config.CREATE_JOB_SUBFOLDER is True


def test_afeez_build_name_selects_afeez_archive(monkeypatch):
    monkeypatch.setattr(config.sys, "executable", r"C:\Apps\Qualitrol Job Archive - Afeez.exe")
    assert str(config.archive_directory()) == r"C:\Users\Afeez.Sotannde\OneDrive - Ralliant\Job files"

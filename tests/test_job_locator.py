import pytest

from app.errors import JobNotFound, NetworkUnavailable
from app.job_locator import locate_job, validate_job_number


def test_validate_job_number():
    assert validate_job_number(" 50591150 ") == "50591150"
    with pytest.raises(ValueError):
        validate_job_number("50A")


def test_locate_job(tmp_path):
    (tmp_path / "50591150").mkdir()
    assert locate_job(tmp_path, "50591150") == tmp_path / "50591150"
    with pytest.raises(JobNotFound):
        locate_job(tmp_path, "99999999")
    with pytest.raises(NetworkUnavailable):
        locate_job(tmp_path / "missing", "50591150")


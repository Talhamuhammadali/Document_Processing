"""Tests for the mock index."""

from app.core.mock_index import build_index, match


def test_index_covers_all_mocks() -> None:
    """Every source PDF with a mock is indexed."""
    assert len(build_index()) >= 10


def test_match_by_filename() -> None:
    """A known filename matches an entry whose paths exist."""
    entry = match("03_CAT_3406C_marine_propulsion_spec.pdf")
    assert entry is not None
    assert entry.pdf_path.exists()
    assert entry.mock_json_path.exists()


def test_no_match_returns_none() -> None:
    """An unknown filename returns None."""
    assert match("not_a_real_file.pdf") is None

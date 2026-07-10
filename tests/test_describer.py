"""Tests for the fake describer."""

from app.core.describer import FakeDescriber


def test_describe_image_deterministic_and_nonempty() -> None:
    """Image descriptions are non-empty and stable for the same bytes."""
    d = FakeDescriber()
    first = d.describe_image(b"abc")
    assert first
    assert first == d.describe_image(b"abc")


def test_describe_image_differs_by_input() -> None:
    """Different images produce different descriptions."""
    d = FakeDescriber()
    assert d.describe_image(b"abc") != d.describe_image(b"xyz")


def test_describe_table_deterministic_and_nonempty() -> None:
    """Table descriptions are non-empty and stable for the same markdown."""
    d = FakeDescriber()
    first = d.describe_table("| a | b |")
    assert first
    assert first == d.describe_table("| a | b |")


def test_describe_table_differs_by_input() -> None:
    """Different tables produce different descriptions."""
    d = FakeDescriber()
    assert d.describe_table("one") != d.describe_table("two")

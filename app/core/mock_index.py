"""Map an uploaded file to its precomputed Docling mock and source PDF."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class MockEntry:
    """A precomputed mock and its source PDF.

    Attributes
    ----------
    mock_json_path : Path
        Path to the Docling mock JSON.
    pdf_path : Path
        Path to the source PDF the mock was produced from.

    """

    mock_json_path: Path
    pdf_path: Path


@lru_cache(maxsize=1)
def build_index() -> dict[str, MockEntry]:
    """Build a filename to MockEntry index by pairing PDFs with mock JSON.

    Returns
    -------
    dict[str, MockEntry]
        Mapping of PDF filename to its mock entry, for every PDF that has a
        matching {stem}.json in the benchmark directory.

    """
    index: dict[str, MockEntry] = {}
    for pdf in sorted(settings.pdf_dir.glob("*.pdf")):
        mock = settings.benchmark_dir / f"{pdf.stem}.json"
        if mock.exists():
            index[pdf.name] = MockEntry(mock_json_path=mock, pdf_path=pdf)
    return index


def match(filename: str) -> MockEntry | None:
    """Match an uploaded filename to a precomputed mock.

    Parameters
    ----------
    filename : str
        The uploaded file's name.

    Returns
    -------
    MockEntry | None
        The matching entry, or None if no mock exists for this filename.

    """
    return build_index().get(filename)

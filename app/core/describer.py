"""Description generation for chunk content (image and table)."""

import hashlib
from abc import ABC, abstractmethod


class Describer(ABC):
    """Generates short natural-language descriptions of chunk content."""

    @abstractmethod
    def describe_image(self, image_png: bytes) -> str:
        """Describe a picture from its PNG image bytes.

        Parameters
        ----------
        image_png : bytes
            PNG-encoded image bytes.

        Returns
        -------
        str
            A short description of the image.

        """

    @abstractmethod
    def describe_table(self, table_markdown: str) -> str:
        """Describe a table from its grid or markdown representation.

        Parameters
        ----------
        table_markdown : str
            The table rendered as markdown or a flattened grid string.

        Returns
        -------
        str
            A short description of the table.

        """


class FakeDescriber(Describer):
    """Deterministic stub describer that needs no model.

    Output is derived from a hash of the input so it is stable across runs and
    differs for different inputs, which keeps tests meaningful.
    """

    def describe_image(self, image_png: bytes) -> str:
        """Return a deterministic placeholder description for an image."""
        digest = hashlib.sha256(image_png).hexdigest()[:8]
        return f"[fake image description {digest}] {len(image_png)} bytes"

    def describe_table(self, table_markdown: str) -> str:
        """Return a deterministic placeholder description for a table."""
        digest = hashlib.sha256(table_markdown.encode()).hexdigest()[:8]
        rows = table_markdown.count("\n") + 1
        return f"[fake table description {digest}] ~{rows} rows"

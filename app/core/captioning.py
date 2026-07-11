"""Placeholder hook for the out-of-scope background captioning job."""

import logging

logger = logging.getLogger(__name__)


def enqueue_captioning(doc_id: str) -> None:
    """Mark where chunk captioning will be scheduled once built.

    Documents are stored without descriptions; a later background job will
    generate and backfill captions (and re-embed picture chunks). This is a
    deliberate no-op placeholder for that out-of-scope work.

    Parameters
    ----------
    doc_id : str
        The document whose captions are deferred.

    """
    logger.info("captioning deferred for %s (out of scope; placeholder hook)", doc_id)

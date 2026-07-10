"""Integration tests for the document endpoints, backed by a testcontainer Redis."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer

import app.routers.documents as documents_router
from app.core.config import settings
from app.main import app
from app.storage.factory import get_repository

client = TestClient(app)
_DOC = "05_CAT_3508B_marine_auxiliary_spec"


@pytest.fixture(scope="session", autouse=True)
def _redis_container() -> Iterator[None]:
    """Start an ephemeral redis-stack and point the app's repository at it."""
    with RedisContainer("redis/redis-stack:latest") as container:
        settings.redis_host = container.get_container_host_ip()
        settings.redis_port = int(container.get_exposed_port(6379))
        get_repository.cache_clear()
        documents_router._repo = get_repository()
        yield


def test_upload_and_fetch_flow() -> None:
    """Upload a known PDF, then read back metadata, chunks, image, and search."""
    with open(f"data/tech_doc_examples/{_DOC}.pdf", "rb") as handle:
        resp = client.post("/documents/upload", files={"file": (f"{_DOC}.pdf", handle, "application/pdf")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_id"] == _DOC
    assert body["num_chunks"] > 0

    assert _DOC in client.get("/documents").json()["documents"]
    assert client.get(f"/documents/{_DOC}").json()["num_pages"] >= 1

    chunks = client.get(f"/documents/{_DOC}/chunks").json()["chunks"]
    assert chunks

    pictures = [c for c in chunks if c["kind"] == "picture" and c["image_ref"]]
    if pictures:
        image = client.get(pictures[0]["image_ref"])
        assert image.status_code == 200
        assert image.headers["content-type"] == "image/png"

    for table in (c for c in chunks if c["kind"] == "table"):
        assert table["image_ref"] is None  # tables carry no image

    search = client.post("/documents/search", json={"query": "power rating", "top_k": 3})
    assert search.status_code == 200
    assert len(search.json()["hits"]) >= 1


def test_upload_unknown_file_returns_404() -> None:
    """An upload with no matching mock returns 404."""
    resp = client.post("/documents/upload", files={"file": ("nope.pdf", b"x", "application/pdf")})
    assert resp.status_code == 404


def test_get_missing_document_returns_404() -> None:
    """Fetching an unknown document returns 404."""
    assert client.get("/documents/does-not-exist").status_code == 404

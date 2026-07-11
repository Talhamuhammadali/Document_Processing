"""API-contract tests for the async document endpoints, backed by a testcontainer Redis.

These exercise the enqueue side only (no worker, no models): open/upload write a job
record and enqueue it, status/available reflect the queued state, and unprocessed
documents 404. Real conversion is covered by the worker, not here.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer

import app.routers.documents as documents_router
from app.core.config import settings
from app.core.jobs import get_job
from app.core.redis_client import redis_client
from app.main import app
from app.storage.factory import get_repository

_FILENAME = "tech_doc_examples/05_CAT_3508B_marine_auxiliary_spec.pdf"
_DOC = "tech_doc_examples__05_CAT_3508B_marine_auxiliary_spec"


@pytest.fixture(scope="session", autouse=True)
def _redis_container() -> Iterator[None]:
    """Start an ephemeral redis-stack and point the app's repository/clients at it."""
    with RedisContainer("redis/redis-stack:latest") as container:
        settings.redis_host = container.get_container_host_ip()
        settings.redis_port = int(container.get_exposed_port(6379))
        get_repository.cache_clear()
        documents_router._repo = get_repository()
        documents_router._redis = redis_client(decode_responses=True)
        yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Yield a TestClient that runs the lifespan (seeds configs, opens the arq pool)."""
    with TestClient(app) as test_client:
        yield test_client


def test_open_enqueues_job(client: TestClient) -> None:
    """Opening a sample writes a queued job record and returns queued status."""
    resp = client.post("/documents/open", json={"filename": _FILENAME, "mode": "accurate", "ocr": "rapidocr"})
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"document_id": _DOC, "status": "queued"}

    job = get_job(documents_router._redis, _DOC)
    assert job is not None
    assert job.mode == "accurate"
    assert job.ocr == "rapidocr"
    assert job.status.value == "queued"


def test_status_reflects_selection(client: TestClient) -> None:
    """The status endpoint echoes the queued state and the chosen mode/ocr."""
    client.post("/documents/open", json={"filename": _FILENAME, "mode": "fast", "ocr": "none"})
    resp = client.get(f"/documents/{_DOC}/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "queued"
    assert body["mode"] == "fast"
    assert body["ocr"] == "none"


def test_available_lists_samples_with_status(client: TestClient) -> None:
    """The available list includes all samples and surfaces queued status."""
    client.post("/documents/open", json={"filename": _FILENAME})
    resp = client.get("/documents/available")
    assert resp.status_code == 200
    entry = next(d for d in resp.json()["available"] if d["id"] == _DOC)
    assert entry["status"] == "queued"


def test_open_unknown_sample_404(client: TestClient) -> None:
    """Opening a filename with no matching sample PDF is a 404."""
    resp = client.post("/documents/open", json={"filename": "does_not_exist.pdf"})
    assert resp.status_code == 404


def test_unprocessed_document_metadata_404(client: TestClient) -> None:
    """A queued-but-unprocessed document has no stored metadata yet."""
    client.post("/documents/open", json={"filename": _FILENAME})
    assert client.get(f"/documents/{_DOC}").status_code == 404


def test_compare_enqueues_six_variants(client: TestClient) -> None:
    """Compare enqueues one job per mode x OCR config and reports all six."""
    resp = client.post("/documents/compare", json={"filename": _FILENAME})
    assert resp.status_code == 200
    variants = resp.json()["variants"]
    assert {(v["mode"], v["ocr"]) for v in variants} == {
        (m, o) for m in ("fast", "accurate") for o in ("none", "tesseract", "rapidocr")
    }

    comp = client.get(f"/documents/compare/{_DOC}").json()
    assert len(comp["variants"]) == 6
    assert all(v["status"] == "queued" for v in comp["variants"])

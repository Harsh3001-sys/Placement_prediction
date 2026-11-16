import pytest

from app import create_app


VERCEL_ORIGIN = "https://placement-prediction-rg4i-pqj3lxfs-harsh-projects18.vercel.app"


@pytest.fixture()
def cors_client(monkeypatch):
    # Include whitespace and a trailing slash to ensure env parsing is robust.
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "https://placement-prediction-rg4i.vercel.app, "
        f"{VERCEL_ORIGIN}/",
    )
    app = create_app({"TESTING": True})
    return app.test_client()


@pytest.mark.parametrize("path", ["/api/health", "/api/ppo/health"])
def test_preflight_allows_vercel_origin(cors_client, path):
    res = cors_client.open(
        path,
        method="OPTIONS",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("Access-Control-Allow-Origin") == VERCEL_ORIGIN


@pytest.mark.parametrize("path", ["/api/health", "/api/ppo/health"])
def test_get_includes_cors_header_for_vercel_origin(cors_client, path):
    res = cors_client.get(path, headers={"Origin": VERCEL_ORIGIN})
    assert res.status_code == 200
    assert res.headers.get("Access-Control-Allow-Origin") == VERCEL_ORIGIN

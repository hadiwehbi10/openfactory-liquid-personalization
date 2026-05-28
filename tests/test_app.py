"""Tests for the OpenFactory Flask web routes."""

from liquid_personalization_app.app import create_app


def test_home_page_loads() -> None:
    ofa_app = create_app(test_mode=True)
    client = ofa_app.app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"OpenFactory Liquid Personalization" in response.data
    assert b"Create product order" in response.data


def test_health_route_returns_ok() -> None:
    ofa_app = create_app(test_mode=True)
    client = ofa_app.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_create_order_generates_virtual_work_order() -> None:
    ofa_app = create_app(test_mode=True)
    client = ofa_app.app.test_client()

    response = client.post(
        "/order",
        data={
            "color": "#8c3636",
            "volume_ml": "250",
            "label_text": "Test 1",
        },
    )

    assert response.status_code == 200
    assert b"Recipe and production sequence generated." in response.data
    assert b"Test 1" in response.data
    assert b"RGB(140, 54, 54)" in response.data
    assert b"Red" in response.data
    assert b"Green" in response.data
    assert b"Blue" in response.data
    assert b"Base / Clear" in response.data
    assert b"Create personalized product order" in response.data
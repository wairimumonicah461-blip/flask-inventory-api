import pytest
import requests
from unittest.mock import Mock, patch
from app import app, fetch_product, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    original_inventory = [item.copy() for item in inventory]

    with app.test_client() as test_client:
        yield test_client

    inventory.clear()
    inventory.extend(original_inventory)


def test_get_all_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert len(response.get_json()) >= 2


def test_get_single_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Organic Almond Milk"


def test_get_missing_item(client):
    response = client.get("/inventory/9999")

    assert response.status_code == 404


def test_create_item(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Mango Juice",
            "price": 120,
            "stock": 10
        }
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Mango Juice"


def test_create_item_with_invalid_data(client):
    response = client.post(
        "/inventory",
        json={"name": "Mango Juice"}
    )

    assert response.status_code == 400


def test_update_item(client):
    response = client.patch(
        "/inventory/1",
        json={"stock": 25}
    )

    assert response.status_code == 200
    assert response.get_json()["stock"] == 25


def test_delete_item(client):
    response = client.delete("/inventory/2")

    assert response.status_code == 200
    assert client.get("/inventory/2").status_code == 404


@patch("app.fetch_product")
def test_barcode_lookup(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "1234567890123",
        "name": "Test Product",
        "brand": "Test Brand",
        "ingredients": "Water",
        "image_url": ""
    }

    response = client.get("/products/barcode/1234567890123")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Test Product"
    mock_fetch.assert_called_once_with(barcode="1234567890123")


@patch("app.fetch_product")
def test_import_external_product(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "5555555555555",
        "name": "Imported Product",
        "brand": "Test Brand",
        "ingredients": "Water",
        "image_url": ""
    }

    response = client.post(
        "/products/import",
        json={"barcode": "5555555555555"}
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Imported Product"
    mock_fetch.assert_called_once_with(barcode="5555555555555")


def make_response(status_code=200, payload=None):
    """Build a fake requests response for testing fetch_product."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload or {}

    # Real requests responses raise an error for 4xx/5xx status codes.
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"{status_code} Error"
        )
    else:
        response.raise_for_status.return_value = None

    return response


@patch("app.requests.get")
def test_fetch_product_maps_openfoodfacts_fields(mock_get):
    mock_get.return_value = make_response(200, {
        "status": 1,
        "product": {
            "code": "3017620422003",
            "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, palm oil, hazelnuts",
            "image_front_url": "https://example.com/nutella.jpg"
        }
    })

    product = fetch_product(barcode="3017620422003")

    assert product == {
        "barcode": "3017620422003",
        "name": "Nutella",
        "brand": "Ferrero",
        "ingredients": "Sugar, palm oil, hazelnuts",
        "image_url": "https://example.com/nutella.jpg"
    }


@patch("app.requests.get")
def test_fetch_product_unknown_barcode_returns_none(mock_get):
    mock_get.return_value = make_response(404, {"status": 0})

    assert fetch_product(barcode="0000000000000") is None


@patch("app.requests.get")
def test_barcode_lookup_unknown_barcode_returns_404(mock_get, client):
    mock_get.return_value = make_response(404, {"status": 0})

    response = client.get("/products/barcode/0000000000000")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"

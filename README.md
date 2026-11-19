# Inventory Management System

A Python REST API and command-line inventory management application built with Flask for the Moringa summative lab. Staff can add, view, edit and delete inventory items, and pull real product details from the [OpenFoodFacts API](https://world.openfoodfacts.org/) by barcode or name.

## Features

- Retrieve all inventory items and individual items.
- Create, update (PATCH) and delete inventory items.
- Look up OpenFoodFacts products by barcode or by name.
- Import an external product straight into the inventory.
- Manage the inventory through a menu-driven command-line interface (CLI).
- Input validation with clear JSON error messages.

## Technologies

- Python 3
- Flask
- Requests
- OpenFoodFacts API

## Project structure

```
flask-inventory-api/
├── app.py            # Flask API: routes, validation, OpenFoodFacts calls
├── cli.py            # Command-line interface that talks to the API
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup

Clone the repository and enter the project folder:

```bash
git clone https://github.com/wairimumonicah461-blip/flask-inventory-api.git
cd flask-inventory-api
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows, activate it with `venv\Scripts\activate` instead.

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`. Leave this terminal open.

## Run the CLI

Open a second terminal, activate the virtual environment again, and run:

```bash
python cli.py
```

The API must be running first, otherwise the CLI shows "Could not connect to the API".

```
=== INVENTORY MANAGEMENT SYSTEM ===
1. View all inventory
2. View one item
3. Add item
4. Update item
5. Delete item
6. Search OpenFoodFacts
7. Import external product
0. Exit
Choose an option:
```

| Option | What it does |
|--------|--------------|
| 1 | Lists every item (ID, name, price, stock) |
| 2 | Shows one item by its ID |
| 3 | Adds an item (asks for name, price and stock) |
| 4 | Updates an item; leave a field blank to keep it unchanged |
| 5 | Deletes an item after a yes/no confirmation |
| 6 | Searches OpenFoodFacts by product name |
| 7 | Imports a product from OpenFoodFacts into the inventory, by barcode or name |
| 0 | Exits the program |

Example of option 1:

```
ID: 1 | Name: Organic Almond Milk | Price: 350.0 | Stock: 20
ID: 2 | Name: Whole Wheat Bread | Price: 180.0 | Stock: 15
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Lists the available endpoints |
| GET | `/inventory` | List all items |
| GET | `/inventory/<id>` | Retrieve one item |
| POST | `/inventory` | Create an item |
| PATCH | `/inventory/<id>` | Update an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/products/barcode/<barcode>` | Look up a product on OpenFoodFacts by barcode |
| GET | `/products/search?name=milk` | Search OpenFoodFacts by name (returns the first match) |
| POST | `/products/import` | Import an OpenFoodFacts product into the inventory |

### Item fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | Yes | Must not be empty |
| `price` | number | Yes | Zero or more |
| `stock` | integer | Yes | Zero or more |
| `barcode` | string | No | |
| `brand` | string | No | |
| `ingredients` | string | No | |

The server assigns the `id` automatically.

### Example requests

Create an item:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Mango Juice", "price": 120, "stock": 10}'
```

Update only the stock of item 1:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 25}'
```

Delete item 2:

```bash
curl -X DELETE http://127.0.0.1:5000/inventory/2
```

Look up a product by barcode, search by name, and import one into the inventory:

```bash
curl http://127.0.0.1:5000/products/barcode/3017620422003
curl "http://127.0.0.1:5000/products/search?name=nutella"
curl -X POST http://127.0.0.1:5000/products/import \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3017620422003"}'
```

### Response status codes

| Code | Meaning |
|------|---------|
| 200 | Request succeeded |
| 201 | Item created or imported |
| 400 | Invalid or missing data in the request |
| 404 | Item or product not found (including an unknown barcode) |
| 502 | The OpenFoodFacts API could not be reached or failed |

Errors are returned as JSON, for example `{"error": "Inventory item not found"}`.

## Working with OpenFoodFacts

- Barcode lookups and name searches call the live OpenFoodFacts API, so an internet connection is needed and results can change over time.
- Name searches return only the first matching product.
- OpenFoodFacts has no price or stock data, so imported items are added with a price of `0.0` and a stock of `0`. Use the update (PATCH) option to set them afterwards.

## Data storage

Inventory data is stored in memory for this lab and resets when the Flask application restarts. The API starts with two sample items (Organic Almond Milk and Whole Wheat Bread). In a production system this list would be replaced by a database such as SQLite or PostgreSQL.

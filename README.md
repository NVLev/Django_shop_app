# Django Shop App

This is a Django application for managing products and orders, offering CRUD functionality for both. It also includes user authentication and an API for interacting with the data.

## Installation

### Using Docker Compose

To run the application using Docker Compose, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/NVLev/Django_shop_app.git
    cd Django_shop_app
    ```

2. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```


## Project Structure

```
Django_shop_app/
├── mysite/
│   ├── mysite/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── shopapp/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   └── ...
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Features

- User authentication
- Product management (CRUD)
- Order management (CRUD)
- API for products and orders
- Dockerized setup

## Configuration

The main configuration for the Django project can be found in the `settings.py` file located under `mysite/mysite/`. Key configurations include:

- Installed apps
- Middleware
- Database settings
- Static files settings
- Authentication settings

## Data Models

The data models for the application are defined in the `models.py` file located under `mysite/shopapp/`. Key models include:

- `Product`: Represents a product in the shop.
- `Order`: Represents an order placed by a user.







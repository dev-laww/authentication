# FastAPI Starter Template

This repository provides a starter template for building web applications using FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Project Structure
```
fastapi-starter
├── alembic/           # Database migration tool
├── fastapi_starter/   # Main application package
│   ├── api/           # API route definitions
│   ├── core/          # Core application settings and configurations
│   ├── controllers/   # Request handlers
│   ├── models/        # Database models
│   ├── repositories/  # Data access layer
│   ├── services/      # Business logic layer
│   ├── app.py         # FastAPI application instance
│   ├── __init__.py    # Package initializer
│   └── __main__.py    # Application entry point
├── alembic.ini
├── main.py            # Application launcher
├── poetry.lock
├── pyproject.toml
├── README.md
└── test_main.http
```

# FutureX Investor Management System

This is a Django-based system for managing investor profiles, investments, ROI distributions, and related financial transactions. It includes several modules such as Investor Management, Investments, and Finance (ROI Distribution and Payments).

## Setup

1. Clone the repository and install dependencies.
2. Set up PostgreSQL and configure the credentials in `settings.py`.
3. Run migrations with `python manage.py migrate`.
4. Start the server with `python manage.py runserver`.

## Modules
- Investor Management
- Investment Management
- ROI Distribution and Financial Tracking

## Technologies Used
- Django
- Django REST Framework (DRF)
- PostgreSQL
- Celery (for background tasks)
- Docker (optional for deployment)
    
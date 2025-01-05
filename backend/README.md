# FITOPIA 健身房管理系統

A FastAPI-based gym management system that handles member management, check-ins, memberships, and transactions.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   uvicorn main:app --reload
   ```

4. Access the API documentation:
   ```bash
   http://127.0.0.1:8000/docs
   ```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Available Routes

The API includes the following main routes:

- `/members/` - Member management
- `/products/` - Product management
- `/membership-plans/` - Membership plan management
- `/member-photos/` - Member photo management
- `/membership-status/` - Membership status management
- `/checkin-records/` - Check-in record management
- `/transaction-records/` - Transaction record management

## CORS

The API has CORS middleware enabled and accepts requests from all origins (`*`).

## Development

To modify the application:

1. Routes are organized in separate modules under the `routes` directory
2. Models are defined in the `models` directory
3. Database configurations can be found in `database.py`

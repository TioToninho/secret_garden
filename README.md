<div align="center">
<h1>Secret Garden</h1>
<h3>Property Management System</h3>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frontend: React](https://img.shields.io/badge/Frontend-React-blue.svg)](https://reactjs.org/)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)

</div>

# Secret Garden - Documentation

Secret Garden is a property management system that facilitates the management of clients, properties, monthly calculations, and financial transfers. The application is divided into frontend (React/Vite) and backend (Python/FastAPI).

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Data Storage](#data-storage)
- [API Endpoints](#api-endpoints)
  - [Clients](#clients)
  - [Owners](#owners)
  - [Monthly Calculations](#monthly-calculations)
  - [Transfers](#transfers)
  - [Bank Returns](#bank-returns)
  - [Monthly Variable Values](#monthly-variable-values)
- [Models](#models)
- [Project Structure](#project-structure)

## Overview

Secret Garden is a complete property management solution that allows you to manage clients, owners, monthly calculations, and financial transfers. The system facilitates payment tracking and financial report generation.

## Key Features

- **Client Management**: Registration and management of tenants/clients
- **Owner Management**: Registration and management of property owners
- **Monthly Calculations**: Automation of rent and fee calculations
- **Transfers**: Control of financial transfers between clients and owners
- **Bank Returns**: Processing of bank payment returns
- **Dashboard**: Visualization of metrics and financial indicators

## Installation

### Backend (Python/FastAPI)

1. Enter the backend directory:
   ```
   cd secret_garden_service
   ```

2. Set up the virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -e .
   ```

4. Copy the environment variables example file:
   ```
   cp .env.example .env
   ```

5. Run the development server:
   ```
   uvicorn src.secret_garden.api.main:app --reload
   ```

### Frontend (React/Vite)

1. Enter the frontend directory:
   ```
   cd secret_garden_front
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Copy the environment variables example file:
   ```
   cp .env.example .env
   ```

4. Run the development server:
   ```
   npm run dev
   ```

## Data Storage

| Data Type | Storage Location | Example |
|-----------|------------------|---------|
| Clients | SQLite | Name, address, contact details |
| Owners | SQLite | Name, bank details, tax information |
| Monthly Calculations | SQLite | Rent values, fees, taxes |
| Transfers | SQLite | Transferred values, dates, status |
| Bank Returns | SQLite | Payment confirmations, dates, values |

## API Endpoints

### Clients

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/clients` | List all clients | No |
| GET | `/clients/{id}` | Get client details | No |
| POST | `/clients` | Create new client | No |
| PUT | `/clients/{id}` | Update client | No |
| DELETE | `/clients/{id}` | Remove client | No |

**Request Example:**
```
GET /clients/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "John Smith",
  "address": "123 Flower Street",
  "phone": "(11) 98765-4321",
  "email": "john.smith@email.com",
  "active": true,
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-02-20T14:15:00Z"
}
```

### Owners

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/owners` | List all owners | No |
| GET | `/owners/{id}` | Get owner details | No |
| POST | `/owners` | Create new owner | No |
| PUT | `/owners/{id}` | Update owner | No |
| DELETE | `/owners/{id}` | Remove owner | No |

**Request Example:**
```
GET /owners/2
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Mary Johnson",
  "bank": "Bank of America",
  "account_number": "12345-6",
  "branch": "1234",
  "document": "123.456.789-00",
  "email": "mary.johnson@email.com",
  "phone": "(11) 91234-5678",
  "created_at": "2023-01-10T09:15:00Z",
  "updated_at": "2023-02-15T11:20:00Z"
}
```

### Monthly Calculations

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/monthly-calculations` | List all monthly calculations | No |
| GET | `/monthly-calculations/{id}` | Get monthly calculation details | No |
| POST | `/monthly-calculations` | Create new monthly calculation | No |
| GET | `/monthly-calculations/client/{client_id}` | List client's calculations | No |

**Request Example:**
```
GET /monthly-calculations/client/1
```

**Response Example:**
```json
[
  {
    "id": 10,
    "client_id": 1,
    "month": 3,
    "year": 2023,
    "rent_value": 1500.00,
    "iptu": 150.00,
    "condo_fee": 350.00,
    "total": 2000.00,
    "payment_status": "paid",
    "calculation_date": "2023-03-01T08:00:00Z",
    "payment_date": "2023-03-10T10:45:00Z"
  },
  {
    "id": 22,
    "client_id": 1,
    "month": 4,
    "year": 2023,
    "rent_value": 1500.00,
    "iptu": 150.00,
    "condo_fee": 350.00,
    "total": 2000.00,
    "payment_status": "pending",
    "calculation_date": "2023-04-01T08:00:00Z",
    "payment_date": null
  }
]
```

### Transfers

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/monthly-transfers` | List all transfers | No |
| GET | `/monthly-transfers/month/{month}/year/{year}` | List transfers by month/year | No |
| GET | `/monthly-transfers/owner/{owner_id}` | List owner's transfers | No |

**Request Example:**
```
GET /monthly-transfers/month/3/year/2023
```

**Response Example:**
```json
[
  {
    "id": 5,
    "owner_id": 2,
    "month": 3,
    "year": 2023,
    "value": 1350.00,
    "status": "processed",
    "transfer_date": "2023-03-15T14:30:00Z",
    "properties_count": 2
  },
  {
    "id": 6,
    "owner_id": 3,
    "month": 3,
    "year": 2023,
    "value": 2700.00,
    "status": "processed",
    "transfer_date": "2023-03-15T14:35:00Z",
    "properties_count": 3
  }
]
```

### Bank Returns

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/bank-returns` | List all bank returns | No |
| POST | `/bank-returns` | Register new bank return | No |
| GET | `/bank-returns/client/{client_id}` | List client's bank returns | No |

**Request Example:**
```
POST /bank-returns
Content-Type: application/json

{
  "client_id": 1,
  "value": 2000.00,
  "date": "2023-03-10T10:45:00Z",
  "bank": "Chase",
  "reference": "2023/03"
}
```

**Response Example:**
```json
{
  "id": 42,
  "client_id": 1,
  "value": 2000.00,
  "date": "2023-03-10T10:45:00Z",
  "bank": "Chase",
  "reference": "2023/03",
  "processed": true,
  "created_at": "2023-03-10T10:46:00Z"
}
```

### Monthly Variable Values

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/monthly-variable-values` | List all variable values | No |
| POST | `/monthly-variable-values` | Create new variable value | No |
| GET | `/monthly-variable-values/client/{client_id}` | List client's variable values | No |

**Request Example:**
```
GET /monthly-variable-values/client/1
```

**Response Example:**
```json
[
  {
    "id": 8,
    "client_id": 1,
    "month": 3,
    "year": 2023,
    "description": "Plumbing repair",
    "value": 250.00,
    "type": "expense",
    "created_at": "2023-03-05T16:20:00Z"
  },
  {
    "id": 9,
    "client_id": 1,
    "month": 3,
    "year": 2023,
    "description": "Late payment fee",
    "value": 50.00,
    "type": "income",
    "created_at": "2023-03-11T09:15:00Z"
  }
]
```

## Models

### Main Flow

1. **Client and Owner Registration**
   - Registration of basic client and owner data

2. **Monthly Calculation**
   - Automatic generation of monthly values to be paid by each client

3. **Payment Registration**
   - Processing of bank returns and payment confirmations

4. **Transfer to Owners**
   - Calculation and registration of transfers to owners after fee deduction

5. **Report Generation**
   - Consolidation of data for financial analysis

### Main Models

- **Client**: Tenant or property occupant
- **Owner**: Property owner
- **MonthlyCalculation**: Monthly calculation of values to be paid
- **MonthlyTransfer**: Transfer to owner
- **BankReturn**: Received payment record
- **MonthlyVariableValues**: Variable values such as extra expenses or credits

## Project Structure

```
secret_garden/
├── secret_garden_front/      # Frontend (React/Vite)
│   ├── public/               # Public files
│   │   ├── assets/           # Static resources
│   │   ├── components/       # React components
│   │   ├── pages/            # Application pages
│   │   ├── services/         # API communication services
│   │   └── App.jsx           # Main component
│   ├── package.json          # Dependencies
│   └── vite.config.js        # Vite configuration
│
└── secret_garden_service/    # Backend (FastAPI)
    ├── src/                  # Source code
    │   ├── secret_garden/    # Main package
    │   │   ├── api/          # API and routes
    │   │   ├── database/     # Database configuration and models
    │   │   ├── models/       # Pydantic models
    │   │   └── services/     # Business logic
    │   └── data/             # SQLite database
    ├── scripts/              # Utility scripts
    └── pyproject.toml        # Dependencies
```

## Contributing

1. Fork the repository
2. Clone the fork: `git clone https://github.com/your-username/secret_garden.git`
3. Create a branch for your feature: `git checkout -b feature/new-functionality`
4. Commit your changes: `git commit -am 'Add new functionality'`
5. Push to GitHub: `git push origin feature/new-functionality`
6. Create a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information. 
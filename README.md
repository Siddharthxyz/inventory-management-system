# Simple Inventory Management System

## Objective
To build a basic inventory management system for chemical products that supports
CRUD operations and stock tracking.

## Features
- Add chemical products
- Unique CAS number validation
- Track inventory stock
- Stock IN and OUT operations
- Prevent negative stock
- Inventory list view

## Tech Stack
- Backend: Flask (Python)
- Database: SQLite
- Frontend: HTML

## Database Models

### ChemicalProduct
- id
- name
- cas_number (unique)
- unit (KG / MT / Litre)

### Inventory
- id
- product_id (Foreign Key)
- current_stock

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd inventory_management_system

## Live Demo
🔗 https://inventory-management-system-iqya.onrender.com

⚠️ Note: This app is hosted on Render Free tier.
The first request may take 30–50 seconds to wake up the server.

# Pharmacy Management System (PMS)
**Group 5 - Kaputt Kommandos**  
*CCCS 106 - Application Development and Emerging Technologies*

## Project Overview
The **Kaputt Kommandos PMS** is a modern desktop application designed to streamline daily pharmacy operations. It handles user authentication, inventory tracking, prescription validation, billing, and patient management.

Built using **Python** and **Flet** (Flutter for Python), the system features a responsive, material-design interface with **Dark Mode** support and **Role-Based Access Control (RBAC)**.

---

## The Team
| Name | Role | Responsibility |
| :--- | :--- | :--- |
| **Carl Renz Colico** | Product Owner / PM | Product Lead / Vision & Feature Prioritization, UI/UX & Accessibility Designer |
| **Kenji Nathaniel David** | Product Owner | QA / Test Coordinator, Documentation & Release Manager |
| **Francis Gabriel Nonato** | Program Manager | Lead Developer, UI/UX & Accessibility Designer |

---

## Key Features
*   **Role-Based Security:** Distinct dashboards and permissions for Patients, Admins, Pharmacists, Inventory Managers, Billing Clerks, and Staff.
*   **Adaptive UI:** Fully supported **Dark Mode** and Light Mode with a cohesive Teal theme.
*   **Inventory Management:** Real-time tracking of medicine stock with visual "Low Stock" alerts.
*   **Prescription Handling:** Pharmacists can view pending prescriptions and dispense medication.
*   **Patient Portal:** Patients can sign up, search for medicines, and view their cart.
*   **Billing System:** Generation of invoices and sales tracking.
*   **Local Database:** Powered by **SQLite** for fast, persistent data storage without external servers.

---

## Tech Stack
*   **Language:** Python 3.13.5
*   **GUI Framework:** [Flet](https://flet.dev/) (0.28.3)
*   **Database:** SQLite3
*   **Version Control:** Git & GitHub

---

## Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/frnonato-lgtm/Pharmacy-Management-System.git
cd Pharmacy-Management-System
```

### 2. Set up Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies clean.

**Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\Activate
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
cd src
python main.py
```

*Note: The `pharmacy.db` file will be generated automatically upon the first successful run.*

---

## Login Credentials (Test Accounts)

The database is pre-seeded with these accounts for testing purposes:

| **Role** | **Username** | **Password** | **Features to Test** |
| :---     | :---         | :---         | :---                 |
| **Patient** | `pat` | `pat123` | Search Medicine, Add to Cart |
| **Administrator** | `admin` | `admin123` | User Management, System Overview |
| **Pharmacist** | `pharm` | `pharm123` | Prescription Validation |
| **Inventory Manager** | `inv` | `inv123` | Stock Management, Low Stock Alerts |
| **Billing Clerk** | `bill` | `bill123` | Invoices, Sales Reports |
| **Staff Member** | `staff` | `staff123` | Patient Search |

New users can also create an account using the **"Create Account"** button on the Patient Login page.

---
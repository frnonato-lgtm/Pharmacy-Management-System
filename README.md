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

### 4. Initialize Database (Important!)
You must run the migration script to create the tables and seed the database with the 54 medicines and default users.

1. **Check for old data:** If a `pharmacy.db` file already exists in `src/storage/`, **delete it** to ensure a fresh start.
2. **Run the seed script:**
```bash
python src/services/db_migration.py
```

*You should see the message: "🎉 MIGRATION & SEEDING COMPLETED SUCCESSFULLY!"*

### 5. Run the Application
Once the database is seeded, navigate to the source folder and launch the app:
```bash
cd src
python main.py
```

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

---

Below are screenshots demonstrating overall features of the app:

| Feature | Screenshot |
|----------|-------------|
| **Landing Page** | ![Landing Page](src/assets/landing_page.png) |
| **Patient Log In** | ![Patient Log In](src/assets/patient_login.png) <br>![Patient Log In Page](src/assets/patient_login_page.png) |
| **Patient Create Account** | ![Patient Create Account](src/assets/patient_create_acc.png) | 
| **Admin Login** | ![Admin Login](src/assets/admin_login.png)<br>![Admin Login Page](src/assets/admin_login_page.png) | 
| **Pharmacist Login** | ![Pharmacist Login](src/assets/pharm_login.png)<br>![Pharmacist Login Page](src/assets/pharm_login_page.png) |
| **Inventory Manager Login** | ![Inventory Manager](src/assets/invmng_login.png)<br>![Inventory Manager Login Page](src/assets/invmng_login_page.png) |
| **Billing Clerk Login** | ![Billing Clerk](src/assets/bill_login.png)<br>![Billing Clerk Login Page](src/assets/bill_login_page.png) |
| **Staff Member Login** | ![Staff Member](src/assets/staff_login.png)<br>![Staff Member Login Page](src/assets/staff_login_page.png) |
| **Patient Dashboard** | ![Patient Dashboard](src/assets/patient_dashboard.png) |
| **Admin Dashboard** | ![Admin Dashboard](src/assets/admin_dashboard.png) |
| **Pharmacist Dashboard** | ![Pharmacist Dashboard](src/assets/pharm_dashboard.png) |
| **Inventory Manager Dashboard** | ![Inventory Manager Dashboard](src/assets/invmng_dashboard.png) |
| **Billing Dashboard** | ![Billings Dashboard](src/assets/bill_dashboard.png) |
| **Staff Dashboard** | ![Staff Dashboard](src/assets/staff_dashboard.png) |

---

---

Below are screenshots demonstrating various features of patient manual: 
| Feature | Patient Manual | Screenshot | 
|----------|-------------|-------------| 
| **Patient Browse Medicine** | Allows patients to browse available medicines, view details, and use the search bar to quickly find medicines| ![Browsing Medicine](src/assets/patient_browse_med.png)<br>![Medicine Search Page](src/assets/patient_meds_page.png) | 
| **Upload Prescription** | Enables patients to submit a prescription form for pharmacist before purchasing required medication | ![Upload Prescription](src/assets/patient_upload_presc.png)<br>![Upload Prescription Page](src/assets/patient_prescription_page.png) | 
| **Patient Browse Cart** | Shows all selected medicines in the cart, allowing patients to review, update quantities, or remove items before checkout. | ![Patient Cart](src/assets/patient_view_cart.png)<br>![Patient Cart Page](src/assets/patient_view_cart_page.png) | 
| **Viewing Patient Orders** | Displays a list of all past and current orders, including order status and purchase history also total amount for easy tracking | ![Viewing All Recent Orders](src/assets/patient_view_all)<br>![View All Orders Page](src/assets/patient_view_all_orders_page.png) | 
| **Patient Side-bar Navigation**| Provides easy access to all patient features such as browsing medicine, orders, cart, bills, and profile through a clean navigation menu| ![Patient Side Navigation Bar](src/assets/patient_nav_bar.png) | 
| **Viewing Patient Profile** | Shows the patient’s personal information, including contact details, account profile, as well as logout button and with options for updates | ![Patient Profile](src/assets/patient_profile)<br>![Patient Profile Page](src/assets/patient_profile_page.png) |

---

---

Below are screenshots demonstrating various features of admin manual: 
| Feature | Description | Screenshot | 
|----------|-------------|-------------| 
| **Manage Users** | Allows the admin to view, add, update, and remove system user accounts | ![Manage Users](src/assets/admin_quick_actions.png)<br>![Manage Users Page](src/assets/admin_user_management.png) | 
| **View Reports** | Lets the admin access system-wide reports, including user activity, inventory status, and performance metrics. | ![View All System User Reports](src/assets/admin_quick_actions.png)<br>![System Reports Page](src/assets/admin_system_reports_page.png) | 
| **System Logs** | Enables the admin to monitor all system activity logs for auditing and tracking actions performed by users | ![View All System Activity Logs](src/assets/admin_quick_actions.png)<br>![System Activity Logs Page](src/assets/admin_system_logs_page.png) |
| **View All Recent Logs** | Displays the most recent system activities, providing quick insight into recent updates or changes | ![View Recent Activity](src/assets/admin_view_recent.png) | 
| **Admin Nav Bar** | Provides easy navigation to all admin tools and features through a structured and organized sidebar | ![Admin Navigation Bar](src/assets/admin_nav_bar.png) | 
| **Admin Manage Inventory Stock** | Allows the admin to view, update, and manage available inventory, including adding stock and monitoring low quantities | ![Manage Inventory Stock](src/assets/admin_manage_stock.png) |
| **Admin Alert System Notification** | Shows system notifications and alerts for critical events such as low stock, prescriptions | ![Alert System Notification](src/assets/admin_system_activity.png) |

---

---

Below are screenshots demonstrating various features of pharmacist manual:

| Feature | Description | Screenshot |
|----------|-------------|-------------|
| **Pharmacist Statistics View** | Provides the pharmacist with an overview of key statistics such as prescriptions handled, pending prescriptions,daily activity and available medicines | ![Stats View](src/assets/pharm_stats_card.png) |
| **Review Prescriptions** | Allows the pharmacist to check uploaded prescriptions, validate them, and approve or decline patient requests | ![Review Prescriptions](src/assets/pharm_review_presc.png)<br>![Review Prescriptions Page](src/assets/pharma_review_presc_page.png) |
| **Prescription View** | Displays the full prescription details including patient information, medicine list, and dosage instructions | ![Prescription View](src/assets/pharm_prescription.png) |
| **Search Medicines** | Enables pharmacists to quickly search for medicines in the system, view availability, and check medicine details | ![Search Medicines](src/assets/pharm_search_medicine.png)<br>![Review Prescriptions Page](src/assets/pharm_search_medicine_page.png) |
| **Generate Pharmacist Report** | Allows pharmacists to generate detailed reports on activities, prescriptions processed, and overall performance metrics | ![Generate Report](src/assets/pharm_generate_report.png)<br>![Pharmacist Report Page](src/assets/pharm_generate_report_page.png) |
| **Pharmacist Prescription Preview** | Shows a preview of the prescription of the Patient and view it from there | ![Prescription Review](src/assets/pharm_presc_preview.png) |
| **Pharmacist Log Activity** | Displays a record of all activities performed by the pharmacist for tracking and audit purposes | ![Log Activity](src/assets/pharm_log_activity.png) |
| **Pharmacist Alert Notification** | Shows notifications for important updates such as low stock notification and pending prescription | ![Pharmacist Alert Notification](src/assets/pharm_alert_notification.png) |
| **Pharmacist Side-Navigation Bar** | Provides easy access to all pharmacist tools and sections through a structured navigation sidebar | ![Pharmacist Nav Bar](src/assets/pharm_side_nav.png) |

---

---

Below are screenshots demonstrating various features of inventory manager manual:

| Feature | Description | Screenshot |
|----------|-------------|-------------|
| **Inventory Manager Statistics View** | Displays key inventory statistics, including total stock and low-quantity alerts | ![Stats View](src/assets/invmng_stats_card.png) |
| **Inventory Manager Manage Stock** | Allows the inventory manager to view all medicines, update quantities, restock items, and monitor product availability | ![Manage Stock](src/assets/invmng_manage_stock.png)<br>![Manage Stock Page](src/assets/invmng_stock_management_page.png) |
| **Adding Medicine** | Enables the inventory manager to add new medicines to the system by entering details such as name, price, category, stock quantity,supplier and expiry date | ![Add Medicine](src/assets/invmng_add_medicines.png) |
| **Inventory Manager Side-Navigation Bar** | Provides quick access to all inventory management features through an organized navigation sidebar| ![Inventory Manager Nav Bar](src/assets/invmng_side_nav.png) |

---

---

Below are screenshots demonstrating various features of billing clerk manual:

| Feature | Description | Screenshot |
|----------|-------------|-------------|
| **Billing Clerk Statistics View** | Provides an overview of key billing metrics, including total invoices, payments processed, and recent billing activity | ![Stats View](src/assets/bill_stats_card.png) |
| **Create Invoice** | Allows the billing clerk to generate new invoices by choosing the order or by entering patient details, and other informations | ![Create Invoice](src/assets/bill_create_invoice.png)<br>![Create Invoice Page](src/assets/bill_create_invoice_page.png) |
| **View All Invoices** | Displays a complete list of all issued invoices with filters for searching, sorting, and reviewing billing history | ![View Invoices](src/assets/bill_view_all_invoices.png)<br>![View Invoices Page](src/assets/bill_view_all_invoices_page.png) |
| **Payment History** | Shows all recorded payments, including dates, invoice numbers, payment amounts, and patient information | ![View Payment History](src/assets/bill_payment_history.png)<br>![Payment History Page](src/assets/bill_payment_history_page.png) |
| **Billing Clerk Report** | Enables the billing clerk to generate detailed reports summarizing invoices, payments, and overall billing performance | ![Billing Clerk Report](src/assets/bill_generate_report.png)<br>![Billing Clerk Report Page](src/assets/bill_generate_report_page.png) |
| **Recent Invoices Preview** | Provides a quick preview of the most recent invoices, with options to view full invoice details and other information | ![Billing Preview](src/assets/bill_recent_invoices_preview.png)<br>![Billing Full Invoice Details](src/assets/bill_invoice_full_details.png) |
| **Recent Activity View** | Displays the latest billing-related actions and updates, allowing clerks to monitor recent system activity at a glance| ![Billing Clerk](src/assets/bill_recent_activity.png) |
| **Billing Clerk Side-Navigation** | Offers easy access to all billing tools and sections through a structured side navigation panel | ![Side-Navigation](src/assets/bill_side_nav.png) |

---

---

Below are screenshots demonstrating various features of staff member(s) manual:

| Feature | Description | Screenshot |
|----------|-------------|-------------|
| **Staff Member Statistics View** | Provides an overview of patient-related statistics such as total patients, patient today, and active prescriptions relevant to staff | ![Stats View](src/assets/staff_stats_card.png) |
| **Search Patient** | Allows staff members to quickly search for patient records using keywords(name, contact number), Patient ID numbers, or names | ![Search Patient](src/assets/staff_search_patient.png)<br>![Search Patient Page](src/assets/staff_search_patient_page.png) |
| **View Patient Details-Read Only** | Displays complete patient information in a secure, read-only format to prevent unauthorized editing | ![Stats View](src/assets/staff_patient_detail_view.png) |
| **View All Patient** | Shows a full list of registered patients with options to browse, filter, and review their basic details | ![View All Patient](src/assets/staff_view_all_patient.png)<br>![View All Patient Page](src/assets/staff_view_all_patient_page.png) |
| **Help Desk Online** | Enables staff to respond to patient inquiries or concerns through an online help desk interface | ![Help Desk](src/assets/staff_help_desk.png)<br>![Help Page](src/assets/staff_help_desk_page.png) |
| **Recent Activity Preview** | Displays the latest staff-related activities, offering a quick overview of recent system interactions. | ![Activity Preview](src/assets/staff_recent_activity.png) |
| **Staff Guidelines** | Provides important guidelines and protocols that staff members must follow while using the system | ![Staff Guidelines](src/assets/staff_guidelines.png) |
| **Staff Side-Navigation** | Offers easy access to all staff tools and pages through an organized navigation panel | ![Staff Side Nav](src/assets/staff_side_nav.png) |


---
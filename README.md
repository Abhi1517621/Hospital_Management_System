# CareFlow Enterprise: Hospital Management System

An enterprise-grade, role-based Hospital Management System (HMS) built with Django. 

I built CareFlow because I wanted to move beyond basic CRUD applications and tackle the messy, real-world edge cases of enterprise software. This project does not just store data; it handles concurrent database transactions, enforces strict financial ledgers, manages timezone-aware scheduling, and strictly governs state transitions across four different user roles while providing a seamless UX for the hospital staff.

---

## Project Overview

At its core, CareFlow simulates a living hospital workflow. When a patient books an appointment, the system enforces timezone-aware availability windows. When a doctor writes a prescription or orders lab work, the system locks that data and routes it directly to the pharmacist and lab technician queues. Every single action taken by any staff member is mathematically routed back to a strictly mapped, itemized financial ledger for the patient.

---

## Database Architecture & Entity-Relationship Diagram

To handle the complex relationships between clinical actions and financial billing, the database is highly normalized. 

Because manual documentation rots quickly in agile development, I treated the database architecture as code. The Entity-Relationship (ER) diagram below is rendered dynamically using Mermaid.js. Notice how the base User model extends into specific profiles, and how the Inventory, Clinical, and Ward modules all route their foreign keys directly into the centralized billing tables to enforce strict state management and billing accuracy.

```mermaid
erDiagram
    %% --- CORE IDENTITIES ---
    Users {
        uuid id PK
        string email UK
        string password_hash
        string role "ENUM: Admin, Doctor, Nurse, LabTech, Pharmacist, Patient"
        datetime created_at
        datetime updated_at
        datetime deleted_at "Soft delete"
    }

    StaffProfile {
        uuid user_id PK, FK "References Users.id"
        string specialization
        int clearance_level 
        decimal base_consultation_fee 
    }

    StaffLicenses {
        uuid id PK
        uuid staff_id FK "References StaffProfile.user_id"
        string license_type "e.g., Medical Board, Pharmacy Council"
        string license_number UK
        date expiry_date
    }

    PatientProfile {
        uuid user_id PK, FK "References Users.id"
        string blood_group
        string emergency_contact
    }

    %% --- OPERATIONS & SCHEDULING ---
    Appointments {
        uuid id PK
        uuid patient_id FK
        uuid doctor_id FK
        datetime scheduled_time
        string status "ENUM: Scheduled, In-Progress, Completed, Cancelled"
        text notes
    }

    Beds {
        uuid id PK
        string room_number
        string type "ENUM: ICU, General, etc."
        decimal current_cost_per_day
    }

    Admissions {
        uuid id PK
        uuid patient_id FK
        uuid bed_id FK
        uuid attending_doctor_id FK
        datetime admitted_at
        datetime discharged_at "Nullable"
    }

    MedicalRecords {
        uuid id PK
        uuid appointment_id FK "Nullable. Links record to specific visit"
        uuid patient_id FK
        uuid doctor_id FK
        text diagnosis
        text prescription_notes
        datetime created_at
    }

    %% --- PHARMACY & INVENTORY CONCURRENCY ---
    MedicineInventory {
        uuid id PK
        string name
        string manufacturer
        int current_stock_quantity
        decimal current_unit_price
    }

    InventoryTransactions {
        uuid id PK
        uuid medicine_id FK
        string transaction_type "ENUM: Restock, Dispense, Adjustment"
        int quantity_change "Positive or Negative"
        datetime timestamp
    }

    PrescriptionItems {
        uuid id PK
        uuid medical_record_id FK
        uuid medicine_id FK
        string dosage
        int quantity_dispensed
    }

    %% --- LAB MODULE ---
    LabTestCatalog {
        uuid id PK
        string test_name
        string department
        decimal current_cost
    }

    LabReports {
        uuid id PK
        uuid patient_id FK
        uuid lab_test_id FK
        uuid technician_id FK 
        text result_data
        string status "ENUM: Pending, Completed"
        datetime completed_at
    }

    %% --- THE BILLING ENGINE ---
    Invoices {
        uuid id PK
        uuid patient_id FK
        decimal total_amount
        string status "ENUM: Draft, Unpaid, Paid"
        datetime generated_at
    }

    %% Specific Charge Tables
    ConsultationCharges {
        uuid id PK
        uuid invoice_id FK
        uuid appointment_id FK
        decimal charged_fee 
    }

    PharmacyCharges {
        uuid id PK
        uuid invoice_id FK
        uuid prescription_item_id FK
        decimal charged_unit_price 
    }

    LabCharges {
        uuid id PK
        uuid invoice_id FK
        uuid lab_report_id FK
        decimal charged_cost 
    }

    RoomCharges {
        uuid id PK
        uuid invoice_id FK
        uuid admission_id FK
        int days_billed
        decimal charged_daily_rate 
    }

    %% --- RELATIONSHIPS ---
    Users ||--o| StaffProfile : "extends"
    Users ||--o| PatientProfile : "extends"
    StaffProfile ||--o{ StaffLicenses : "holds"
    
    PatientProfile ||--o{ Appointments : "books"
    StaffProfile ||--o{ Appointments : "conducts"
    Appointments ||--o| MedicalRecords : "results in"
    
    PatientProfile ||--o{ Admissions : "undergoes"
    Beds ||--o{ Admissions : "hosts"
    StaffProfile ||--o{ Admissions : "attends"
    
    PatientProfile ||--o{ MedicalRecords : "owns"
    StaffProfile ||--o{ MedicalRecords : "creates"
    
    MedicalRecords ||--o{ PrescriptionItems : "contains"
    MedicineInventory ||--o{ PrescriptionItems : "dispensed as"
    MedicineInventory ||--o{ InventoryTransactions : "tracks history"
    
    PatientProfile ||--o{ LabReports : "takes"
    LabTestCatalog ||--o{ LabReports : "defines"
    StaffProfile ||--o{ LabReports : "conducts"

    %% Billing Relationships
    PatientProfile ||--o{ Invoices : "receives"
    Invoices ||--o{ ConsultationCharges : "includes"
    Invoices ||--o{ PharmacyCharges : "includes"
    Invoices ||--o{ LabCharges : "includes"
    Invoices ||--o{ RoomCharges : "includes"
    
    Appointments ||--o{ ConsultationCharges : "generates"
    PrescriptionItems ||--o| PharmacyCharges : "generates"
    LabReports ||--o| LabCharges : "generates"
    Admissions ||--o{ RoomCharges : "generates"
```
---

## Technical Highlights


*   **ACID Transactions & Concurrency Locks:** I used Django's `transaction.atomic` and `select_for_update` in the pharmacy dispensing engine. This guarantees that if two pharmacists try to dispense the last remaining bottle of medication at the exact same millisecond, the database row is locked, preventing negative inventory balances.
*   **The Master Ledger Routing:** Initially, unpaid charges were floating and loosely attached to patients. I refactored the database schema to use centralized charge tables. Now, every department routes their specific foreign keys directly to the ledger, generating perfectly isolated, itemized financial records that cannot be duplicated.
*   **The Timezone Trap:** I implemented two-layer validation for appointment booking. The HTML frontend restricts date selection, but the backend parses the incoming strings into timezone-aware datetime objects and mathematically compares them against the server's atomic clock to prevent malicious API POST requests from booking past dates.
*   **Strict Clinical State Machines:** The backend is heavily fortified against edge cases. Doctors cannot double-admit a patient already in a bed, discharged patients cannot be re-discharged, and pharmacists are physically locked out of dispensing more or less medication than the doctor explicitly prescribed in the `PrescriptionItems` table.

---

## System Roles & Workflows

The system uses a custom User model segmented into distinct operational roles. If a user attempts to access a view outside their clearance, they are blocked by a custom role-based access control (RBAC) system.

*   **Patients:** Can book appointments within a strict 3-day rolling window and view itemized ledger entries.
*   **Doctors:** Manage the consultation room, diagnose, prescribe drugs, order lab tests, and admit/discharge patients to the inpatient ward.
*   **Pharmacists:** Monitor the prescription queue and securely dispense inventory.
*   **Lab Technicians:** Receive automated requisitions from the doctor, input bloodwork/test results, and clear the lab queue.

---

## Tech Stack

*   **Backend:** Python, Django, Django ORM
*   **Frontend:** HTML5, CSS3, Django Templates
*   **Documentation:** Mermaid.js (Diagram as Code)
*   **Database:** SQLite (Development) / PostgreSQL-ready (Production)
*   **Architecture:** MVT (Model-View-Template), Atomic Financial Ledgers

---

## How to Run Locally

**1. Clone the repository:**
```bash
git clone https://github.com/Abhi1517621/Hospital_Management_System
cd careflow-hms
```

**2. Set up the virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run database migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Create the master administrator:**
```bash
python manage.py createsuperuser
```

**6. Boot the server:**
```bash
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/` to see the smart routing homepage.

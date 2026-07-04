# CareFlow Enterprise: Hospital Management System

An enterprise-grade, role-based Hospital Management System (HMS) built with Django. 

I built CareFlow because I wanted to move beyond basic CRUD applications and tackle the messy, real-world edge cases of enterprise software. This project doesn't just store data; it handles concurrent database transactions, enforces strict financial ledgers, manages timezone-aware scheduling, and strictly governs state transitions across four different user roles while providing a seamless UX for the hospital staff.

## Project Overview
At its core, CareFlow simulates a living hospital workflow. When a patient books an appointment, the system enforces timezone-aware availability windows. When a doctor writes a prescription or orders lab work, the system locks that data and routes it directly to the pharmacist and lab technician queues. Every single action taken by any staff member is mathematically routed back to a strictly mapped, itemized financial ledger for the patient.

## Database Architecture & ER Diagram
To handle the complex relationships between clinical actions and financial billing, the database is highly normalized. 

Below is the Entity-Relationship (ER) diagram mapping out the core architecture. Notice how the base User model extends into specific profiles, and how the Inventory, Clinical, and Ward modules all route their foreign keys directly into the centralized `LedgerEntries` table to enforce strict state management and billing accuracy.

![CareFlow ER Diagram](image_ad358f.jpg)

## Technical Highlights
If we are discussing this in an interview, these are the architectural challenges and design decisions I can speak to in depth:

* ACID Transactions & Concurrency Locks: 
  I used Django's transaction.atomic and select_for_update in the pharmacy dispensing engine. This guarantees that if two pharmacists try to dispense the last remaining bottle of medication at the exact same millisecond, the database row is locked, preventing negative inventory balances.

* The Master Ledger Routing: 
  Initially, unpaid charges were floating and loosely attached to patients. I refactored the database schema to use a centralized LedgerEntries table (as seen in the ER diagram). Now, every department routes their specific foreign keys (admission_id, consultation_id, prescription_item_id, lab_report_id) directly to the ledger, generating perfectly isolated, itemized financial records that cannot be duplicated.

* The Timezone Trap: 
  I implemented two-layer validation for appointment booking. The HTML5 frontend restricts date selection, but the backend parses the incoming strings into timezone-aware datetime objects and mathematically compares them against the server's atomic clock to prevent malicious API POST requests from booking past dates.

* Strict Clinical State Machines: 
  The backend is heavily fortified against edge cases. Doctors cannot double-admit a patient already in a bed, discharged patients cannot be re-discharged, and pharmacists are physically locked out of dispensing more or less medication than the doctor explicitly prescribed in the PrescriptionItems table.

## System Roles & Workflows
The system uses a custom User model segmented into distinct operational roles. If a user attempts to access a view outside their clearance, they are blocked by a custom role-based access control (RBAC) system.

1. Patients: Can book appointments within a strict 3-day rolling window and view itemized ledger entries.
2. Doctors: Manage the consultation room, diagnose, prescribe drugs, order lab tests, and admit/discharge patients to the inpatient ward.
3. Pharmacists: Monitor the prescription queue and securely dispense inventory.
4. Lab Technicians: Receive automated requisitions from the doctor, input bloodwork/test results, and clear the lab queue.

## Tech Stack
* Backend: Python, Django, Django ORM
* Frontend: HTML5, CSS3, Django Templates
* Database: SQLite (Development) / PostgreSQL-ready (Production)
* Architecture: MVT (Model-View-Template), Atomic Financial Ledgers

## How to Run Locally

1. Clone the repository:
   git clone https://github.com/yourusername/careflow-hms.git
   cd careflow-hms

2. Set up the virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run database migrations:
   python manage.py makemigrations
   python manage.py migrate

5. Create the master administrator:
   python manage.py createsuperuser

6. Boot the server:
   python manage.py runserver

   Navigate to http://127.0.0.1:8000/ to see the smart routing homepage.

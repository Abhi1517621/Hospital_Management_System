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

Realistic Scheduling Flow: I included an Appointments table to map out how a hospital actually works. It sets up a logical chain of events: a patient books a slot, that appointment results in a medical record, and that specific record generates the bill.

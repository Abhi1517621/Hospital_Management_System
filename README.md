Clean Billing Structure: Instead of using one massive ledger table packed with empty (null) columns to track different types of expenses, I broke the billing down into specific tables (like ConsultationCharges and PharmacyCharges). These all roll up cleanly into a main Invoices table, making the database much faster to query and easier to maintain.

Tracking Historical Prices: In a real hospital, if the price of a medicine goes up today, it shouldn't change the bill of a patient who was discharged yesterday. I designed the charge tables to capture and freeze the exact price at the time of the transaction, protecting past financial records from future catalog updates.

Safe Pharmacy Inventory: Managing medicine stock by just updating a single number can cause race conditions if two pharmacists try to dispense the same drug at the exact same millisecond. To fix this, I implemented an InventoryTransactions table. It works like a bank statement, logging every single addition or removal of a drug step-by-step to prevent bugs and keep an accurate audit trail.

Realistic Scheduling Flow: I included an Appointments table to map out how a hospital actually works. It sets up a logical chain of events: a patient books a slot, that appointment results in a medical record, and that specific record generates the bill.

<img width="3582" height="2495" alt="HMS_final" src="https://github.com/user-attachments/assets/55baef40-3bc1-4f1f-8262-d61205dc8bb2" />

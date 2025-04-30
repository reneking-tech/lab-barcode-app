from database import Session, init_db
from models import Chemical, Movement
from barcode_utils import generate_barcode
from datetime import date, timedelta
import os

# Create directories
os.makedirs("static/barcodes", exist_ok=True)
os.makedirs("static/reports", exist_ok=True)

# Initialize DB
init_db()
session = Session()

samples = [
    {
        "chemical_name": "Acetone",
        "article_number": "TEST-ACE-001",
        "batch_number": "BATCH-1001",
        "test_type": "GC-MS",
        "expected_report_date": date.today() + timedelta(days=2),
        "client_name": "client1@example.com",
        "current_location": "GC-MS Room 1",
        "issues": "",
        "report_status": "Not Ready"
    },
    {
        "chemical_name": "Formaldehyde",
        "article_number": "TEST-FOR-002",
        "batch_number": "BATCH-1002",
        "test_type": "Titration",
        "expected_report_date": date.today() + timedelta(days=3),
        "client_name": "client2@example.com",
        "current_location": "Chem Lab 2",
        "issues": "Instrument undergoing calibration",
        "report_status": "Not Ready"
    },
    {
        "chemical_name": "Sodium Hydroxide",
        "article_number": "TEST-NAOH-003",
        "batch_number": "BATCH-1003",
        "test_type": "pH Test",
        "expected_report_date": date.today() - timedelta(days=1),
        "client_name": "client3@example.com",
        "current_location": "Wet Chemistry Bench 1",
        "issues": "",
        "report_status": "Ready",
        "report_file_path": "static/reports/naoh_003_report.pdf"
    }
]

for sample in samples:
    barcode_data = f"{sample['article_number']}-{sample['batch_number']}"
    barcode_filename = barcode_data.replace(" ", "_")
    barcode_path = generate_barcode(barcode_data, barcode_filename)

    chem = Chemical(
        article_number=sample["article_number"],
        batch_number=sample["batch_number"],
        expiry_date=date.today() + timedelta(days=365),
        barcode_path=barcode_path,
        status="in_stock",
        written_off=False,
        reorder_point=5,
        chemical_name=sample["chemical_name"],
        hazard_class="Flammable" if "Acetone" in sample["chemical_name"] else "Corrosive",
        ph="7.0",
        client_name=sample["client_name"],
        test_type=sample["test_type"],
        expected_report_date=sample["expected_report_date"],
        report_status=sample["report_status"],
        report_file_path=sample.get("report_file_path", ""),
        current_location=sample["current_location"],
        issues=sample["issues"]
    )
    session.add(chem)
    session.commit()

    movement = Movement(
        chemical_id=chem.id,
        movement_type="received",
        timestamp=date.today()
    )
    session.add(movement)

session.commit()
session.close()

print("✅ Dummy data created for client portal testing.")

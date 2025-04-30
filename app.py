# app.py

from database import init_db, Session
from models import Chemical, Movement
from barcode_utils import generate_barcode
from datetime import date, timedelta
import random

def seed_test_chemicals(n=20):
    session = Session()

    articles = ["MERCK", "SIGMA", "BIO", "CHEM"]
    chemicals = [
        ("Acetone", "Flammable", "7.0"),
        ("Sodium Hydroxide", "Corrosive", "14"),
        ("Hydrochloric Acid", "Corrosive", "1"),
        ("Ethanol", "Flammable", "7.2"),
        ("Potassium Permanganate", "Oxidizer", "7"),
        ("Ammonium Nitrate", "Explosive", "5.5"),
        ("Formaldehyde", "Toxic", "3.5"),
        ("Phenol", "Toxic", "6.0"),
    ]

    for i in range(n):
        name, hazard, ph = random.choice(chemicals)
        article = f"{random.choice(articles)}-{name[:3].upper()}-{i+1:03d}"
        batch = f"BATCH-{random.randint(1000,9999)}"
        expiry = date.today() + timedelta(days=random.randint(-60, 365))
        barcode_data = f"{article}-{batch}"
        barcode_filename = barcode_data.replace(" ", "_")
        barcode_path = generate_barcode(barcode_data, barcode_filename)

        chem = Chemical(
            article_number=article,
            batch_number=batch,
            expiry_date=expiry,
            barcode_path=barcode_path,
            status="in_stock",
            written_off=False,
            reorder_point=random.randint(3, 10),
            chemical_name=name,
            hazard_class=hazard,
            ph=ph
        )
        session.add(chem)
        session.commit()

        move = Movement(
            chemical_id=chem.id,
            movement_type="received",
            timestamp=date.today() - timedelta(days=random.randint(0, 10))
        )
        session.add(move)

    session.commit()
    session.close()
    print(f"✅ Seeded {n} realistic test chemicals.")

if __name__ == '__main__':
    init_db()
    seed_test_chemicals(20)

# models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Chemical(Base):
    __tablename__ = 'chemicals'

    id = Column(Integer, primary_key=True)
    article_number = Column(String, nullable=False)
    batch_number = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=False)
    barcode_path = Column(String)
    status = Column(String, default='in_stock')
    written_off = Column(Boolean, default=False)
    reorder_point = Column(Integer, default=5)
    chemical_name = Column(String, nullable=False)
    hazard_class = Column(String, nullable=True)
    ph = Column(String, nullable=True)

    # New fields for client-facing dashboard
    client_name = Column(String, nullable=True)
    test_type = Column(String, nullable=True)
    expected_report_date = Column(Date, nullable=True)
    report_status = Column(String, default='Not Ready')
    report_file_path = Column(String, nullable=True)
    current_location = Column(String, nullable=True)
    issues = Column(String, nullable=True)

    movements = relationship("Movement", back_populates="chemical")

class Movement(Base):
    __tablename__ = 'movements'

    id = Column(Integer, primary_key=True)
    chemical_id = Column(Integer, ForeignKey('chemicals.id'), nullable=False)
    movement_type = Column(String, nullable=False)
    timestamp = Column(Date, nullable=False)

    chemical = relationship("Chemical", back_populates="movements")
# print_labels.py

import streamlit as st
from database import Session
from models import Chemical
import os

# --- Page Config ---
st.set_page_config(page_title="Printable Barcode Labels", layout="wide")
st.title("🖨️ Printable Barcode Label Sheet")

# --- Load Chemicals from DB ---
session = Session()
chemicals = session.query(Chemical).all()

if not chemicals:
    st.warning("⚠️ No chemicals available to print.")
    st.stop()

# --- User Inputs ---
cols_per_row = st.selectbox("Labels per row", [2, 3, 4], index=1)

num_labels = st.slider("How many labels to print?", min_value=1, max_value=len(chemicals), value=10)

# --- Choose Chemicals to Print ---
selected_chems = chemicals[:num_labels]

# --- Arrange Labels in Rows ---
rows = [selected_chems[i:i+cols_per_row] for i in range(0, len(selected_chems), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for col, chem in zip(cols, row):
        label_text = f"""
**{chem.chemical_name}**

Article: `{chem.article_number}`  
Batch: `{chem.batch_number}`  
Expiry: `{chem.expiry_date}`  
Hazard: `{chem.hazard_class}`  
pH: `{chem.ph}`
"""
        if os.path.exists(chem.barcode_path):
            with col:
                st.image(chem.barcode_path, width=180)
                st.markdown(label_text)
        else:
            with col:
                st.warning("⚠️ Barcode not found.")

# --- Close DB Session ---
session.close()

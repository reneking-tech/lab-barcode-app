# dashboard.py

import streamlit as st
from database import Session
from models import Chemical, Movement
from barcode_utils import generate_barcode
import pandas as pd
from datetime import date
import os
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Bionexa Lab Chemical Dashboard", layout="wide")
st.title("🔬 Bionexa Lab Chemical Dashboard")

# --- Database Setup ---
session = Session()
chemicals = session.query(Chemical).all()

# --- Convert DB Records to Dicts ---
data = []
today = date.today()

for chem in chemicals:
    days_to_expiry = (chem.expiry_date - today).days
    expiry_status = (
        "Expired" if days_to_expiry < 0 else
        "Expiring Soon" if days_to_expiry <= 30 else
        "Valid"
    )
    data.append({
        "ID": chem.id,
        "Chemical Name": chem.chemical_name,
        "Article Number": chem.article_number,
        "Batch Number": chem.batch_number,
        "Expiry Date": chem.expiry_date,
        "Days to Expiry": days_to_expiry,
        "Expiry Status": expiry_status,
        "Status": chem.status,
        "Written Off": "Yes" if chem.written_off else "No",
        "Hazard Class": chem.hazard_class,
        "pH": chem.ph,
        "Barcode Path": chem.barcode_path,
        "Reorder Point": chem.reorder_point
    })

df = pd.DataFrame(data)

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filters")

if not df.empty:
    status_options = df["Status"].unique().tolist()
    selected_status = st.sidebar.multiselect("Status", status_options, default=status_options)

    expiry_status_options = df["Expiry Status"].unique().tolist()
    selected_expiry_status = st.sidebar.multiselect("Expiry Status", expiry_status_options, default=expiry_status_options)

    hazard_options = df["Hazard Class"].dropna().unique().tolist()
    selected_hazards = st.sidebar.multiselect("Hazard Class", hazard_options, default=hazard_options)

    filtered_df = df[
        (df["Status"].isin(selected_status)) &
        (df["Expiry Status"].isin(selected_expiry_status)) &
        (df["Hazard Class"].isin(selected_hazards))
    ]
else:
    st.sidebar.warning("⚠️ No chemicals yet — please receive chemicals first.")
    filtered_df = df

# --- Expiry Summary ---
st.sidebar.markdown("### ⏰ Expiry Summary")
if not df.empty:
    st.sidebar.dataframe(df["Expiry Status"].value_counts().reset_index().rename(columns={"index": "Status", "Expiry Status": "Count"}))

# --- Reorder Alerts ---
st.sidebar.header("🛒 Reorder Alerts")
if not df.empty:
    reorder_alerts = df[df["Status"] == "in_stock"].groupby(["Chemical Name"]).size()
    low_stock = reorder_alerts[reorder_alerts <= 5]
    if not low_stock.empty:
        st.sidebar.error(f"⚠️ Low Stock Alert:\n\n{low_stock}")
    else:
        st.sidebar.success("✅ All items sufficiently stocked.")

# --- Main Display Table ---
st.markdown("### 📦 Filtered Chemicals")

def color_expiry(val):
    if val == "Expired":
        return 'background-color: #ff4d4d'
    elif val == "Expiring Soon":
        return 'background-color: #ffe066'
    else:
        return ''

if not filtered_df.empty:
    st.dataframe(
        filtered_df.style.applymap(color_expiry, subset=["Expiry Status"]),
        use_container_width=True
    )
else:
    st.warning("No chemicals match the current filters.")

# --- Barcode Preview ---
st.markdown("### 🖼️ Barcode Preview (First 3 Rows)")

for i, row in filtered_df.head(3).iterrows():
    st.markdown(f"**{row['Chemical Name']} – {row['Article Number']} – {row['Batch Number']}**")
    
    # Show the exact path being checked
    st.text(f"🔎 Looking for: {row['Barcode Path']}")

    # Show image if it exists
    if os.path.exists(row["Barcode Path"]):
        st.image(row["Barcode Path"], width=300)
    else:
        st.warning("⚠️ Barcode image not found.")

    st.markdown("---")


# --- Receive New Chemical Form ---
st.markdown("## ➕ Receive New Chemical")

with st.form("receive_chemical_form"):
    chemical_name = st.text_input("Chemical Name")
    article_number = st.text_input("Article Number")
    batch_number = st.text_input("Batch Number")
    expiry_date = st.date_input("Expiry Date")
    hazard_class = st.text_input("Hazard Class")
    ph = st.text_input("pH Value")
    reorder_point = st.number_input("Reorder Point (Minimum Stock Level)", min_value=1, value=5)

    submitted = st.form_submit_button("Receive Chemical")

    if submitted:
        if not article_number or not batch_number or not chemical_name:
            st.warning("⚠️ Please fill in all required fields.")
        else:
            barcode_data = f"{article_number}-{batch_number}"
            barcode_filename = barcode_data.replace(" ", "_")
            barcode_path = generate_barcode(barcode_data, barcode_filename)

            new_chemical = Chemical(
                article_number=article_number,
                batch_number=batch_number,
                expiry_date=expiry_date,
                barcode_path=barcode_path,
                status="in_stock",
                written_off=False,
                reorder_point=reorder_point,
                chemical_name=chemical_name,
                hazard_class=hazard_class,
                ph=ph
            )

            session = Session()
            session.add(new_chemical)
            session.commit()

            received_movement = Movement(
                chemical_id=new_chemical.id,
                movement_type="received",
                timestamp=date.today()
            )
            session.add(received_movement)
            session.commit()
            session.close()

            st.success(f"✅ Received and recorded chemical: {chemical_name} ({article_number})")
            st.rerun()

# --- Dispatch Chemical Form ---
st.markdown("## ➡️ Dispatch Chemical (Scan or Type Barcode)")

with st.form("dispatch_chemical_form"):
    barcode_input = st.text_input("Scan or Enter Barcode (Article Number-Batch Number)")
    dispatch_submit = st.form_submit_button("Dispatch Chemical")

    if dispatch_submit:
        if not barcode_input:
            st.warning("⚠️ Please scan or enter a barcode.")
        else:
            session = Session()
            chemicals = session.query(Chemical).all()

            matching_chemical = None
            for chem in chemicals:
                expected_barcode = f"{chem.article_number}-{chem.batch_number}"
                if barcode_input.strip() == expected_barcode:
                    matching_chemical = chem
                    break

            if matching_chemical:
                if matching_chemical.status == "dispatched":
                    st.error("⚠️ Chemical already dispatched.")
                else:
                    matching_chemical.status = "dispatched"
                    session.commit()

                    dispatch_movement = Movement(
                        chemical_id=matching_chemical.id,
                        movement_type="dispatched",
                        timestamp=date.today()
                    )
                    session.add(dispatch_movement)
                    session.commit()
                    session.close()

                    st.success(f"✅ Dispatched chemical: {matching_chemical.chemical_name}")
                    st.rerun()
            else:
                st.error("❌ No matching chemical found.")

# --- Movement History ---
st.markdown("## 📜 Movement History")

movements = session.query(Movement).all()

movement_data = [{
    "Chemical ID": m.chemical_id,
    "Movement Type": m.movement_type,
    "Timestamp": m.timestamp
} for m in movements]

movements_df = pd.DataFrame(movement_data)

if not movements_df.empty:
    st.dataframe(movements_df, use_container_width=True)
else:
    st.info("No movement records yet.")

# --- Analytics Dashboard ---
st.markdown("## 📊 Analytics Overview")

if not df.empty:
    # --- Stock Levels by Chemical Name ---
    st.markdown("### Stock Levels by Chemical")
    stock_levels = df[df["Status"] == "in_stock"]["Chemical Name"].value_counts().reset_index()
    stock_levels.columns = ["Chemical Name", "Count"]
    st.dataframe(stock_levels, use_container_width=True)

    # --- Hazard Class Breakdown ---
    st.markdown("### Chemicals by Hazard Class")
    hazard_counts = df["Hazard Class"].dropna().value_counts().reset_index()
    hazard_counts.columns = ["Hazard Class", "Count"]
    st.bar_chart(hazard_counts.set_index("Hazard Class"), use_container_width=True)

    # --- Toggle Chart Type for Status ---
    st.markdown("### Chemicals by Status")
    chart_type = st.radio("Select chart type:", ["Bar Chart", "Pie Chart"], horizontal=True)

    status_chart = df["Status"].value_counts().reset_index()
    status_chart.columns = ["Status", "Count"]

    if chart_type == "Bar Chart":
        st.bar_chart(data=status_chart.set_index("Status"), use_container_width=True)
    else:
        pie_chart = px.pie(status_chart, names="Status", values="Count", title="Chemical Status Distribution")
        st.plotly_chart(pie_chart, use_container_width=True)

    # --- Expiry by Month ---
    st.markdown("### Chemicals by Expiry Month")
    df["Expiry Month"] = df["Expiry Date"].apply(lambda x: x.strftime("%Y-%m") if pd.notnull(x) else None)
    expiry_chart = df["Expiry Month"].value_counts().sort_index().reset_index()
    expiry_chart.columns = ["Month", "Count"]
    st.line_chart(data=expiry_chart.set_index("Month"), use_container_width=True)
else:
    st.info("No data available for analytics yet.")

# --- CSV Export ---
st.markdown("## ⬇️ Download Chemicals Table")

if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Chemicals as CSV",
        data=csv,
        file_name='chemicals_export.csv',
        mime='text/csv',
    )

# --- Close Session ---
session.close()

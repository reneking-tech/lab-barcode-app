# client_portal.py

import streamlit as st
from database import Session
from models import Chemical
from datetime import date
import os

st.set_page_config(page_title="Client Portal - Test Status", layout="centered")
st.title("🧪 Bionexa Client Portal")
st.markdown("Enter your **Sample ID** *or* **Email** below to track the status of your chemical test.")

col1, col2 = st.columns(2)
sample_id = col1.text_input("🔍 Sample ID (e.g. TEST-202504001)")
email = col2.text_input("✉️ Client Email")

session = Session()
chemical = None

if sample_id:
    chemical = session.query(Chemical).filter(
        (Chemical.article_number + '-' + Chemical.batch_number) == sample_id
    ).first()
elif email:
    chemical = session.query(Chemical).filter(Chemical.client_name.ilike(f"%{email}%")).order_by(Chemical.id.desc()).first()

if sample_id or email:
    if chemical:
        st.success(f"✅ Test found for: **{chemical.chemical_name}**")

        st.markdown(f"**Test Type:** {chemical.test_type or 'Not specified'}")
        st.markdown(f"**Status:** {chemical.status.title()}")
        st.markdown(f"**Expected Report Date:** {chemical.expected_report_date or 'TBD'}")
        st.markdown(f"**Ready for Collection:** {'✅ Yes' if chemical.report_status == 'Ready' else '❌ No'}")

        st.markdown(f"**Current Location:** {chemical.current_location or 'Not yet assigned'}")

        if chemical.issues:
            st.error(f"⚠️ Issue: {chemical.issues}")
        else:
            st.success("No current issues reported.")

        if chemical.report_status == "Ready" and chemical.report_file_path and os.path.exists(chemical.report_file_path):
            with open(chemical.report_file_path, "rb") as file:
                st.download_button(
                    label="⬇️ Download Report",
                    data=file,
                    file_name=os.path.basename(chemical.report_file_path),
                    mime="application/pdf"
                )
        else:
            st.info("Report not yet available.")
    else:
        st.error("❌ No test found for that Sample ID or Email.")

session.close()

# Admin tool for uploading final report (visible only with admin checkbox)
st.markdown("---")
st.markdown("### 🧪 Lab Staff Only")

if st.checkbox("I am a lab staff member (show upload tool)"):
    with st.form("upload_form"):
        up_sample_id = st.text_input("Sample ID (article-batch)")
        uploaded_file = st.file_uploader("Upload PDF Report", type="pdf")
        submit = st.form_submit_button("Upload Report")

        if submit and up_sample_id and uploaded_file:
            chem = session.query(Chemical).filter(
                (Chemical.article_number + '-' + Chemical.batch_number) == up_sample_id
            ).first()
            if chem:
                save_path = os.path.join("static", "reports")
                os.makedirs(save_path, exist_ok=True)
                file_path = os.path.join(save_path, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                chem.report_file_path = file_path
                chem.report_status = "Ready"
                session.commit()
                st.success("✅ Report uploaded and client will now see download link.")
            else:
                st.error("❌ No chemical found for that Sample ID.")

session.close()
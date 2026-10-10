"""Streamlit User Interface for University Student Services Assistant.

Provides an interactive portal for students to ask questions, view policies,
and check eligibility against university rules.
"""

import streamlit as st
import requests
import os

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="University Student Services Assistant",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 University Student Services Assistant")
st.caption("AI-Powered Advising, Policy Search & Rule-Based Eligibility")

# Sidebar for connection status and settings
with st.sidebar:
    st.header("System Status")
    
    # Check backend API health
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code == 200:
            health_data = response.json()
            st.success(f"Backend Connected ({health_data.get('status')})")
            st.caption(f"API Version: {health_data.get('version')}")
        else:
            st.warning(f"Backend status: {response.status_code}")
    except requests.exceptions.RequestException:
        st.error("Backend Disconnected")
        st.caption(f"Target: {BACKEND_URL}")

    st.divider()
    st.subheader("Student Identity")
    student_id = st.text_input("Student ID (optional)", placeholder="e.g. S1001")

# Main content area
st.info("👋 Welcome! Ask questions about university policies, degree requirements, or financial aid.")

user_query = st.text_input("Your Question:", placeholder="e.g., What is the minimum GPA required for academic honors?")

if st.button("Submit Question", type="primary"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        st.write(f"**Submitted Question:** {user_query}")
        if student_id:
            st.write(f"**Student ID:** {student_id}")
        st.info("Workflow orchestration and RAG retrieval will be connected in subsequent phases.")

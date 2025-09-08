import streamlit as st

st.set_page_config(page_title="EcoCritique Diagnostic", page_icon="🔧")

st.title("🔧 EcoCritique Diagnostic Mode")
st.write("App is loading! This proves Streamlit is working.")

# Test imports one by one
st.header("Testing Imports...")

try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except Exception as e:
    st.error(f"❌ pandas import failed: {e}")

try:
    import plotly
    st.success("✅ plotly imported successfully")
except Exception as e:
    st.error(f"❌ plotly import failed: {e}")

try:
    import PyPDF2
    st.success("✅ PyPDF2 imported successfully")
except Exception as e:
    st.error(f"❌ PyPDF2 import failed: {e}")

try:
    import requests
    st.success("✅ requests imported successfully")
except Exception as e:
    st.error(f"❌ requests import failed: {e}")

try:
    import openpyxl
    st.success("✅ openpyxl imported successfully")
except Exception as e:
    st.error(f"❌ openpyxl import failed: {e}")

try:
    import docx
    st.success("✅ python-docx imported successfully")
except Exception as e:
    st.error(f"❌ python-docx import failed: {e}")

try:
    import altair
    st.success("✅ altair imported successfully")
except Exception as e:
    st.error(f"❌ altair import failed: {e}")

st.header("Testing Component Imports...")

try:
    from components.auth import initialize_auth
    st.success("✅ auth component imported successfully")
except Exception as e:
    st.error(f"❌ auth component import failed: {e}")

try:
    from components.database_init import initialize_database as init_all_tables
    st.success("✅ database_init component imported successfully")
except Exception as e:
    st.error(f"❌ database_init component import failed: {e}")

st.header("System Information")
import sys
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

st.success("🎉 If you see this, basic Streamlit functionality is working!")

import streamlit as st
import os
import sys
import traceback

st.set_page_config(page_title="EcoCritique Debug", page_icon="🔧")

st.title("🔧 EcoCritique Debug Mode")

# Test 1: Basic functionality
st.success("✅ Streamlit is working!")
st.write(f"Python version: {sys.version}")

# Test 2: File system
st.header("File System Check")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Files in current directory: {os.listdir('.')}")

# Check if data directory exists
if os.path.exists('data'):
    st.success("✅ Data directory exists")
    st.write(f"Files in data directory: {os.listdir('data')}")
else:
    st.error("❌ Data directory not found!")

# Test 3: Import components
st.header("Component Import Test")

try:
    from components.auth import initialize_auth
    st.success("✅ Auth component imported")
except Exception as e:
    st.error(f"❌ Auth import failed: {e}")
    st.code(traceback.format_exc())

try:
    from components.database_init import initialize_database as init_all_tables
    st.success("✅ Database init component imported")
    
    # Try to initialize database
    st.write("Attempting database initialization...")
    init_all_tables()
    st.success("✅ Database initialized successfully!")
except Exception as e:
    st.error(f"❌ Database initialization failed: {e}")
    st.code(traceback.format_exc())

# Test 4: Check for critical files
st.header("Critical Files Check")
critical_files = [
    'data/landscape_ecology_kb.txt',
    'data/socratic_prompts.json',
    'components/database.py',
    'components/chat_engine.py'
]

for file in critical_files:
    if os.path.exists(file):
        st.success(f"✅ {file} exists")
    else:
        st.error(f"❌ {file} NOT FOUND")

st.balloons()
st.success("🎉 Debug complete! Check errors above.")

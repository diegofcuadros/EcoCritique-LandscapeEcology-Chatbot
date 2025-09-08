import streamlit as st

st.write("Hello World - EcoCritique is starting!")
st.write("If you see this message, Streamlit is working correctly.")

# Test basic imports
try:
    import pandas as pd
    st.success("pandas imported OK")
except Exception as e:
    st.error(f"pandas error: {e}")

try:
    import os
    st.write(f"Current directory: {os.getcwd()}")
    st.write(f"Files in data folder: {os.listdir('data') if os.path.exists('data') else 'data folder not found'}")
except Exception as e:
    st.error(f"File system error: {e}")
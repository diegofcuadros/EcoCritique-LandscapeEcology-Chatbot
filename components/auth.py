import streamlit as st
import hashlib
import os
from datetime import datetime, timedelta

def initialize_auth():
    """Initialize authentication system with default credentials"""
    if 'auth_initialized' not in st.session_state:
        # Default professor credentials (should be changed in production)
        st.session_state.professor_credentials = {
            'admin': hashlib.sha256('landscape2024'.encode()).hexdigest()
        }
        
        # Weekly access codes (professor sets these)
        st.session_state.weekly_codes = {
            'current': 'week1_2024',
            'expires': datetime.now() + timedelta(days=7)
        }
        
        # Student roster (can be loaded from file)
        st.session_state.student_roster = set()
        
        st.session_state.auth_initialized = True

def check_authentication(user_type, user_id, access_code):
    """Verify user credentials based on role"""
    
    if user_type == "Guest":
        return True
    
    elif user_type == "Student":
        # Check if student ID format is valid
        if not user_id or len(user_id) < 6:
            return False
            
        # Check weekly access code
        current_code = st.session_state.weekly_codes.get('current', '')
        if access_code != current_code:
            return False
            
        # Add student to roster if not present
        st.session_state.student_roster.add(user_id)
        return True
    
    elif user_type == "Professor":
        # Check professor credentials
        if user_id in st.session_state.professor_credentials:
            stored_hash = st.session_state.professor_credentials[user_id]
            provided_hash = hashlib.sha256(access_code.encode()).hexdigest()
            return stored_hash == provided_hash
        return False
    
    return False

def update_weekly_code(new_code):
    """Update the weekly access code (professor function)"""
    st.session_state.weekly_codes = {
        'current': new_code,
        'expires': datetime.now() + timedelta(days=7)
    }

def add_professor_account(username, password):
    """Add a new professor account"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    st.session_state.professor_credentials[username] = password_hash

def get_student_roster():
    """Get list of registered students"""
    return list(st.session_state.student_roster)

def is_authenticated():
    """Check if current session is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get current user information"""
    return {
        'type': st.session_state.get('user_type', 'Guest'),
        'id': st.session_state.get('user_id', 'Unknown')
    }

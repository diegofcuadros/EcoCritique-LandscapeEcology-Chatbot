import streamlit as st
import os
import sys
from components.auth import initialize_auth, check_authentication
from components.database_init import initialize_database as init_all_tables

# Page configuration
st.set_page_config(
    page_title="Landscape Ecology Chatbot",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .course-info {
        text-align: center;
        color: #2E8B57;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .university-info {
        text-align: center;
        color: #2E8B57;
        font-size: 1.0rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .info-box {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    try:
        # Initialize database and authentication
        init_all_tables()  # This function correctly ensures all tables exist with the right schema.
        initialize_auth()
        
        # Quick database health check (only show to professors)
        if st.session_state.get('user_type') == 'Professor':
            from components.database_init import check_database_health
            is_healthy, message = check_database_health()
            if not is_healthy:
                st.error(f"Database issue: {message}")
            else:
                st.caption(f"✅ Database: {message}")
        
        # Main header
        st.markdown('<h1 class="main-header">🌿 Landscape Ecology Chatbot</h1>', unsafe_allow_html=True)
        st.markdown('<p class="course-info">GEOG/EVST 5015C/6015C</p>', unsafe_allow_html=True)
        st.markdown('<p class="university-info">University of Cincinnati</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">An AI-powered learning companion for critical article analysis</p>', unsafe_allow_html=True)
        
        # Check if user is authenticated
        if 'authenticated' not in st.session_state or not st.session_state.authenticated:
            show_login_page()
        else:
            show_main_interface()

    except Exception as e:
        # This block will catch any error during startup and print it to the logs.
        st.error(f"A critical error occurred on startup: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)

def show_login_page():
    st.markdown("### Welcome to the Landscape Ecology Learning Platform")
    
    with st.container():
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **How to use this system:**
        1. **Students**: Use your student ID to access weekly article discussions
        2. **Professor**: Use your instructor credentials to manage content and view interactions
        3. **Guest**: Explore the demo mode with sample content
        
        This AI chatbot uses Socratic questioning to guide you through critical analysis of 
        landscape ecology articles without providing direct answers.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Authentication form
    with st.form("login_form"):
        st.markdown("#### Login to Continue")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_type = st.selectbox(
                "Select your role:",
                ["Student", "Professor", "Guest"],
                help="Choose your role to access appropriate features"
            )
            
            if user_type == "Student":
                user_id = st.text_input(
                    "Student ID:",
                    placeholder="Enter your student ID (e.g., ST123456)",
                    help="Use the student ID provided by your instructor"
                )
                access_code = st.text_input(
                    "Weekly Access Code:",
                    placeholder="Enter this week's access code",
                    help="Get the access code from your instructor or Canvas"
                )
            elif user_type == "Professor":
                user_id = st.text_input(
                    "Instructor Username:",
                    placeholder="Enter your instructor username"
                )
                access_code = st.text_input(
                    "Password:",
                    type="password",
                    placeholder="Enter your password"
                )
            else:  # Guest
                user_id = "guest_user"
                access_code = "demo"
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if check_authentication(user_type, user_id, access_code):
                st.session_state.authenticated = True
                st.session_state.user_type = user_type
                st.session_state.user_id = user_id
                st.success(f"Welcome, {user_type}!")
                st.rerun()
            else:
                # Show helpful error messages
                if user_type == "Student":
                    st.error("Please check your Student ID (at least 3 characters) and Access Code ('week1_2024')")
                elif user_type == "Professor":
                    st.error("Please check your username ('admin') and password ('landscape2024')")
                else:
                    st.error("Invalid credentials. Please check your information and try again.")

def show_main_interface():
    user_type = st.session_state.get('user_type', 'Guest')
    user_id = st.session_state.get('user_id', 'Unknown')
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"**Logged in as:** {user_type}")
        st.markdown(f"**User ID:** {user_id}")
        
        # Logout button
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # Navigation based on user type
        if user_type == "Student" or user_type == "Guest":
            st.markdown("### Navigation")
            st.markdown("- 📖 **Student Chat**: Discuss weekly articles")
            if user_type == "Guest":
                st.markdown("- 🎯 Demo mode with sample content")
        
        elif user_type == "Professor":
            st.markdown("### Professor Tools")
            st.markdown("- 📊 **Dashboard**: View student interactions")
            st.markdown("- 📤 **Upload**: Add weekly articles")
            st.markdown("- ⚙️ **Settings**: Manage course content")
    
    # Main content area
    if user_type == "Student" or user_type == "Guest":
        st.markdown("### 📖 Article Discussion")
        st.markdown("Navigate to the **Student Chat** page to begin your article analysis session.")
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("""
            **What to expect in your chat session:**
            
            🔍 **Guided Discovery**: The AI will ask questions to help you discover insights yourself
            
            🎯 **No Direct Answers**: You'll be guided to think critically rather than given solutions
            
            📈 **Progressive Difficulty**: Questions will deepen as you demonstrate understanding
            
            ⏱️ **Tracked Progress**: Your engagement and insights are logged for assessment
            
            💡 **Socratic Method**: Learn through questioning and self-discovery
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif user_type == "Professor":
        st.markdown("### 🎓 Professor Dashboard")
        st.markdown("Use the navigation pages to manage your course and view student progress.")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Students", "0", help="Students who have accessed the system this week")
        
        with col2:
            st.metric("Average Session Time", "0 min", help="Average time students spend in discussion")
        
        with col3:
            st.metric("Articles Uploaded", "0", help="Number of articles available for discussion")

if __name__ == "__main__":
    main()

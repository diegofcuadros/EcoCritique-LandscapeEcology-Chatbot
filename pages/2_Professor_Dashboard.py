import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from components.auth import is_authenticated, get_current_user
from components.database import get_student_analytics, get_chat_sessions, get_chat_messages, export_interactions_csv

st.set_page_config(page_title="Professor Dashboard", page_icon="📊", layout="wide")

def main():
    st.title("📊 Professor Dashboard")
    
    if not is_authenticated():
        st.error("Please log in from the main page to access the dashboard.")
        st.stop()
    
    user = get_current_user()
    if user['type'] != 'Professor':
        st.error("This page is only accessible to professors.")
        st.stop()
    
    # Main dashboard layout
    display_overview_metrics()
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analytics", "👥 Student Sessions", "💬 Chat Transcripts", "📥 Export Data"])
    
    with tab1:
        display_analytics_charts()
    
    with tab2:
        display_student_sessions()
    
    with tab3:
        display_chat_transcripts()
    
    with tab4:
        display_export_options()

def display_overview_metrics():
    """Display key metrics overview"""
    st.markdown("### 📊 Course Overview")
    
    analytics = get_student_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Students",
            analytics['total_students'],
            help="Number of unique students who have used the system"
        )
    
    with col2:
        st.metric(
            "Active This Week",
            analytics['active_students'],
            help="Students who have had sessions in the last 7 days"
        )
    
    with col3:
        st.metric(
            "Avg Session Time",
            f"{analytics['avg_duration']} min",
            help="Average duration of student chat sessions"
        )
    
    with col4:
        st.metric(
            "Total Sessions",
            analytics['total_sessions'],
            help="Total number of chat sessions completed"
        )

def display_analytics_charts():
    """Display analytics charts and visualizations"""
    st.markdown("### 📈 Student Engagement Analytics")
    
    # Get sessions data
    sessions_df = get_chat_sessions(limit=500)
    
    if sessions_df.empty:
        st.info("No student sessions data available yet.")
        return
    
    # Filter for students only
    student_sessions = sessions_df[sessions_df['user_type'] == 'Student'].copy()
    
    if student_sessions.empty:
        st.info("No student sessions found.")
        return
    
    # Convert timestamps
    student_sessions['start_time'] = pd.to_datetime(student_sessions['start_time'])
    student_sessions['date'] = student_sessions['start_time'].dt.date
    
    # Row 1: Time-based charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sessions per day
        daily_sessions = student_sessions.groupby('date').size().reset_index(name='sessions')
        
        fig_daily = px.line(
            daily_sessions, 
            x='date', 
            y='sessions',
            title="Daily Session Count",
            labels={'date': 'Date', 'sessions': 'Number of Sessions'}
        )
        fig_daily.update_layout(height=300)
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        # Session duration distribution
        fig_duration = px.histogram(
            student_sessions, 
            x='duration_minutes',
            title="Session Duration Distribution",
            labels={'duration_minutes': 'Duration (minutes)', 'count': 'Number of Sessions'},
            nbins=20
        )
        fig_duration.update_layout(height=300)
        st.plotly_chart(fig_duration, use_container_width=True)
    
    # Row 2: Student performance charts
    col3, col4 = st.columns(2)
    
    with col3:
        # Max level reached distribution
        level_counts = student_sessions['max_level_reached'].value_counts().sort_index()
        
        fig_levels = px.bar(
            x=level_counts.index,
            y=level_counts.values,
            title="Conversation Depth Distribution",
            labels={'x': 'Max Level Reached', 'y': 'Number of Sessions'}
        )
        fig_levels.update_layout(xaxis=dict(tickmode='linear'))
        fig_levels.update_layout(height=300)
        st.plotly_chart(fig_levels, use_container_width=True)
    
    with col4:
        # Articles discussion frequency
        article_counts = student_sessions['article_title'].value_counts().head(10)
        
        fig_articles = px.bar(
            x=article_counts.values,
            y=article_counts.index,
            orientation='h',
            title="Most Discussed Articles",
            labels={'x': 'Number of Sessions', 'y': 'Article'}
        )
        fig_articles.update_layout(height=300)
        st.plotly_chart(fig_articles, use_container_width=True)

def display_student_sessions():
    """Display student sessions table with filtering"""
    st.markdown("### 👥 Student Session Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.date_input(
            "Filter by date (from):",
            value=datetime.now().date() - timedelta(days=7),
            help="Show sessions from this date onwards"
        )
    
    with col2:
        min_duration = st.number_input(
            "Min duration (minutes):",
            min_value=0.0,
            value=0.0,
            step=0.5,
            help="Show sessions longer than this duration"
        )
    
    with col3:
        article_filter = st.text_input(
            "Filter by article:",
            placeholder="Enter article title or keyword",
            help="Filter sessions by article title"
        )
    
    # Get and filter sessions
    sessions_df = get_chat_sessions(limit=1000)
    
    if not sessions_df.empty:
        # Apply filters
        filtered_df = sessions_df[sessions_df['user_type'] == 'Student'].copy()
        
        # Date filter
        filtered_df['start_time'] = pd.to_datetime(filtered_df['start_time'])
        filtered_df = filtered_df[filtered_df['start_time'].dt.date >= date_filter]
        
        # Duration filter
        filtered_df = filtered_df[filtered_df['duration_minutes'] >= min_duration]
        
        # Article filter
        if article_filter:
            filtered_df = filtered_df[
                filtered_df['article_title'].str.contains(article_filter, case=False, na=False)
            ]
        
        # Display table
        if not filtered_df.empty:
            # Format for display
            display_df = filtered_df.copy()
            display_df['start_time'] = display_df['start_time'].dt.strftime('%Y-%m-%d %H:%M')
            display_df['duration_minutes'] = display_df['duration_minutes'].round(1)
            
            # Select columns for display
            columns_to_show = [
                'user_id', 'article_title', 'start_time', 'duration_minutes', 
                'message_count', 'max_level_reached'
            ]
            
            st.dataframe(
                display_df[columns_to_show],
                column_config={
                    'user_id': 'Student ID',
                    'article_title': 'Article',
                    'start_time': 'Start Time',
                    'duration_minutes': 'Duration (min)',
                    'message_count': 'Messages',
                    'max_level_reached': 'Max Level'
                },
                use_container_width=True,
                height=400
            )
            
            st.markdown(f"**Total sessions found:** {len(filtered_df)}")
        else:
            st.info("No sessions match the current filters.")
    else:
        st.info("No student sessions available yet.")

def display_chat_transcripts():
    """Display detailed chat transcripts"""
    st.markdown("### 💬 Chat Transcript Viewer")
    
    # Get sessions for transcript selection
    sessions_df = get_chat_sessions(limit=200)
    student_sessions = sessions_df[sessions_df['user_type'] == 'Student']
    
    if student_sessions.empty:
        st.info("No student sessions available for transcript viewing.")
        return
    
    # Session selection
    session_options = {}
    for _, row in student_sessions.iterrows():
        display_name = f"{row['user_id']} - {row['article_title']} ({row['start_time'][:16]})"
        session_options[display_name] = row['session_id']
    
    selected_session_name = st.selectbox(
        "Select a session to view transcript:",
        options=list(session_options.keys()),
        help="Choose a session to view the complete conversation"
    )
    
    if selected_session_name:
        session_id = session_options[selected_session_name]
        
        # Get session details
        session_info = student_sessions[student_sessions['session_id'] == session_id].iloc[0]
        
        # Display session info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Student", session_info['user_id'])
        with col2:
            st.metric("Duration", f"{session_info['duration_minutes']:.1f} min")
        with col3:
            st.metric("Messages", session_info['message_count'])
        with col4:
            st.metric("Max Level", session_info['max_level_reached'])
        
        st.markdown(f"**Article:** {session_info['article_title']}")
        
        # Get and display messages
        messages = get_chat_messages(session_id)
        
        if messages:
            st.markdown("---")
            st.markdown("#### Conversation Transcript")
            
            for i, message in enumerate(messages):
                timestamp = pd.to_datetime(message['timestamp']).strftime('%H:%M:%S')
                
                if message['role'] == 'student':
                    st.markdown(f"**🧑‍🎓 Student** _{timestamp}_")
                    st.info(message['content'])
                else:
                    st.markdown(f"**🤖 AI Tutor** _{timestamp}_")
                    st.success(message['content'])
                
                if i < len(messages) - 1:
                    st.markdown("")
        else:
            st.warning("No messages found for this session.")

def display_export_options():
    """Display data export options"""
    st.markdown("### 📥 Export Student Data")
    
    st.markdown("""
    Export student interaction data for grading and analysis purposes.
    All exported data respects student privacy and contains only educational interaction data.
    """)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date:",
            value=datetime.now().date() - timedelta(days=30),
            help="Export data from this date"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date:",
            value=datetime.now().date(),
            help="Export data until this date"
        )
    
    export_format = st.selectbox(
        "Export Format:",
        ["CSV", "Excel"],
        help="Choose the format for exported data"
    )
    
    if st.button("Generate Export", use_container_width=True):
        with st.spinner("Preparing export..."):
            # Get data
            export_df = export_interactions_csv(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            if not export_df.empty:
                st.success(f"Export generated! Found {len(export_df)} records.")
                
                # Prepare filename
                filename = f"student_interactions_{start_date}_{end_date}"
                
                if export_format == "CSV":
                    csv_data = export_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"{filename}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                else:  # Excel
                    from io import BytesIO
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, sheet_name='Student_Interactions', index=False)
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"{filename}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                # Show preview
                st.markdown("#### Export Preview (first 10 rows)")
                st.dataframe(export_df.head(10), use_container_width=True)
                
            else:
                st.warning("No data found for the selected date range.")

if __name__ == "__main__":
    main()

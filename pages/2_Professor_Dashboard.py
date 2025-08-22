import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
from datetime import datetime, timedelta
from components.auth import is_authenticated, get_current_user
from components.database import get_student_analytics, get_chat_sessions, get_chat_messages, export_interactions_csv
from components.assessment_quality import AssessmentQualitySystem

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
    
    # Initialize assessment system
    assessment_system = AssessmentQualitySystem()
    
    # Main dashboard layout
    display_overview_metrics()
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Analytics", 
        "👥 Student Sessions", 
        "💬 Chat Transcripts", 
        "🎯 Assessment Quality",
        "📅 Weekly Reports",
        "📥 Export Data"
    ])
    
    with tab1:
        display_analytics_charts()
    
    with tab2:
        display_student_sessions()
    
    with tab3:
        display_chat_transcripts()
    
    with tab4:
        display_assessment_quality(assessment_system)
    
    with tab5:
        display_weekly_reports(assessment_system)
    
    with tab6:
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
    
    # Add engagement metrics section
    st.markdown("### 🎯 Student Engagement Metrics")
    
    # Get engagement statistics from database
    conn = sqlite3.connect('data/chatbot_interactions.db')
    cursor = conn.cursor()
    
    try:
        # First ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_progress (
                student_id TEXT PRIMARY KEY,
                current_level INTEGER DEFAULT 1,
                total_interactions INTEGER DEFAULT 0,
                badges_earned TEXT DEFAULT '[]',
                concepts_explored TEXT DEFAULT '[]',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peer_insights (
                insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                article_title TEXT,
                cognitive_level INTEGER,
                upvotes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        
        # Count students with badges
        cursor.execute("""SELECT COUNT(*) FROM student_progress WHERE badges_earned != '[]'""")
        result = cursor.fetchone()
        students_with_badges = result[0] if result else 0
        
        # Count peer insights
        cursor.execute("SELECT COUNT(*) FROM peer_insights")
        result = cursor.fetchone()
        total_insights = result[0] if result else 0
        
        # Average cognitive level
        cursor.execute("SELECT AVG(current_level) FROM student_progress WHERE current_level > 0")
        result = cursor.fetchone()
        avg_level = result[0] if result and result[0] else 1.0
        
        # Count students exploring concepts
        cursor.execute("SELECT COUNT(*) FROM student_progress WHERE concepts_explored != '[]'")
        result = cursor.fetchone()
        students_with_concepts = result[0] if result else 0
        
    except Exception as e:
        students_with_badges = 0
        total_insights = 0
        avg_level = 1.0
        students_with_concepts = 0
    finally:
        conn.close()
    
    eng_col1, eng_col2, eng_col3, eng_col4 = st.columns(4)
    
    with eng_col1:
        st.metric(
            "Students with Badges",
            students_with_badges,
            help="Students who earned at least one achievement badge"
        )
    
    with eng_col2:
        st.metric(
            "Peer Insights Shared",
            total_insights,
            help="Quality questions shared for peer learning"
        )
    
    with eng_col3:
        st.metric(
            "Avg Cognitive Level",
            f"{avg_level:.1f}/4",
            help="Average depth of student cognitive engagement"
        )
    
    with eng_col4:
        st.metric(
            "Concept Explorers",
            students_with_concepts,
            help="Students actively connecting multiple concepts"
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
    if len(student_sessions) > 0:
        student_sessions = student_sessions.copy()  # Make a copy to avoid warnings
        student_sessions['start_time'] = pd.to_datetime(student_sessions['start_time'])
        student_sessions['date'] = pd.to_datetime(student_sessions['start_time']).dt.date
    
    # Row 1: Time-based charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sessions per day
        daily_sessions = student_sessions.groupby('date').size().reset_index().rename(columns={0: 'sessions'})
        
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
        if len(student_sessions) > 0:
            level_counts = pd.Series(student_sessions['max_level_reached']).value_counts().sort_index()
            
            fig_levels = px.bar(
                x=level_counts.index,
                y=level_counts.values,
                title="Conversation Depth Distribution",
                labels={'x': 'Max Level Reached', 'y': 'Number of Sessions'}
            )
            fig_levels.update_layout(xaxis=dict(tickmode='linear'))
            fig_levels.update_layout(height=300)
            st.plotly_chart(fig_levels, use_container_width=True)
        else:
            st.info("No data available")
    
    with col4:
        # Articles discussion frequency
        if len(student_sessions) > 0:
            article_counts = pd.Series(student_sessions['article_title']).value_counts().head(10)
            
            fig_articles = px.bar(
                x=article_counts.values,
                y=article_counts.index,
                orientation='h',
                title="Most Discussed Articles",
                labels={'x': 'Number of Sessions', 'y': 'Article'}
            )
            fig_articles.update_layout(height=300)
            st.plotly_chart(fig_articles, use_container_width=True)
        else:
            st.info("No data available")

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
        
        if len(filtered_df) > 0:
            # Date filter
            filtered_df['start_time'] = pd.to_datetime(filtered_df['start_time'])
            filtered_df = filtered_df[pd.to_datetime(filtered_df['start_time']).dt.date >= date_filter]
            
            # Duration filter  
            filtered_df = filtered_df[pd.to_numeric(filtered_df['duration_minutes'], errors='coerce') >= min_duration]
            
            # Article filter
            if article_filter:
                article_series = pd.Series(filtered_df['article_title'])
                mask = article_series.str.contains(article_filter, case=False, na=False)
                filtered_df = filtered_df[mask]
        
        # Display table
        if not filtered_df.empty:
            # Format for display
            display_df = filtered_df.copy()
            if len(display_df) > 0:
                display_df['start_time'] = pd.to_datetime(display_df['start_time']).dt.strftime('%Y-%m-%d %H:%M')
                display_df['duration_minutes'] = pd.to_numeric(display_df['duration_minutes'], errors='coerce').round(1)
            
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
        session_mask = pd.Series(student_sessions['session_id']) == session_id
        matching_sessions = student_sessions[session_mask]
        if len(matching_sessions) > 0:
            session_info = matching_sessions.iloc[0]
        else:
            st.error("Session not found")
            return
        
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
                    import pandas as pd
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, sheet_name='Student_Interactions', index=False)
                    buffer.seek(0)
                    
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

def display_assessment_quality(assessment_system):
    """Display automated assessment and rubric scoring"""
    st.markdown("### 🎯 Automated Assessment Quality")
    st.markdown("View automated rubric scoring and participation quality metrics for student engagement")
    
    # Class overview
    st.markdown("#### Class Assessment Overview")
    class_df = assessment_system.get_class_assessment_overview()
    
    if not class_df.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Students Assessed", len(class_df))
        with col2:
            st.metric("Avg Class Score", f"{class_df['avg_score'].mean():.1f}%")
        with col3:
            st.metric("Highest Avg Score", f"{class_df['avg_score'].max():.1f}%")
        with col4:
            st.metric("Lowest Avg Score", f"{class_df['avg_score'].min():.1f}%")
        
        # Display class data
        st.dataframe(
            class_df[['student_id', 'sessions_evaluated', 'avg_score', 'grades']],
            use_container_width=True,
            hide_index=True
        )
        
        # Rubric criteria comparison
        st.markdown("#### Rubric Criteria Performance")
        
        criteria_cols = ['avg_depth', 'avg_integration', 'avg_questions', 'avg_consistency', 'avg_progression']
        criteria_names = ['Depth of Analysis', 'Concept Integration', 'Question Quality', 'Engagement Consistency', 'Cognitive Progression']
        
        fig = go.Figure()
        for i, (col, name) in enumerate(zip(criteria_cols, criteria_names)):
            fig.add_trace(go.Box(
                y=class_df[col],
                name=name,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title="Class Performance by Rubric Criteria",
            yaxis_title="Score (%)",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assessment data available yet. Assessments are generated after students complete sessions.")
    
    # Individual student assessment
    st.markdown("#### Individual Student Assessment")
    
    conn = sqlite3.connect('data/chatbot_interactions.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT cs.user_id, cs.session_id, cs.article_title, cs.timestamp
        FROM chat_sessions cs
        ORDER BY cs.timestamp DESC
        LIMIT 20
    """)
    recent_sessions = cursor.fetchall()
    conn.close()
    
    if recent_sessions:
        session_options = [
            f"{row[0]} - {row[2][:30]}... ({datetime.fromisoformat(row[3]).strftime('%Y-%m-%d')})"
            for row in recent_sessions
        ]
        
        selected_session = st.selectbox(
            "Select a session to evaluate:",
            options=range(len(recent_sessions)),
            format_func=lambda x: session_options[x]
        )
        
        if st.button("Generate Rubric Evaluation"):
            student_id = recent_sessions[selected_session][0]
            session_id = recent_sessions[selected_session][1]
            
            with st.spinner("Evaluating session..."):
                assessment_system.display_rubric_evaluation(student_id, session_id)
                
                # Also show quality metrics
                st.divider()
                assessment_system.display_quality_metrics(student_id)
    else:
        st.info("No sessions available for evaluation")

def display_weekly_reports(assessment_system):
    """Display weekly progress reports for students"""
    st.markdown("### 📅 Weekly Progress Reports")
    st.markdown("Automated weekly summaries of student development and engagement")
    
    # Report generation options
    col1, col2 = st.columns(2)
    
    with col1:
        # Select student
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM chat_sessions ORDER BY user_id")
        students = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if students:
            selected_student = st.selectbox(
                "Select Student:",
                options=["All Students"] + students,
                help="Choose a student to view their weekly reports"
            )
        else:
            selected_student = None
            st.info("No students found in the system")
    
    with col2:
        # Select week
        week_start = st.date_input(
            "Week Starting:",
            value=datetime.now().date() - timedelta(days=datetime.now().weekday()),
            help="Select the Monday of the week to generate report"
        )
    
    if selected_student and selected_student != "All Students":
        # Generate and display individual report
        if st.button("Generate Weekly Report", use_container_width=True):
            with st.spinner("Generating report..."):
                assessment_system.display_weekly_reports(selected_student)
    elif selected_student == "All Students":
        # Display all reports
        assessment_system.display_weekly_reports()
    
    # Batch report generation
    st.divider()
    st.markdown("#### Batch Report Generation")
    
    if st.button("Generate Reports for All Students (Current Week)", use_container_width=True):
        with st.spinner("Generating reports for all students..."):
            week_start_dt = datetime.now() - timedelta(days=datetime.now().weekday())
            week_start_dt = week_start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            success_count = 0
            error_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, student_id in enumerate(students):
                try:
                    report = assessment_system.generate_weekly_report(student_id, week_start_dt)
                    if "error" not in report:
                        success_count += 1
                    else:
                        error_count += 1
                except:
                    error_count += 1
                
                progress = (i + 1) / len(students)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i + 1}/{len(students)} students...")
            
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ Generated {success_count} reports successfully")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} students had insufficient data for reports")
    
    # Export weekly reports
    st.divider()
    st.markdown("#### Export Weekly Reports")
    
    if st.button("Export All Weekly Reports to Excel", use_container_width=True):
        conn = sqlite3.connect('data/chatbot_interactions.db')
        query = """
            SELECT 
                student_id,
                week_start,
                week_end,
                sessions_completed,
                avg_quality_score,
                cognitive_progress,
                strengths,
                areas_for_improvement
            FROM weekly_reports
            ORDER BY week_start DESC, student_id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            # Prepare Excel export
            from io import BytesIO
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Weekly_Reports', index=False)
            
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Weekly Reports (Excel)",
                data=buffer.getvalue(),
                file_name=f"weekly_reports_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.success(f"Export ready! Contains {len(df)} weekly reports.")
        else:
            st.warning("No weekly reports available for export")

if __name__ == "__main__":
    main()

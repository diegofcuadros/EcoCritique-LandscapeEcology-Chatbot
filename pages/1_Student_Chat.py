import streamlit as st
from datetime import datetime
from components.auth import is_authenticated, get_current_user
from components.chat_engine import SocraticChatEngine, initialize_chat_session, add_message, get_chat_history, calculate_session_duration
from components.rag_system import get_rag_system, get_article_processor
from components.database import save_chat_session, get_articles
from components.student_engagement import StudentEngagementSystem
from components.assessment_quality import AssessmentQualitySystem
import PyPDF2
import io

st.set_page_config(page_title="Student Chat", page_icon="📖", layout="wide")

def main():
    st.title("📖 Article Discussion Chat")
    
    if not is_authenticated():
        st.error("Please log in from the main page to access the chat.")
        st.stop()
    
    user = get_current_user()
    if user['type'] not in ['Student', 'Guest']:
        st.error("This page is only accessible to students.")
        st.stop()
    
    # Initialize systems
    chat_engine = SocraticChatEngine()
    rag_system = get_rag_system()
    article_processor = get_article_processor()
    engagement_system = StudentEngagementSystem()
    assessment_system = AssessmentQualitySystem()
    
    # Initialize chat session
    initialize_chat_session()
    
    # Sidebar - Article Selection and Session Info
    with st.sidebar:
        st.markdown("### Current Session")
        st.markdown(f"**Student:** {user['id']}")
        
        duration = calculate_session_duration()
        st.markdown(f"**Session Time:** {duration:.1f} minutes")
        
        message_count = len(get_chat_history())
        st.markdown(f"**Messages:** {message_count}")
        
        # Show badges earned
        progress = engagement_system.get_student_progress(user['id'])
        if progress['badges_earned']:
            st.markdown("**Badges Earned:**")
            for badge_key in progress['badges_earned']:
                if badge_key in engagement_system.achievement_badges:
                    badge = engagement_system.achievement_badges[badge_key]
                    st.markdown(f"{badge['icon']} {badge['name']}")
        
        st.divider()
        
        # Article selection
        st.markdown("### Select Article")
        articles_df = get_articles(active_only=True)
        
        if not articles_df.empty:
            article_options = {}
            for _, row in articles_df.iterrows():
                display_name = f"Week {row['week_number']}: {row['title']}"
                article_options[display_name] = row
            
            selected_article_name = st.selectbox(
                "Choose an article to discuss:",
                options=list(article_options.keys()),
                help="Select the article you want to analyze"
            )
            
            selected_article = article_options[selected_article_name]
            
            # Load article content
            if st.button("Load Article", use_container_width=True):
                try:
                    with open(selected_article['file_path'], 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        article_text = ""
                        for page in pdf_reader.pages:
                            article_text += page.extract_text()
                        
                        article_processor.process_article_text(article_text, selected_article['title'])
                        st.success("Article loaded successfully!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error loading article: {e}")
        else:
            st.warning("No articles available. Please contact your instructor.")
            
        st.divider()
        
        # Session controls
        if st.button("Save Session", use_container_width=True):
            save_current_session(user, chat_engine)
        
        if st.button("Reset Chat", use_container_width=True):
            reset_chat_session()
    
    # Main chat interface
    display_chat_interface(chat_engine, rag_system, article_processor, user, engagement_system)

def display_chat_interface(chat_engine, rag_system, article_processor, user, engagement_system):
    """Display the main chat interface with engagement features"""
    
    # Check if article is loaded
    current_article = st.session_state.get('current_article')
    if not current_article:
        st.info("👆 Please select and load an article from the sidebar to begin the discussion.")
        return
    
    # Display engagement features at the top
    message_count = len(get_chat_history())
    
    # Progress indicator and achievements
    with st.container():
        engagement_system.display_progress_indicator(user['id'], message_count)
    
    st.divider()
    
    # Article info and concept map
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.expander("📄 Current Article", expanded=False):
            st.markdown(f"**Title:** {current_article['title']}")
            st.markdown(f"**Summary:** {st.session_state.get('article_summary', 'No summary available')}")
            
            key_concepts = st.session_state.get('key_concepts', [])
            if key_concepts:
                st.markdown(f"**Key Concepts:** {', '.join(key_concepts)}")
    
    with col2:
        # Concept map
        key_concepts = st.session_state.get('key_concepts', [])
        engagement_system.display_concept_map(user['id'], current_article['title'], key_concepts)
    
    st.divider()
    
    # Peer insights section
    with st.expander("💭 Peer Insights - Learn from Fellow Students", expanded=False):
        engagement_system.display_peer_insights(current_article['title'])
    
    st.divider()
    
    # Chat messages display
    chat_container = st.container()
    with chat_container:
        messages = get_chat_history()
        
        if not messages:
            # Initial bot message
            intro_message = f"""
            Hello! I'm your Socratic AI tutor. I see we're discussing "{current_article['title']}".
            
            I'm here to guide you through critical analysis of this article using questions rather than giving you direct answers. 
            
            Have you finished reading the article? What caught your attention first?
            """
            add_message("assistant", intro_message)
            st.rerun()
        
        # Display all messages
        for message in messages:
            if message["role"] == "student":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your response here...")
    
    if user_input:
        # Add user message
        add_message("student", user_input)
        
        # Check if user is seeking direct answers
        if chat_engine.detect_answer_seeking(user_input):
            bot_response = chat_engine.redirect_answer_seeking()
        else:
            # Get relevant knowledge
            relevant_knowledge = rag_system.search_knowledge(user_input)
            article_context = article_processor.get_article_context()
            
            # Generate Socratic response
            bot_response = chat_engine.generate_socratic_response(
                user_input, 
                get_chat_history(),
                article_context,
                relevant_knowledge
            )
        
        # Add bot response
        add_message("assistant", bot_response)
        
        # Track message quality for assessment
        quality_metrics = assessment_system.calculate_message_quality(user_input)
        
        # Store quality metrics in database
        import sqlite3
        conn = sqlite3.connect('data/chatbot_interactions.db')
        cursor = conn.cursor()
        
        # Ensure quality_metrics table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                message_id INTEGER,
                thoughtfulness_score REAL,
                critical_thinking_present BOOLEAN,
                synthesis_present BOOLEAN,
                word_count INTEGER,
                question_complexity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO quality_metrics 
            (student_id, message_id, thoughtfulness_score, critical_thinking_present,
             synthesis_present, word_count, question_complexity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user['id'], len(get_chat_history()), quality_metrics['thoughtfulness_score'],
              quality_metrics['critical_thinking_present'], quality_metrics['synthesis_present'],
              quality_metrics['word_count'], quality_metrics['question_complexity']))
        
        conn.commit()
        conn.close()
        
        # Check if the user's question is high quality for peer insights
        if engagement_system.check_question_quality(user_input, get_chat_history()):
            # Determine cognitive level based on message count
            level = min(4, 1 + (message_count // 2))
            engagement_system.save_peer_insight(user_input, current_article['title'], level)
        
        # Update student progress with concepts
        key_concepts = st.session_state.get('key_concepts', [])
        engagement_system.update_progress(user['id'], len(get_chat_history()), key_concepts)
        
        # Auto-save session periodically
        if len(get_chat_history()) % 4 == 0:  # Save every 4 messages
            save_current_session(user, chat_engine, auto_save=True)
        
        st.rerun()

def save_current_session(user, chat_engine, auto_save=False):
    """Save the current chat session"""
    messages = get_chat_history()
    if not messages:
        if not auto_save:
            st.warning("No messages to save.")
        return
    
    session_id = st.session_state.get('chat_session_id')
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.chat_session_id = session_id
    
    article_title = st.session_state.get('current_article', {}).get('title', 'Unknown Article')
    duration = calculate_session_duration()
    max_level = chat_engine.get_conversation_level(messages)
    
    success = save_chat_session(
        session_id=session_id,
        user_id=user['id'],
        user_type=user['type'],
        messages=messages,
        article_title=article_title,
        duration_minutes=duration,
        max_level=max_level
    )
    
    if success and not auto_save:
        st.success("Session saved successfully!")
    elif not success and not auto_save:
        st.error("Failed to save session.")

def reset_chat_session():
    """Reset the current chat session"""
    keys_to_remove = ['chat_messages', 'chat_session_id', 'chat_start_time']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Chat session reset!")
    st.rerun()

if __name__ == "__main__":
    main()

import streamlit as st
import os
import time
from datetime import datetime
from components.auth import is_authenticated, get_current_user
from components.chat_engine import SocraticChatEngine, initialize_chat_session, add_message, get_chat_history, calculate_session_duration
from components.rag_system import get_rag_system, get_article_processor
from components.database import save_chat_session, get_articles, DATABASE_PATH
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
                def load_article_safely(file_path, title):
                    """Safely load and process article with comprehensive error handling"""
                    try:
                        # Check if file exists
                        if not os.path.exists(file_path):
                            st.error(f"📄 Article file not found: {file_path}")
                            return False
                        
                        # Check file size
                        file_size = os.path.getsize(file_path)
                        if file_size == 0:
                            st.error("📄 Article file appears to be empty")
                            return False
                        elif file_size > 50 * 1024 * 1024:  # 50MB limit
                            st.error("📄 Article file is too large (>50MB)")
                            return False
                        
                        # Progress indicator
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Read and process PDF
                        status_text.text("📖 Reading PDF file...")
                        progress_bar.progress(0.2)
                        
                        with open(file_path, 'rb') as file:
                            try:
                                pdf_reader = PyPDF2.PdfReader(file)
                                total_pages = len(pdf_reader.pages)
                                
                                if total_pages == 0:
                                    st.error("📄 PDF appears to have no pages")
                                    return False
                                
                                status_text.text(f"📄 Processing {total_pages} pages...")
                                progress_bar.progress(0.4)
                                
                                article_text = ""
                                successful_pages = 0
                                
                                for i, page in enumerate(pdf_reader.pages):
                                    try:
                                        page_text = page.extract_text()
                                        if page_text.strip():  # Only add non-empty pages
                                            article_text += f"\n--- Page {i+1} ---\n{page_text}"
                                            successful_pages += 1
                                        
                                        # Update progress
                                        progress = 0.4 + (0.4 * (i + 1) / total_pages)
                                        progress_bar.progress(progress)
                                        
                                    except Exception as e:
                                        st.warning(f"⚠️ Could not extract text from page {i+1}: {str(e)[:100]}")
                                        continue
                                
                                if len(article_text.strip()) < 100:
                                    st.error(f"📄 PDF text extraction yielded insufficient content ({len(article_text)} characters). The PDF might be image-based or corrupted.")
                                    return False
                                
                                if successful_pages == 0:
                                    st.error("📄 No readable pages found in PDF")
                                    return False
                                
                                status_text.text("🤖 Processing with AI research agent...")
                                progress_bar.progress(0.8)
                                
                                # Process with article processor
                                if hasattr(article_processor, 'process_article_text'):
                                    success = article_processor.process_article_text(article_text, title)
                                elif hasattr(article_processor, 'process_article'):
                                    success = article_processor.process_article(article_text, title)
                                else:
                                    st.warning("🔧 Article processor method not found - using basic processing")
                                    # Store article text directly in session state as fallback
                                    st.session_state.current_article_text = article_text
                                    st.session_state.current_article_title = title
                                    success = True
                                
                                progress_bar.progress(1.0)
                                status_text.text("✅ Article processing complete!")
                                
                                # Clean up progress indicators after a moment
                                import time
                                time.sleep(1)
                                progress_bar.empty()
                                status_text.empty()
                                
                                return success
                                
                            except PyPDF2.PdfReadError as e:
                                st.error(f"📄 PDF reading error: {str(e)[:100]}. The file might be corrupted or password-protected.")
                                return False
                            except Exception as e:
                                st.error(f"📄 Unexpected PDF processing error: {str(e)[:100]}")
                                return False
                        
                    except FileNotFoundError:
                        st.error(f"📁 Article file not found: {file_path}")
                        st.info("💡 Please contact your instructor to upload this article.")
                        return False
                    except PermissionError:
                        st.error(f"🔒 Permission denied accessing: {file_path}")
                        return False
                    except Exception as e:
                        st.error(f"🚨 Unexpected error loading article: {str(e)[:200]}")
                        st.info("💡 Please try refreshing the page or contact your instructor if this persists.")
                        return False
                
                # Call the safe loading function
                success = load_article_safely(selected_article['file_path'], selected_article['title'])
                
                if success:
                    st.success("🎉 Article loaded and processed successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Article loading failed. Please try a different article or contact your instructor.")
        else:
            st.warning("No articles available. Please contact your instructor.")
            
        st.divider()
        
        # Session controls
        if st.button("Save Session", use_container_width=True):
            save_current_session(user, chat_engine)
        
        if st.button("Reset Chat", use_container_width=True):
            reset_chat_session()
    
    # Main chat interface
    display_chat_interface(chat_engine, rag_system, article_processor, user, engagement_system, assessment_system)

def display_chat_interface(chat_engine, rag_system, article_processor, user, engagement_system, assessment_system):
    """Display the main chat interface with engagement features"""
    
    # Check if article is loaded
    current_article = st.session_state.get('current_article')
    if not current_article:
        st.info("👆 Please select and load an article from the sidebar to begin the discussion.")
        return
    
    # Initialize default values if processing data is missing
    if 'key_bullet_points' not in st.session_state:
        st.session_state.key_bullet_points = []
    if 'key_terminology' not in st.session_state:
        st.session_state.key_terminology = {}
    if 'article_summary' not in st.session_state:
        st.session_state.article_summary = "Article summary being processed..."
    if 'key_concepts' not in st.session_state:
        st.session_state.key_concepts = []
    
    # If we have an article but missing enhanced data, try to reprocess
    if (current_article and 
        (not st.session_state.get('key_bullet_points') or not st.session_state.get('key_terminology')) and
        st.session_state.get('processed_text')):
        
        try:
            # Reprocess using existing text data
            processed_text = st.session_state.get('processed_text', '')
            if processed_text:
                # Generate missing content
                if not st.session_state.get('key_bullet_points'):
                    st.session_state.key_bullet_points = article_processor._generate_bullet_points(processed_text)
                if not st.session_state.get('key_terminology'):
                    st.session_state.key_terminology = article_processor._extract_terminology(processed_text)
        except Exception as e:
            st.warning(f"Could not reprocess article data: {e}")
    
    # Show reprocess button if data is still missing
    if (current_article and 
        (not st.session_state.get('key_bullet_points') or not st.session_state.get('key_terminology'))):
        
        st.info("Article content needs to be reprocessed with enhanced features.")
        if st.button("🔄 Reprocess Article", key="reprocess_article"):
            # Try to reprocess from the file
            articles_df = get_articles(active_only=True)
            matching_article = None
            
            for _, article in articles_df.iterrows():
                if article['title'] == current_article['title']:
                    matching_article = article
                    break
            
            if matching_article is not None:
                try:
                    success = article_processor.process_article_from_file(
                        matching_article['file_path'], 
                        matching_article['title']
                    )
                    if success:
                        st.success("Article reprocessed successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Reprocessing failed: {e}")
    
    # Display engagement features at the top
    message_count = len(get_chat_history())
    
    # Progress indicator and achievements
    with st.container():
        engagement_system.display_progress_indicator(user['id'], message_count)
    
    st.divider()
    
    # Enhanced Article Information Section - Always Visible
    st.markdown("### 📄 Current Article")
    
    # Create a prominent container for article information
    with st.container():
        # Article title and basic info
        st.markdown(f"**{current_article['title']}**")
        
        # Create tabs for different information sections
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary & Key Points", "🔍 Key Terminology", "🧠 Key Concepts", "🗺️ Concept Map"])
        
        with tab1:
            # Article summary
            article_summary = st.session_state.get('article_summary', 'No summary available')
            st.markdown("**Article Summary:**")
            st.info(article_summary)
            
            # 10 bullet points
            bullet_points = st.session_state.get('key_bullet_points', [])
            if bullet_points:
                st.markdown("**Key Findings & Content:**")
                for i, point in enumerate(bullet_points, 1):
                    st.markdown(f"{i}. {point}")
            else:
                st.markdown("**Key Points:** Processing article content...")
        
        with tab2:
            # Key terminology with definitions
            terminology = st.session_state.get('key_terminology', {})
            if terminology:
                st.markdown("**Important Terms & Definitions:**")
                for term, definition in terminology.items():
                    with st.expander(f"🔍 **{term}**", expanded=False):
                        st.markdown(definition)
            else:
                st.markdown("**Terminology:** Processing article content...")
        
        with tab3:
            # Key concepts
            key_concepts = st.session_state.get('key_concepts', [])
            if key_concepts:
                st.markdown("**Key Landscape Ecology Concepts in this Article:**")
                concepts_text = ""
                for concept in key_concepts:
                    concepts_text += f"• **{concept}**\n"
                st.markdown(concepts_text)
                
                # Learning objectives
                learning_objectives = st.session_state.get('learning_objectives', [])
                if learning_objectives:
                    st.markdown("**Learning Objectives:**")
                    for obj in learning_objectives:
                        st.markdown(f"• {obj}")
            else:
                st.markdown("**Concepts:** Processing article content...")
        
        with tab4:
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
            Hello! I'm your Landscape Ecology AI tutor. I see we're discussing "{current_article['title']}".
            
            I'm here to help you understand this article and landscape ecology concepts. I can answer your questions about methods, findings, and concepts, while also guiding you through critical analysis with thought-provoking questions.
            
            Have you finished reading the article? What would you like to know more about or discuss?
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
        conn = sqlite3.connect(DATABASE_PATH)
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
        
        # Auto-save session after every exchange to ensure data persistence
        save_current_session(user, chat_engine, auto_save=True)
        
        st.rerun()

def save_current_session(user, chat_engine, auto_save=False):
    """Save the current chat session"""
    messages = get_chat_history()
    if not messages:
        if not auto_save:
            st.warning("No messages to save.")
        return
    
    # Ensure stable session ID - create once and keep for the entire session
    session_id = st.session_state.get('chat_session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        st.session_state.chat_session_id = session_id
    
    article_title = st.session_state.get('current_article', {}).get('title', 'Unknown Article')
    duration = calculate_session_duration()
    max_level = chat_engine.get_conversation_level(messages)
    
    # Standardize user_type to ensure consistent database filtering
    user_type = "Student" if user['type'].lower() in ['student', 'guest'] else user['type']
    
    success = save_chat_session(
        session_id=session_id,
        user_id=user['id'],
        user_type=user_type,
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

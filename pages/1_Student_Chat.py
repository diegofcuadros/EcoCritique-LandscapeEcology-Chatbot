import streamlit as st
from datetime import datetime
from components.auth import is_authenticated, get_current_user
from components.chat_engine import SocraticChatEngine, initialize_chat_session, add_message, get_chat_history, calculate_session_duration
from components.rag_system import get_rag_system, get_article_processor
from components.database import save_chat_session, get_articles
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
    display_chat_interface(chat_engine, rag_system, article_processor, user)

def display_chat_interface(chat_engine, rag_system, article_processor, user):
    """Display the main chat interface"""
    
    # Check if article is loaded
    current_article = st.session_state.get('current_article')
    if not current_article:
        st.info("👆 Please select and load an article from the sidebar to begin the discussion.")
        return
    
    # Article info
    with st.expander("📄 Current Article", expanded=False):
        st.markdown(f"**Title:** {current_article['title']}")
        st.markdown(f"**Summary:** {st.session_state.get('article_summary', 'No summary available')}")
        
        key_concepts = st.session_state.get('key_concepts', [])
        if key_concepts:
            st.markdown(f"**Key Concepts:** {', '.join(key_concepts)}")
    
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

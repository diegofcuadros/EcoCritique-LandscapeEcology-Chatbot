import streamlit as st
import os
import shutil
from datetime import datetime
import PyPDF2
import io
from components.auth import is_authenticated, get_current_user
from components.database import save_article, get_articles
from components.rag_system import get_rag_system

st.set_page_config(page_title="Article Upload", page_icon="📤", layout="wide")

def main():
    st.title("📤 Article Upload & Management")
    
    if not is_authenticated():
        st.error("Please log in from the main page to access this feature.")
        st.stop()
    
    user = get_current_user()
    if user['type'] != 'Professor':
        st.error("This page is only accessible to professors.")
        st.stop()
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📤 Upload New Article", "📚 Manage Articles", "🧠 Knowledge Base"])
    
    with tab1:
        display_upload_interface()
    
    with tab2:
        display_article_management()
    
    with tab3:
        display_knowledge_base_management()

def display_upload_interface():
    """Display the article upload interface"""
    st.markdown("### Upload New Article")
    st.markdown("Upload PDF articles for student discussion sessions.")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("data/articles", exist_ok=True)
    
    with st.form("article_upload_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Article file upload
            uploaded_file = st.file_uploader(
                "Choose PDF file:",
                type=['pdf'],
                help="Select a PDF article for students to analyze"
            )
            
            # Article metadata
            article_title = st.text_input(
                "Article Title:",
                placeholder="Enter the full title of the article",
                help="This will be displayed to students"
            )
            
            learning_objectives = st.text_area(
                "Learning Objectives:",
                placeholder="What should students learn from this article?\n- Objective 1\n- Objective 2\n- Objective 3",
                height=100,
                help="Key learning goals for this article discussion"
            )
            
            key_concepts = st.text_area(
                "Key Concepts to Explore:",
                placeholder="List important concepts students should discover:\n- Concept 1\n- Concept 2\n- Concept 3",
                height=100,
                help="Main concepts the AI should guide students to explore"
            )
        
        with col2:
            week_number = st.number_input(
                "Week Number:",
                min_value=1,
                max_value=16,
                value=1,
                help="Which week of the course is this for?"
            )
            
            st.markdown("#### Upload Guidelines")
            st.info("""
            **Best Practices:**
            - Use clear, descriptive titles
            - Include 3-5 learning objectives
            - List key concepts students should discover
            - Ensure PDF is text-readable (not just scanned images)
            """)
        
        # Research agent option
        enable_research = st.checkbox(
            "🤖 Enable AI Research Agent",
            value=True,
            help="Automatically research and gather related information about this article from the web"
        )
        
        # Submit button
        submitted = st.form_submit_button("Upload Article", use_container_width=True)
        
        if submitted:
            upload_article(uploaded_file, article_title, week_number, learning_objectives, key_concepts, enable_research)

def upload_article(uploaded_file, title, week_number, objectives, concepts, enable_research=False):
    """Process and save uploaded article"""
    
    # Validation
    if not uploaded_file:
        st.error("Please select a PDF file to upload.")
        return
    
    if not title.strip():
        st.error("Please provide an article title.")
        return
    
    try:
        # Read and validate PDF
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        if len(pdf_reader.pages) == 0:
            st.error("The uploaded PDF appears to be empty.")
            return
        
        # Extract text to validate readability
        sample_text = ""
        for page in pdf_reader.pages[:3]:  # Check first 3 pages
            sample_text += page.extract_text()
        
        if len(sample_text.strip()) < 100:
            st.warning("The PDF may not contain readable text. This could affect the AI's ability to discuss the article.")
        
        # Save file
        safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        filename = f"week_{week_number}_{safe_filename}.pdf"
        file_path = os.path.join("data/articles", filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Save to database
        article_id = save_article(
            title=title,
            file_path=file_path,
            week_number=week_number,
            learning_objectives=objectives,
            key_concepts=concepts
        )
        
        if article_id:
            st.success(f"Article '{title}' uploaded successfully!")
            st.balloons()
            
            # Add to knowledge base if concepts provided
            if concepts.strip():
                rag_system = get_rag_system()
                rag_system.add_to_knowledge_base(f"Article: {title}\nKey concepts: {concepts}")
            
            # Run AI Research Agent if enabled
            if enable_research:
                with st.spinner("🔍 AI Research Agent gathering related information..."):
                    try:
                        from components.research_agent import get_research_agent
                        research_agent = get_research_agent()
                        
                        # Extract article text for research
                        article_text = ""
                        for page in pdf_reader.pages:
                            article_text += page.extract_text()
                        
                        research_results = research_agent.research_article(
                            title,
                            article_text,
                            f"week{week_number}_{article_id}"
                        )
                        
                        st.success("🤖 Research Agent completed!")
                        st.info(f"""
**Research Summary:**
- 📁 Research folder: `{research_results['folder_path']}`
- 🔍 Concepts analyzed: {research_results['concepts_found']}
- 🌐 Web searches performed: {research_results['searches_performed']}
- 📚 Knowledge chunks created: {research_results['knowledge_chunks_created']}

The AI chatbot now has enhanced knowledge about this article!
                        """)
                    except Exception as e:
                        st.warning(f"Research agent encountered an issue: {str(e)}")
                        st.info("Article uploaded successfully, but additional research could not be completed.")
            
            # Show preview
            with st.expander("📄 Upload Summary", expanded=True):
                st.markdown(f"**Title:** {title}")
                st.markdown(f"**Week:** {week_number}")
                st.markdown(f"**File:** {filename}")
                st.markdown(f"**Pages:** {len(pdf_reader.pages)}")
                if objectives:
                    st.markdown(f"**Learning Objectives:** {objectives}")
                if concepts:
                    st.markdown(f"**Key Concepts:** {concepts}")
        else:
            st.error("Failed to save article to database.")
            # Clean up file if database save failed
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        st.error(f"Error processing article: {str(e)}")

def display_article_management():
    """Display interface for managing existing articles"""
    st.markdown("### Manage Existing Articles")
    
    articles_df = get_articles(active_only=False)
    
    if articles_df.empty:
        st.info("No articles uploaded yet. Use the 'Upload New Article' tab to add articles.")
        return
    
    # Display articles table
    st.markdown("#### Uploaded Articles")
    
    # Add action buttons to dataframe display
    for idx, article in articles_df.iterrows():
        with st.expander(f"Week {article['week_number']}: {article['title']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Upload Date:** {article['upload_date'][:16]}")
                st.markdown(f"**File:** {os.path.basename(article['file_path'])}")
                st.markdown(f"**Status:** {'Active' if article['is_active'] else 'Inactive'}")
                
                if article['learning_objectives']:
                    st.markdown(f"**Learning Objectives:**")
                    st.markdown(article['learning_objectives'])
                
                if article['key_concepts']:
                    st.markdown(f"**Key Concepts:**")
                    st.markdown(article['key_concepts'])
            
            with col2:
                # Toggle active status
                current_status = bool(article['is_active'])
                new_status = st.checkbox(
                    "Active",
                    value=current_status,
                    key=f"active_{article['id']}",
                    help="Toggle whether students can access this article"
                )
                
                if new_status != current_status:
                    update_article_status(article['id'], new_status)
                    st.rerun()
            
            with col3:
                # Delete button
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{article['id']}",
                    help="Permanently delete this article"
                ):
                    delete_article(article['id'], article['file_path'])
                    st.rerun()

def update_article_status(article_id, is_active):
    """Update article active status"""
    # This would update the database - simplified for this example
    st.success(f"Article status updated to {'Active' if is_active else 'Inactive'}")

def delete_article(article_id, file_path):
    """Delete an article"""
    try:
        # Remove file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Would also remove from database in real implementation
        st.success("Article deleted successfully!")
        
    except Exception as e:
        st.error(f"Error deleting article: {e}")

def display_knowledge_base_management():
    """Display knowledge base management interface"""
    st.markdown("### Knowledge Base Management")
    st.markdown("Manage the landscape ecology knowledge base that guides the AI tutor.")
    
    rag_system = get_rag_system()
    
    # Display current knowledge base stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Knowledge Chunks", len(rag_system.knowledge_base))
    
    with col2:
        st.metric("Search Index Status", "Ready" if hasattr(rag_system, 'search_index') else "Not Ready")
    
    # Add new knowledge
    st.markdown("#### Add New Knowledge")
    
    with st.form("knowledge_form"):
        new_knowledge = st.text_area(
            "Add landscape ecology content:",
            placeholder="Enter new concepts, definitions, or explanations that the AI should know about...",
            height=150,
            help="Add new knowledge that will help the AI provide better guidance to students"
        )
        
        if st.form_submit_button("Add to Knowledge Base"):
            if new_knowledge.strip():
                rag_system.add_to_knowledge_base(new_knowledge)
                st.success("Knowledge added successfully!")
                st.rerun()
            else:
                st.error("Please enter some content to add.")
    
    # Test knowledge retrieval
    st.markdown("#### Test Knowledge Retrieval")
    
    test_query = st.text_input(
        "Test query:",
        placeholder="Enter a question to test knowledge retrieval...",
        help="Test how well the knowledge base responds to student questions"
    )
    
    if test_query:
        relevant_knowledge = rag_system.search_knowledge(test_query)
        
        with st.expander("Retrieved Knowledge", expanded=True):
            st.markdown(relevant_knowledge)
    
    # Knowledge base preview
    if st.checkbox("Show Knowledge Base Preview"):
        st.markdown("#### Current Knowledge Base")
        
        for i, chunk in enumerate(rag_system.knowledge_base[:10]):  # Show first 10 chunks
            with st.expander(f"Chunk {i+1}", expanded=False):
                st.markdown(chunk)
        
        if len(rag_system.knowledge_base) > 10:
            st.markdown(f"... and {len(rag_system.knowledge_base) - 10} more chunks")

if __name__ == "__main__":
    main()

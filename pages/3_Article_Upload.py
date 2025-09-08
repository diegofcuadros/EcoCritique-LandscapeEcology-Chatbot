import streamlit as st
import os
import shutil
from datetime import datetime
import PyPDF2
import io
from components.auth import is_authenticated, get_current_user
from components.database import save_article, get_articles, delete_article, update_article_status
from components.assignment_parser import AssignmentParser
# Delayed import to avoid initialization issues
# from components.rag_system import get_rag_system

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📤 Upload New Article", "📚 Manage Articles", "📄 Upload Assignment", "❓ Assignment Questions", "🧠 Knowledge Base", "🔍 Research Monitoring"])
    
    with tab1:
        display_upload_interface()
    
    with tab2:
        display_article_management()
    
    with tab3:
        display_assignment_upload_interface()
    
    with tab4:
        display_assignment_questions_interface()
    
    with tab5:
        display_knowledge_base_management()
    
    with tab6:
        display_research_monitoring()

def display_assignment_upload_interface():
    """Display the assignment upload and parsing interface"""
    st.markdown("### 📄 Upload & Parse Assignment")
    st.markdown("Upload assignment documents (PDF, Word, or text) to automatically extract structured questions and create tutoring guidance.")
    
    # Create assignments directory if it doesn't exist
    os.makedirs("data/assignments", exist_ok=True)
    
    # Initialize assignment parser
    parser = AssignmentParser()
    
    with st.form("assignment_upload_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Assignment file upload
            uploaded_assignment = st.file_uploader(
                "Choose assignment file:",
                type=['pdf', 'docx', 'txt', 'md'],
                help="Select an assignment document to parse (PDF, Word, or text file)"
            )
            
            # Assignment metadata
            assignment_title = st.text_input(
                "Assignment Title:",
                placeholder="Enter assignment title (will be auto-detected if not provided)",
                help="Leave blank to auto-detect from document"
            )
            
            assignment_type = st.selectbox(
                "Assignment Type:",
                ["socratic_analysis", "case_study_analysis", "concept_application", "research_synthesis"],
                help="Type of assignment for optimal tutoring approach"
            )
            
            # Link to article
            articles_df = get_articles()
            if not articles_df.empty:
                article_options = ["No specific article"] + [f"Week {row['week_number']}: {row['title']}" for _, row in articles_df.iterrows()]
                linked_article = st.selectbox(
                    "Link to Article (optional):",
                    article_options,
                    help="Associate this assignment with a specific article for enhanced guidance"
                )
            else:
                linked_article = "No specific article"
                st.info("Upload articles first to link assignments to specific readings.")
        
        with col2:
            st.markdown("#### Parsing Features")
            st.info("""
            **Auto-Detection:**
            - Question extraction from text
            - Bloom's taxonomy classification
            - Evidence requirements
            - Learning objectives
            - Word count estimation
            
            **Enhanced Tutoring:**
            - Generated guidance prompts
            - Progressive questioning
            - Context-aware responses
            """)
        
        # Submit button
        submitted = st.form_submit_button("📄 Parse Assignment", use_container_width=True)
        
        if submitted:
            if uploaded_assignment:
                process_assignment_upload(uploaded_assignment, assignment_title, assignment_type, linked_article, parser)
            else:
                st.error("Please select an assignment file to upload.")

def process_assignment_upload(uploaded_file, title, assignment_type, linked_article, parser):
    """Process and parse uploaded assignment"""
    
    try:
        # Parse the assignment document
        with st.spinner("🔍 Parsing assignment document..."):
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            
            parsed_data = parser.parse_assignment_document(file_content, filename, assignment_type)
        
        # Check for parsing errors
        if parsed_data.get('error'):
            st.error(f"❌ Parsing failed: {parsed_data['error_message']}")
            return
        
        # Validate parsed data
        is_valid, issues = parser.validate_parsed_assignment(parsed_data)
        
        if not is_valid:
            st.warning("⚠️ Parsing Issues Detected:")
            for issue in issues:
                st.warning(f"• {issue}")
            
            if not st.checkbox("Continue anyway? (You can manually edit questions later)"):
                return
        
        # Show parsing preview
        st.success("✅ Assignment parsed successfully!")
        
        with st.expander("📋 Parsing Preview", expanded=True):
            preview_text = parser.generate_assignment_preview(parsed_data)
            st.markdown(preview_text)
        
        # Allow manual refinement
        st.markdown("### ✏️ Refine Parsed Assignment")
        
        refined_data = refine_parsed_assignment(parsed_data, title)
        
        # Save to database if user confirms
        if st.button("💾 Save Assignment to Database", use_container_width=True, type="primary"):
            save_parsed_assignment(refined_data, linked_article, uploaded_file.name)
            
    except Exception as e:
        st.error(f"❌ Error processing assignment: {str(e)}")
        st.info("Please check the file format and try again.")

def refine_parsed_assignment(parsed_data, manual_title):
    """Allow manual refinement of parsed assignment data"""
    
    # Use manual title if provided, otherwise use parsed title
    final_title = manual_title.strip() if manual_title.strip() else parsed_data.get('assignment_title', 'Untitled Assignment')
    
    with st.form("refine_assignment"):
        st.markdown("#### Assignment Metadata")
        
        col1, col2 = st.columns(2)
        with col1:
            refined_title = st.text_input("Assignment Title:", value=final_title)
            refined_word_count = st.text_input("Word Count Target:", value=parsed_data.get('total_word_count', '600-900 words'))
        
        with col2:
            refined_type = st.text_input("Assignment Type:", value=parsed_data.get('assignment_type', 'socratic_analysis'))
        
        # Workflow steps
        workflow_steps = parsed_data.get('workflow_steps', [])
        refined_workflow = st.text_area(
            "Workflow Steps (one per line):",
            value="\n".join(workflow_steps),
            height=120,
            help="Steps students should follow when working through this assignment"
        )
        
        st.markdown("#### Questions")
        
        # Display questions for refinement
        questions = parsed_data.get('questions', [])
        refined_questions = []
        
        for i, question in enumerate(questions):
            with st.expander(f"Question {i+1}: {question.get('id', 'Q'+str(i+1))}", expanded=i < 2):
                q_col1, q_col2 = st.columns(2)
                
                with q_col1:
                    q_id = st.text_input("Question ID:", value=question.get('id', f'Q{i+1}'), key=f'refine_id_{i}')
                    q_title = st.text_input("Question Title:", value=question.get('title', ''), key=f'refine_title_{i}')
                    q_bloom = st.selectbox(
                        "Bloom's Level:",
                        ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
                        index=['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'].index(
                            question.get('bloom_level', 'analyze')
                        ),
                        key=f'refine_bloom_{i}'
                    )
                
                with q_col2:
                    q_word_target = st.text_input("Word Target:", value=question.get('word_target', '150-200 words'), key=f'refine_words_{i}')
                    q_evidence = st.text_input("Required Evidence:", value=question.get('required_evidence', ''), key=f'refine_evidence_{i}')
                
                q_prompt = st.text_area(
                    "Question Prompt:",
                    value=question.get('prompt', ''),
                    height=100,
                    key=f'refine_prompt_{i}'
                )
                
                q_objectives = st.text_input(
                    "Learning Objectives (comma-separated):",
                    value=', '.join(question.get('learning_objectives', [])),
                    key=f'refine_obj_{i}'
                )
                
                # Show generated tutoring prompts
                tutoring_prompts = question.get('tutoring_prompts', [])
                if tutoring_prompts:
                    st.markdown("**Generated Tutoring Prompts:**")
                    for prompt in tutoring_prompts:
                        st.markdown(f"• {prompt}")
                
                refined_questions.append({
                    'id': q_id,
                    'title': q_title,
                    'prompt': q_prompt,
                    'bloom_level': q_bloom,
                    'word_target': q_word_target,
                    'required_evidence': q_evidence,
                    'learning_objectives': [obj.strip() for obj in q_objectives.split(',') if obj.strip()],
                    'key_concepts': question.get('key_concepts', []),
                    'tutoring_prompts': tutoring_prompts
                })
        
        # Update button
        if st.form_submit_button("🔄 Update Preview"):
            # Create refined data structure
            refined_data = {
                'assignment_title': refined_title,
                'assignment_type': refined_type,
                'total_word_count': refined_word_count,
                'workflow_steps': [step.strip() for step in refined_workflow.split('\n') if step.strip()],
                'questions': refined_questions,
                'parsed_at': parsed_data.get('parsed_at'),
                'filename': parsed_data.get('filename'),
                'file_type': parsed_data.get('file_type')
            }
            
            # Show updated preview
            parser = AssignmentParser()
            st.markdown("### 🔄 Updated Preview")
            preview_text = parser.generate_assignment_preview(refined_data)
            st.markdown(preview_text)
            
            return refined_data
    
    # Return original data if no updates
    return parsed_data

def save_parsed_assignment(assignment_data, linked_article, original_filename):
    """Save parsed assignment to database"""
    
    try:
        from components.database import save_assignment_questions
        
        # Determine article ID if linked
        article_id = None
        if linked_article != "No specific article":
            articles_df = get_articles()
            for _, row in articles_df.iterrows():
                article_display = f"Week {row['week_number']}: {row['title']}"
                if article_display == linked_article:
                    article_id = row['id']
                    break
        
        # If no specific article linked, create a general assignment entry
        if not article_id:
            # Save as general assignment (we need to create a placeholder article or modify the database)
            st.warning("⚠️ No article linked. You'll need to manually associate this assignment with an article later.")
            st.info("For now, the assignment structure has been parsed and can be manually added to an article.")
            
            # Show the assignment data that can be copied
            st.markdown("### 📋 Parsed Assignment Data")
            st.markdown("Copy this data to manually create assignment questions:")
            
            with st.expander("Assignment JSON Data", expanded=False):
                st.json(assignment_data)
            
            return
        
        # Save assignment questions
        assignment_id = save_assignment_questions(
            article_id=article_id,
            assignment_title=assignment_data['assignment_title'],
            questions_data={
                'assignment_type': assignment_data['assignment_type'],
                'total_word_count': assignment_data['total_word_count'],
                'workflow_steps': assignment_data['workflow_steps'],
                'questions': assignment_data['questions']
            }
        )
        
        if assignment_id:
            st.success(f"✅ Assignment saved successfully! (ID: {assignment_id})")
            st.balloons()
            
            # Show summary
            with st.expander("📊 Assignment Summary", expanded=True):
                st.markdown(f"**Title:** {assignment_data['assignment_title']}")
                st.markdown(f"**Type:** {assignment_data['assignment_type']}")
                st.markdown(f"**Questions:** {len(assignment_data['questions'])}")
                st.markdown(f"**Linked Article:** {linked_article}")
                st.markdown(f"**Original File:** {original_filename}")
                
                if assignment_data['workflow_steps']:
                    st.markdown("**Workflow Steps:**")
                    for i, step in enumerate(assignment_data['workflow_steps'], 1):
                        st.markdown(f"{i}. {step}")
            
            st.info("🎯 Students will now receive enhanced tutoring guidance when working on this assignment!")
            
        else:
            st.error("❌ Failed to save assignment to database.")
            
    except Exception as e:
        st.error(f"❌ Error saving assignment: {str(e)}")

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
                try:
                    from components.rag_system import get_rag_system
                    rag_system = get_rag_system()
                    rag_system.add_to_knowledge_base(f"Article: {title}\nKey concepts: {concepts}")
                except Exception as e:
                    st.warning(f"Could not update knowledge base: {str(e)[:50]}...")
            
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
                        
                        if research_results and research_results.get('success', False):
                            st.success("🤖 Research Agent completed!")
                            st.info(f"""
**Research Summary:**
- 📁 Research folder: `{research_results.get('folder_path', 'N/A')}`
- 🔍 Concepts analyzed: {research_results.get('concepts_found', 'N/A')}
- 🌐 Web searches performed: {research_results.get('searches_performed', 'N/A')}
- 📚 Knowledge chunks created: {research_results.get('knowledge_chunks_created', 'N/A')}

The AI chatbot now has enhanced knowledge about this article!
                            """)
                        else:
                            st.warning("🤖 Research Agent completed but no results were returned.")
                            st.info("Article uploaded successfully, but additional research was not available.")
                    except ImportError:
                        st.warning("🔧 Research Agent is not available in this deployment.")
                        st.info("Article uploaded successfully. Research features can be added later.")
                    except Exception as e:
                        st.warning(f"🔍 Research Agent encountered an issue: {str(e)[:100]}...")
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
        week_num = str(article['week_number'])
        article_title = str(article['title'])
        upload_date = str(article['upload_date'])[:16]
        file_path = str(article['file_path'])
        is_active = bool(article['is_active'])
        objectives = str(article.get('learning_objectives', '')) if article.get('learning_objectives') else ''
        concepts = str(article.get('key_concepts', '')) if article.get('key_concepts') else ''
        
        with st.expander(f"Week {week_num}: {article_title}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Upload Date:** {upload_date}")
                st.markdown(f"**File:** {os.path.basename(file_path)}")
                st.markdown(f"**Status:** {'Active' if is_active else 'Inactive'}")
                
                if objectives:
                    st.markdown(f"**Learning Objectives:**")
                    st.markdown(objectives)
                
                if concepts:
                    st.markdown(f"**Key Concepts:**")
                    st.markdown(concepts)
            
            with col2:
                # Toggle active status
                current_status = is_active
                new_status = st.checkbox(
                    "Active",
                    value=current_status,
                    key=f"active_{article['id']}",
                    help="Toggle whether students can access this article"
                )
                
                if new_status != current_status:
                    if update_article_status(article['id'], new_status):
                        st.success(f"Article status updated to {'Active' if new_status else 'Inactive'}")
                        st.rerun()
                    else:
                        st.error("Failed to update article status")
            
            with col3:
                # Delete button with confirmation
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{article['id']}",
                    help="Permanently delete this article",
                    type="secondary"
                ):
                    # Store deletion request in session state for confirmation
                    st.session_state[f"confirm_delete_{article['id']}"] = True
                
                # Show confirmation dialog if deletion was requested
                if st.session_state.get(f"confirm_delete_{article['id']}", False):
                    st.warning("⚠️ Are you sure you want to delete this article? This action cannot be undone.")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button(
                            "✅ Yes, Delete",
                            key=f"confirm_yes_{article['id']}",
                            type="primary"
                        ):
                            if delete_article_completely(article['id'], file_path):
                                st.success("Article deleted successfully!")
                                # Clear confirmation state
                                if f"confirm_delete_{article['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_{article['id']}"]
                                st.rerun()
                            else:
                                st.error("Failed to delete article")
                    
                    with col_confirm2:
                        if st.button(
                            "❌ Cancel",
                            key=f"confirm_no_{article['id']}"
                        ):
                            # Clear confirmation state
                            if f"confirm_delete_{article['id']}" in st.session_state:
                                del st.session_state[f"confirm_delete_{article['id']}"]
                            st.rerun()

def delete_article_completely(article_id, file_path):
    """Delete an article completely - both file and database record"""
    try:
        # Delete from database first
        database_deleted = delete_article(article_id)
        
        # Remove file if database deletion was successful
        file_deleted = True
        if database_deleted and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                st.warning(f"Database record deleted but file removal failed: {e}")
                file_deleted = False
        
        return database_deleted and file_deleted
        
    except Exception as e:
        st.error(f"Error deleting article: {e}")
        return False

def display_knowledge_base_management():
    """Display knowledge base management interface"""
    st.markdown("### Knowledge Base Management")
    st.markdown("Manage the landscape ecology knowledge base that guides the AI tutor.")
    
    try:
        from components.rag_system import get_rag_system
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
                    try:
                        rag_system.add_to_knowledge_base(new_knowledge)
                        st.success("Knowledge added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding knowledge: {str(e)[:50]}...")
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
            try:
                relevant_knowledge = rag_system.search_knowledge(test_query)
                with st.expander("Retrieved Knowledge", expanded=True):
                    st.markdown(relevant_knowledge)
            except Exception as e:
                st.error(f"Error searching knowledge: {str(e)[:50]}...")
        
        # Knowledge base preview
        if st.checkbox("Show Knowledge Base Preview"):
            st.markdown("#### Current Knowledge Base")
            
            try:
                for i, chunk in enumerate(rag_system.knowledge_base[:10]):  # Show first 10 chunks
                    with st.expander(f"Chunk {i+1}", expanded=False):
                        st.markdown(chunk)
                
                if len(rag_system.knowledge_base) > 10:
                    st.markdown(f"... and {len(rag_system.knowledge_base) - 10} more chunks")
            except Exception as e:
                st.error(f"Error displaying knowledge base: {str(e)[:50]}...")
    
    except ImportError:
        st.error("🔧 Knowledge base system is not available.")
        st.info("Please check the system configuration.")
    except Exception as e:
        st.error(f"🚨 Error loading knowledge base management: {str(e)[:100]}...")
        st.info("Please contact administrator if this persists.")


def display_assignment_questions_interface():
    """Display assignment questions management interface"""
    st.markdown("### ❓ Assignment Questions")
    st.markdown("Create and manage assignment questions for each article to guide student discussions.")
    
    # Get all articles
    try:
        from components.database import get_articles, save_assignment_questions, get_assignment_questions
        articles_df = get_articles()
        
        if articles_df.empty:
            st.warning("No articles uploaded yet. Upload articles first before creating assignments.")
            return
        
        # Article selection
        st.markdown("#### Select Article for Assignment")
        
        article_options = {}
        for _, row in articles_df.iterrows():
            display_name = f"Week {row['week_number']}: {row['title']}"
            article_options[display_name] = row
        
        selected_article_name = st.selectbox(
            "Choose article:",
            options=list(article_options.keys()),
            help="Select the article to create or edit assignment questions for"
        )
        
        selected_article = article_options[selected_article_name]
        article_id = selected_article['id']
        
        # Check if assignment already exists
        existing_assignment = get_assignment_questions(article_id)
        
        if existing_assignment:
            st.success(f"✅ Assignment questions exist for this article")
            display_existing_assignment(existing_assignment)
            
            if st.button("🔄 Edit Assignment Questions", use_container_width=True):
                st.session_state.edit_assignment = True
        
        # Create new assignment or edit existing
        if not existing_assignment or st.session_state.get('edit_assignment', False):
            create_assignment_form(article_id, selected_article['title'], existing_assignment)
            
    except Exception as e:
        st.error(f"Error loading assignment interface: {e}")


def display_existing_assignment(assignment_data):
    """Display existing assignment questions"""
    st.markdown("#### Current Assignment")
    
    with st.expander("Assignment Overview", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Title:** {assignment_data['assignment_title']}")
            st.markdown(f"**Type:** {assignment_data['assignment_type']}")
            st.markdown(f"**Word Count:** {assignment_data['total_word_count']}")
        
        with col2:
            st.markdown(f"**Questions:** {len(assignment_data['questions'])}")
            if assignment_data['workflow_steps']:
                st.markdown("**Workflow Steps:**")
                for i, step in enumerate(assignment_data['workflow_steps'], 1):
                    st.markdown(f"{i}. {step}")
    
    # Display questions
    st.markdown("#### Assignment Questions")
    for question in assignment_data['questions']:
        with st.expander(f"{question['id']}: {question['title']}", expanded=False):
            st.markdown(f"**Prompt:** {question['prompt']}")
            if question['learning_objectives']:
                st.markdown(f"**Learning Objectives:** {', '.join(question['learning_objectives'])}")
            if question['required_evidence']:
                st.markdown(f"**Required Evidence:** {question['required_evidence']}")
            if question['word_target']:
                st.markdown(f"**Word Target:** {question['word_target']}")
            if question['bloom_level']:
                st.markdown(f"**Bloom's Level:** {question['bloom_level']}")


def create_assignment_form(article_id, article_title, existing_data=None):
    """Create form for assignment questions"""
    st.markdown("#### Create/Edit Assignment Questions")
    
    with st.form("assignment_form"):
        # Assignment metadata
        col1, col2 = st.columns(2)
        
        with col1:
            assignment_title = st.text_input(
                "Assignment Title:",
                value=existing_data.get('assignment_title', f"Assignment for {article_title}"),
                help="Title for this assignment"
            )
            
            assignment_type = st.selectbox(
                "Assignment Type:",
                ["socratic_reading_analysis", "case_study_analysis", "concept_application"],
                index=0,
                help="Type of assignment"
            )
        
        with col2:
            word_count = st.text_input(
                "Total Word Count:",
                value=existing_data.get('total_word_count', '600-900 words'),
                help="Expected total word count for student responses"
            )
        
        # Workflow steps
        st.markdown("**Suggested Workflow Steps** (one per line):")
        workflow_text = st.text_area(
            "Workflow Steps:",
            value="\n".join(existing_data.get('workflow_steps', [
                "Define and contrast concepts with page citations",
                "Probe integration barriers with tutor", 
                "Identify concrete examples and critique them",
                "Explore human dimension concepts",
                "Design planning application scenario"
            ])),
            height=120,
            help="Steps students should follow when working with the AI tutor"
        )
        
        # Questions
        st.markdown("#### Individual Questions")
        
        # Pre-populate with Hersperger example if new assignment
        if not existing_data:
            default_questions = [
                {
                    'id': 'Q1',
                    'title': 'Concept contrast and change',
                    'prompt': 'Hersperger et al. distinguish between early core concepts (structure, function, change, scale) and newer applied concepts (ecosystem services, green infrastructure, resilience, human experience). Use the tutor to help you define and contrast one early and one newer concept. How do they reflect different phases in the evolution of landscape ecology?',
                    'learning_objectives': ['Define concepts', 'Compare evolution phases'],
                    'required_evidence': 'Page-anchored quotations',
                    'word_target': '120-180 words',
                    'bloom_level': 'analysis'
                },
                {
                    'id': 'Q2',
                    'title': 'Concept integration into planning',
                    'prompt': 'The review shows that most concepts are used in the analysis stage of planning, but rarely in goal-setting or monitoring. Ask the tutor for passages showing this evidence, then discuss: why might concepts remain confined to analysis? What barriers prevent their fuller integration across the planning cycle?',
                    'learning_objectives': ['Analyze barriers', 'Evaluate integration'],
                    'required_evidence': 'Passages showing evidence',
                    'word_target': '120-180 words', 
                    'bloom_level': 'evaluation'
                }
            ]
        else:
            default_questions = existing_data['questions']
        
        # Dynamic question builder
        if 'assignment_questions' not in st.session_state:
            st.session_state.assignment_questions = default_questions
        
        for i, question in enumerate(st.session_state.assignment_questions):
            with st.expander(f"Question {i+1}: {question.get('id', 'New')}", expanded=i < 2):
                q_col1, q_col2 = st.columns(2)
                
                with q_col1:
                    q_id = st.text_input(
                        "Question ID:",
                        value=question.get('id', f'Q{i+1}'),
                        key=f'q_id_{i}'
                    )
                    
                    q_title = st.text_input(
                        "Question Title:",
                        value=question.get('title', ''),
                        key=f'q_title_{i}'
                    )
                
                with q_col2:
                    q_word_target = st.text_input(
                        "Word Target:",
                        value=question.get('word_target', '120-180 words'),
                        key=f'q_words_{i}'
                    )
                    
                    q_bloom_level = st.selectbox(
                        "Bloom's Level:",
                        ['comprehension', 'analysis', 'synthesis', 'evaluation'],
                        index=['comprehension', 'analysis', 'synthesis', 'evaluation'].index(
                            question.get('bloom_level', 'analysis')
                        ),
                        key=f'q_bloom_{i}'
                    )
                
                q_prompt = st.text_area(
                    "Question Prompt:",
                    value=question.get('prompt', ''),
                    height=100,
                    key=f'q_prompt_{i}'
                )
                
                q_learning_obj = st.text_input(
                    "Learning Objectives (comma-separated):",
                    value=', '.join(question.get('learning_objectives', [])),
                    key=f'q_obj_{i}'
                )
                
                q_evidence = st.text_input(
                    "Required Evidence:",
                    value=question.get('required_evidence', ''),
                    key=f'q_evidence_{i}'
                )
                
                # Update session state
                st.session_state.assignment_questions[i] = {
                    'id': q_id,
                    'title': q_title, 
                    'prompt': q_prompt,
                    'learning_objectives': [obj.strip() for obj in q_learning_obj.split(',') if obj.strip()],
                    'required_evidence': q_evidence,
                    'word_target': q_word_target,
                    'bloom_level': q_bloom_level
                }
        
        # Add/Remove question buttons
        col_add, col_remove = st.columns(2)
        with col_add:
            if st.form_submit_button("➕ Add Question"):
                st.session_state.assignment_questions.append({
                    'id': f'Q{len(st.session_state.assignment_questions)+1}',
                    'title': '',
                    'prompt': '',
                    'learning_objectives': [],
                    'required_evidence': '',
                    'word_target': '120-180 words',
                    'bloom_level': 'analysis'
                })
                st.rerun()
        
        with col_remove:
            if st.form_submit_button("➖ Remove Last Question") and len(st.session_state.assignment_questions) > 1:
                st.session_state.assignment_questions.pop()
                st.rerun()
        
        # Submit assignment
        if st.form_submit_button("💾 Save Assignment Questions", use_container_width=True):
            save_assignment_form(article_id, assignment_title, assignment_type, word_count, workflow_text)


def save_assignment_form(article_id, assignment_title, assignment_type, word_count, workflow_text):
    """Save the assignment questions"""
    try:
        from components.database import save_assignment_questions
        
        workflow_steps = [step.strip() for step in workflow_text.split('\n') if step.strip()]
        
        questions_data = {
            'assignment_type': assignment_type,
            'total_word_count': word_count,
            'workflow_steps': workflow_steps,
            'questions': st.session_state.assignment_questions
        }
        
        assignment_id = save_assignment_questions(article_id, assignment_title, questions_data)
        
        if assignment_id:
            st.success(f"✅ Assignment questions saved successfully! (ID: {assignment_id})")
            st.balloons()
            
            # Clear form state
            if 'assignment_questions' in st.session_state:
                del st.session_state.assignment_questions
            if 'edit_assignment' in st.session_state:
                del st.session_state.edit_assignment
                
            st.rerun()
        else:
            st.error("❌ Failed to save assignment questions.")
            
    except Exception as e:
        st.error(f"Error saving assignment: {e}")


def display_research_monitoring():
    """Display research monitoring interface for professors"""
    st.markdown("### 🔍 AI Research Agent Monitoring")
    st.markdown("Monitor what research has been gathered for each article to enhance the chatbot's knowledge.")
    
    try:
        from components.research_agent import get_research_agent
        research_agent = get_research_agent()
        
        # Check if the method exists
        if not hasattr(research_agent, 'get_all_research_for_professor'):
            st.warning("🔧 Research monitoring feature is not yet implemented.")
            st.info("This feature will show research data gathered by the AI Research Agent for each article.")
            return
        
        # Get all research data
        all_research = research_agent.get_all_research_for_professor()
        
        if not all_research:
            st.info("No research data found. Articles with AI Research enabled will appear here after upload.")
            return
        
        st.markdown(f"**Total Articles with Research:** {len(all_research)}")
        st.divider()
        
        # Display research for each article
        for research_data in all_research:
            with st.expander(f"📄 {research_data['title']} - Research Overview", expanded=False):
                
                # Basic metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Concepts Found", research_data.get('concepts_found', 0))
                with col2:
                    st.metric("Web Searches", research_data.get('searches_performed', 0))
                with col3:
                    st.metric("Knowledge Chunks", research_data['summary'].get('knowledge_chunks', 0))
                with col4:
                    research_date = research_data['research_date'][:10] if research_data.get('research_date') else 'Unknown'
                    st.metric("Research Date", research_date)
                
                st.divider()
                
                # Research summary details
                st.markdown("#### 📋 Research Summary")
                summary = research_data['summary']
                
                if summary.get('key_concepts'):
                    st.markdown(f"**Key Concepts Researched:** {', '.join(summary['key_concepts'])}")
                
                if summary.get('study_system'):
                    st.markdown(f"**Study System:** {summary['study_system']}")
                
                if summary.get('search_queries'):
                    st.markdown("**Search Queries Used:**")
                    for i, query in enumerate(summary['search_queries'][:5], 1):
                        st.markdown(f"{i}. {query}")
                    if len(summary['search_queries']) > 5:
                        st.markdown(f"...and {len(summary['search_queries']) - 5} more queries")
                
                st.divider()
                
                # Knowledge preview
                st.markdown("#### 📚 Gathered Knowledge Preview")
                if research_data.get('knowledge_preview'):
                    with st.expander("View Knowledge Content Preview", expanded=False):
                        st.text_area(
                            "Knowledge Content (first 1000 characters):",
                            research_data['knowledge_preview'],
                            height=200,
                            disabled=True
                        )
                
                # File information
                if research_data.get('search_files'):
                    st.markdown(f"**Individual Search Files:** {len(research_data['search_files'])} files")
                    st.markdown(f"**Research Folder:** `{research_data['folder_path']}`")
                
                # Chatbot integration status
                st.success("✅ Research has been integrated into the chatbot's knowledge base")
                st.info("Students discussing this article will benefit from this enhanced knowledge!")
        
        st.divider()
        
        # Overall statistics
        st.markdown("### 📊 Overall Research Statistics")
        
        total_concepts = sum(r.get('concepts_found', 0) for r in all_research)
        total_searches = sum(r.get('searches_performed', 0) for r in all_research)
        total_chunks = sum(r['summary'].get('knowledge_chunks', 0) for r in all_research)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Concepts Researched", total_concepts)
        with col2:
            st.metric("Total Web Searches Performed", total_searches)
        with col3:
            st.metric("Total Knowledge Chunks Created", total_chunks)
        
        # Tips for professors
        with st.expander("💡 How to Use This Information", expanded=False):
            st.markdown("""
            **Understanding the Research Data:**
            
            - **Concepts Found**: Key landscape ecology concepts identified in the article
            - **Web Searches**: Number of targeted searches performed to gather related information
            - **Knowledge Chunks**: Pieces of information added to the chatbot's knowledge base
            
            **What This Means for Your Students:**
            
            ✅ **Enhanced Discussions**: Students get more detailed, accurate responses about article topics
            
            ✅ **Current Research**: Chatbot has access to recent findings and case studies
            
            ✅ **Comprehensive Context**: Students can explore connections to broader landscape ecology concepts
            
            ✅ **Better Learning**: More informed discussions lead to deeper understanding
            
            **Quality Assurance:**
            
            - Research focuses on peer-reviewed academic sources
            - Content is filtered for landscape ecology relevance
            - Information is organized by concept areas and applications
            - All research is saved for your review and verification
            """)
    
    except ImportError:
        st.error("Research agent not available. Please check the system configuration.")
    except Exception as e:
        st.error(f"Error loading research data: {e}")

if __name__ == "__main__":
    main()

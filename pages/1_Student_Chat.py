import streamlit as st
import os
import time
from datetime import datetime
from components.auth import is_authenticated, get_current_user
from components.chat_engine import SocraticChatEngine, initialize_chat_session, add_message, get_chat_history, calculate_session_duration
from components.rag_system import get_rag_system, get_article_processor
from components.database import save_chat_session, get_articles, get_assignment_questions, get_student_assignment_progress, update_student_assignment_progress, DATABASE_PATH
from components.student_engagement import StudentEngagementSystem
from components.assessment_quality import AssessmentQualitySystem
from components.focus_manager import FocusManager
import PyPDF2
import io

st.set_page_config(page_title="Student Chat", page_icon="📖", layout="wide")

def generate_assignment_aware_response(user_input, chat_history, article_context, relevant_knowledge, assignment_context, chat_engine):
    """Generate assignment-focused responses that guide students through structured questions"""
    
    current_question_details = assignment_context.get('current_question_details', {})
    current_question_id = assignment_context.get('current_question')
    completed_questions = assignment_context.get('completed_questions', [])
    all_questions = assignment_context.get('all_questions', [])
    
    # Initialize advanced focus manager
    focus_manager = FocusManager()
    
    # Analyze conversation drift with advanced multi-factor analysis
    drift_analysis = focus_manager.analyze_conversation_drift(
        user_input=user_input,
        chat_history=chat_history,
        current_question=current_question_details,
        assignment_context=assignment_context
    )
    
    # Check if intervention is needed
    if focus_manager.should_intervene(drift_analysis) and current_question_details:
        # Get current student progress for context
        student_progress = assignment_context.get('progress', {})
        
        # Generate contextual redirection response
        redirect_response = focus_manager.generate_redirection_response(
            drift_analysis=drift_analysis,
            current_question=current_question_details,
            assignment_context=assignment_context,
            student_progress=student_progress
        )
        
        # Add drift analysis info for debugging (can be removed in production)
        if st.session_state.get('debug_mode', False):
            with st.expander("🔍 Focus Analysis Debug", expanded=False):
                st.json({
                    "drift_score": drift_analysis["drift_score"],
                    "drift_type": drift_analysis["drift_type"],
                    "recommendation": drift_analysis["recommendation"],
                    "confidence": drift_analysis["confidence"],
                    "indicators": drift_analysis["indicators"][:3],  # Show first 3
                    "focus_signals": drift_analysis["focus_signals"][:3]
                })
        
        return redirect_response
    
    # Build enhanced context for AI
    enhanced_context = f"""
ASSIGNMENT CONTEXT:
- Assignment: {assignment_context.get('assignment_title', 'Study Questions')}
- Target Length: {assignment_context.get('total_word_count', 'Not specified')}
- Current Focus: Question {current_question_id}
- Question Title: {current_question_details.get('title', 'No title')}
- Question Prompt: {current_question_details.get('prompt', 'No prompt')}
- Required Evidence: {current_question_details.get('required_evidence', 'No specific evidence required')}
- Bloom Level: {current_question_details.get('bloom_level', 'Not specified')}
- Completed Questions: {', '.join(completed_questions) if completed_questions else 'None yet'}

TUTORING GUIDANCE:
{chr(10).join('- ' + prompt for prompt in current_question_details.get('tutoring_prompts', []))}

COACHING GUIDELINES:
1. Keep the conversation focused on the current question (drift score: {drift_analysis['drift_score']:.2f})
2. Guide the student to find specific evidence from the article
3. Ask probing questions that develop critical thinking
4. Use the tutoring prompts above to guide your questioning strategy
5. Help synthesize findings toward the writing goal
6. Encourage academic analysis over summary
"""
    
    # Check if student is ready to move to next question
    message_count_on_current = len([msg for msg in chat_history if current_question_id in msg.get('content', '')])
    
    if message_count_on_current > 8:  # Substantial discussion on current question
        # Check if student has good evidence and understanding
        evidence_keywords = ['evidence', 'example', 'study shows', 'data', 'result', 'finding']
        has_evidence = any(keyword in user_input.lower() for keyword in evidence_keywords)
        
        if has_evidence:
            # Suggest moving to next question
            next_question_index = next((i for i, q in enumerate(all_questions) if q.get('id') == current_question_id), -1)
            if next_question_index >= 0 and next_question_index + 1 < len(all_questions):
                next_question = all_questions[next_question_index + 1]
                
                transition_response = f"""Excellent work on {current_question_id}! You've gathered solid evidence and shown good analytical thinking.

Let's move forward to **{next_question['id']}: {next_question.get('title', 'Next Question')}**

{next_question.get('prompt', 'No prompt available')}

{f"**Required evidence:** {next_question.get('required_evidence', 'Use article content')}" if next_question.get('required_evidence') else ""}

How does the article address this question? What specific information did you find relevant?"""
                
                return transition_response
    
    # Generate standard Socratic response with assignment context
    base_response = chat_engine.generate_socratic_response(
        user_input, 
        chat_history,
        article_context,
        relevant_knowledge
    )
    
    # Enhance with assignment-specific guidance
    if current_question_details and current_question_id not in user_input:
        assignment_reminder = f"""

**Remember:** We're working on {current_question_id}: {current_question_details.get('title', 'Current Question')}
Focus on finding specific evidence from the article that helps answer this question."""
        
        return base_response + assignment_reminder
    
    return base_response

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
                    # Load assignment questions if they exist for this article
                    assignment_questions = get_assignment_questions(selected_article['id'])
                    if assignment_questions:
                        st.session_state.assignment_questions = assignment_questions
                        st.session_state.current_article_id = selected_article['id']
                        
                        # Load student progress for this assignment
                        if 'assignment_id' in assignment_questions:
                            progress = get_student_assignment_progress(user['id'], assignment_questions['assignment_id'])
                            st.session_state.assignment_progress = progress
                        
                        st.success("🎉 Article and assignment questions loaded successfully!")
                        st.info(f"📝 Assignment: {assignment_questions.get('assignment_title', 'Study Questions')} available")
                    else:
                        st.success("🎉 Article loaded successfully!")
                        # Clear any previous assignment context
                        if 'assignment_questions' in st.session_state:
                            del st.session_state['assignment_questions']
                        if 'assignment_progress' in st.session_state:
                            del st.session_state['assignment_progress']
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Article loading failed. Please try a different article or contact your instructor.")
        else:
            st.warning("No articles available. Please contact your instructor.")
            
        # Display assignment questions if available
        assignment_questions = st.session_state.get('assignment_questions')
        if assignment_questions:
            st.markdown("### 📝 Assignment Questions")
            
            # Show assignment overview
            st.markdown(f"**{assignment_questions.get('assignment_title', 'Study Questions')}**")
            st.caption(f"Word Target: {assignment_questions.get('total_word_count', 'Not specified')}")
            
            # Debug mode toggle (for development/testing)
            if user['type'] == 'Professor':
                with st.expander("🔧 Debug Options", expanded=False):
                    st.session_state['debug_mode'] = st.checkbox(
                        "🔍 Show Focus Analysis", 
                        value=st.session_state.get('debug_mode', False),
                        help="Show detailed focus analysis for each student message (Professor only)"
                    )
            
            # Show workflow steps if available
            workflow_steps = assignment_questions.get('workflow_steps', [])
            if workflow_steps:
                st.markdown("**Workflow Steps:**")
                for i, step in enumerate(workflow_steps, 1):
                    st.markdown(f"{i}. {step}")
            
            # Show progress if available
            progress = st.session_state.get('assignment_progress', {})
            if progress:
                completed_questions = progress.get('questions_completed', [])
                total_questions = len(assignment_questions.get('questions', []))
                
                if total_questions > 0:
                    progress_pct = len(completed_questions) / total_questions
                    st.progress(progress_pct, f"Progress: {len(completed_questions)}/{total_questions} questions")
                
                current_question = progress.get('current_question')
                if current_question:
                    st.info(f"🎯 Current Focus: Question {current_question}")
            
            # Show individual questions in expandable format
            questions = assignment_questions.get('questions', [])
            if questions:
                st.markdown("**Questions:**")
                for question in questions:
                    question_id = question.get('id', 'Q?')
                    question_title = question.get('title', 'Untitled Question')
                    
                    # Check if this question is completed
                    is_completed = question_id in progress.get('questions_completed', [])
                    status_icon = "✅" if is_completed else "📝"
                    
                    with st.expander(f"{status_icon} {question_id}: {question_title}", expanded=False):
                        st.markdown(f"**{question.get('prompt', 'No prompt available')}**")
                        
                        word_target = question.get('word_target', '')
                        if word_target:
                            st.caption(f"Word target: {word_target}")
                        
                        bloom_level = question.get('bloom_level', '')
                        if bloom_level:
                            st.caption(f"Cognitive level: {bloom_level}")
                        
                        required_evidence = question.get('required_evidence', '')
                        if required_evidence:
                            st.markdown(f"**Required evidence:** {required_evidence}")
        
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
            # Check if there are assignment questions for structured guidance
            assignment_questions = st.session_state.get('assignment_questions')
            
            if assignment_questions:
                # Assignment-aware initial message
                assignment_title = assignment_questions.get('assignment_title', 'Study Questions')
                questions = assignment_questions.get('questions', [])
                workflow_steps = assignment_questions.get('workflow_steps', [])
                
                # Get student's current progress
                progress = st.session_state.get('assignment_progress', {})
                current_question = progress.get('current_question')
                completed_questions = progress.get('questions_completed', [])
                
                # Determine which question to focus on
                if not current_question and questions:
                    # Start with the first question
                    next_question_id = questions[0].get('id', 'Q1')
                    current_question = next_question_id
                    
                    # Update progress
                    if 'assignment_id' in assignment_questions:
                        update_student_assignment_progress(
                            user['id'], 
                            assignment_questions['assignment_id'], 
                            current_question=current_question
                        )
                        st.session_state.assignment_progress = {'current_question': current_question, 'questions_completed': completed_questions}
                
                intro_message = f"""
Hello! I'm your Landscape Ecology AI tutor. I see we're working on "{current_article['title']}" with the assignment: **{assignment_title}**.

This is a structured writing assignment designed to help you develop critical thinking skills. I'm here to guide you through each question systematically.

**Assignment Overview:**
• Target length: {assignment_questions.get('total_word_count', '600-900 words')}
• Questions to address: {len(questions)}
• This is analytical writing, not just summary

**Your Workflow:**
"""
                
                if workflow_steps:
                    for i, step in enumerate(workflow_steps, 1):
                        intro_message += f"{i}. {step}\n"
                else:
                    intro_message += """1. Read the article thoroughly
2. Work through each question systematically
3. Gather evidence and citations
4. Develop your analytical responses
5. Synthesize into coherent writing"""
                
                if current_question and questions:
                    # Find the current question details
                    current_q_details = None
                    for q in questions:
                        if q.get('id') == current_question:
                            current_q_details = q
                            break
                    
                    intro_message += f"""

**Let's start with {current_question}:**
"""
                    if current_q_details:
                        intro_message += f"""
**{current_q_details.get('title', 'Question')}**

{current_q_details.get('prompt', 'No prompt available')}
"""
                        
                        required_evidence = current_q_details.get('required_evidence', '')
                        if required_evidence:
                            intro_message += f"""
**Evidence needed:** {required_evidence}
"""
                    
                    intro_message += """
Have you read the article? Let's discuss what you found relevant to this first question. What aspects of the article relate to this question?"""
                else:
                    intro_message += """

Have you finished reading the article? Let's start working through the assignment questions systematically."""
            else:
                # Generic intro message for articles without assignments
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
        
        # Get assignment context for enhanced response generation
        assignment_questions = st.session_state.get('assignment_questions')
        assignment_progress = st.session_state.get('assignment_progress', {})
        assignment_context = None
        
        if assignment_questions:
            current_question = assignment_progress.get('current_question')
            questions = assignment_questions.get('questions', [])
            
            # Build assignment context
            assignment_context = {
                'assignment_title': assignment_questions.get('assignment_title'),
                'current_question': current_question,
                'all_questions': questions,
                'workflow_steps': assignment_questions.get('workflow_steps', []),
                'total_word_count': assignment_questions.get('total_word_count'),
                'completed_questions': assignment_progress.get('questions_completed', [])
            }
            
            # Find current question details
            if current_question:
                for q in questions:
                    if q.get('id') == current_question:
                        assignment_context['current_question_details'] = q
                        break
        
        # Check if user is seeking direct answers
        if chat_engine.detect_answer_seeking(user_input):
            bot_response = chat_engine.redirect_answer_seeking()
        else:
            # Get relevant knowledge
            relevant_knowledge = rag_system.search_knowledge(user_input)
            article_context = article_processor.get_article_context()
            
            # Generate assignment-aware Socratic response
            if assignment_context:
                bot_response = generate_assignment_aware_response(
                    user_input,
                    get_chat_history(),
                    article_context,
                    relevant_knowledge,
                    assignment_context,
                    chat_engine
                )
            else:
                # Generate standard Socratic response
                bot_response = chat_engine.generate_socratic_response(
                    user_input, 
                    get_chat_history(),
                    article_context,
                    relevant_knowledge
                )
        
        # Add bot response
        add_message("assistant", bot_response)
        
        # Update assignment progress if applicable
        if assignment_context and 'assignment_id' in assignment_questions:
            assignment_id = assignment_questions['assignment_id']
            current_question = assignment_context.get('current_question')
            
            # Check if student provided substantial evidence/analysis (indicating readiness to progress)
            evidence_keywords = ['evidence', 'example', 'study shows', 'data', 'result', 'finding', 'demonstrates', 'indicates']
            analysis_keywords = ['because', 'therefore', 'analysis', 'conclude', 'suggest', 'implies', 'relationship']
            
            has_evidence = any(keyword in user_input.lower() for keyword in evidence_keywords)
            has_analysis = any(keyword in user_input.lower() for keyword in analysis_keywords)
            is_substantial = len(user_input.split()) > 20  # More than 20 words
            
            if has_evidence and has_analysis and is_substantial and current_question:
                # Check if this question should be marked as progressing well
                current_progress = st.session_state.get('assignment_progress', {})
                evidence_found = current_progress.get('evidence_found', [])
                
                # Add evidence item
                evidence_item = f"{current_question}: {user_input[:100]}..."
                if evidence_item not in evidence_found:
                    update_student_assignment_progress(
                        user['id'], 
                        assignment_id, 
                        current_question=current_question,
                        evidence_item=evidence_item
                    )
                    
                    # Update session state
                    updated_progress = get_student_assignment_progress(user['id'], assignment_id)
                    st.session_state.assignment_progress = updated_progress
        
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

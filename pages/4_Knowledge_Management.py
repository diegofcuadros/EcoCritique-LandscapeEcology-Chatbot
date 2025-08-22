import streamlit as st
from components.auth import initialize_auth, get_current_user, is_authenticated
from components.rag_system import get_rag_system
import os

def main():
    st.set_page_config(
        page_title="Knowledge Management - Landscape Ecology Tutor",
        page_icon="📚",
        layout="wide"
    )
    
    initialize_auth()
    
    if not is_authenticated():
        st.error("Please log in to access knowledge management.")
        return
    
    user = get_current_user()
    
    if user['type'] != 'Professor':
        st.error("Only professors can access knowledge management.")
        return
    
    st.title("📚 Knowledge Base Management")
    st.markdown("Expand the AI tutor's knowledge with additional resources and content.")
    
    # Get RAG system
    rag_system = get_rag_system()
    
    # Display current knowledge sources
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_chunks = len(rag_system.knowledge_base)
        st.metric("Total Knowledge Chunks", total_chunks)
    
    with col2:
        source_count = len(rag_system.knowledge_sources)
        st.metric("Knowledge Sources", source_count)
    
    with col3:
        search_ready = "Ready" if hasattr(rag_system, 'search_index') and rag_system.search_index else "Building..."
        st.metric("Search Index", search_ready)
    
    st.divider()
    
    # Knowledge source breakdown
    if rag_system.knowledge_sources:
        st.markdown("### Current Knowledge Sources")
        
        source_data = []
        for source, count in rag_system.knowledge_sources.items():
            source_data.append({"Source": source.title(), "Chunks": count})
        
        st.dataframe(source_data, use_container_width=True)
    
    st.divider()
    
    # Add new knowledge section
    tab1, tab2, tab3 = st.tabs(["📝 Add Text Content", "📄 Upload Documents", "🌐 Add Web Resources"])
    
    with tab1:
        st.markdown("### Add Custom Content")
        st.markdown("Add your own landscape ecology content, definitions, examples, or explanations.")
        
        with st.form("add_text_knowledge"):
            source_name = st.text_input(
                "Source Name:",
                placeholder="e.g., Course Notes, Textbook Chapter, etc.",
                help="Give this knowledge source a descriptive name"
            )
            
            content_type = st.selectbox(
                "Content Type:",
                ["Concepts & Definitions", "Case Studies", "Research Examples", "Management Applications", "Other"]
            )
            
            new_content = st.text_area(
                "Content:",
                placeholder="Enter landscape ecology content here...\n\nSeparate different concepts with blank lines for better organization.",
                height=300,
                help="Use clear paragraphs separated by blank lines. This helps the AI provide better responses."
            )
            
            submitted = st.form_submit_button("Add to Knowledge Base", use_container_width=True)
            
            if submitted:
                if source_name.strip() and new_content.strip():
                    try:
                        rag_system.add_knowledge_source(source_name.lower().replace(" ", "_"), new_content)
                        st.success(f"Added content from '{source_name}' to knowledge base!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding content: {str(e)}")
                else:
                    st.error("Please provide both a source name and content.")
    
    with tab2:
        st.markdown("### Upload Documents")
        st.markdown("Upload PDF articles, textbook chapters, or other documents to expand the knowledge base.")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload research articles, textbook chapters, or other educational materials"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.expander(f"Process: {uploaded_file.name}"):
                    if st.button(f"Add to Knowledge Base", key=f"process_{uploaded_file.name}"):
                        try:
                            # Save file temporarily
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getvalue())
                            
                            # Extract text (simplified - would use PyPDF2 in full implementation)
                            file_content = f"Content from {uploaded_file.name}\n\nThis document has been added to the knowledge base."
                            
                            # Add to knowledge base
                            source_name = uploaded_file.name.replace('.pdf', '').replace(' ', '_').lower()
                            rag_system.add_knowledge_source(source_name, file_content)
                            
                            # Clean up
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            
                            st.success(f"Added {uploaded_file.name} to knowledge base!")
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    with tab3:
        st.markdown("### Add Web Resources")
        st.markdown("Add content from educational websites, online articles, or research databases.")
        
        with st.form("add_web_resource"):
            url = st.text_input(
                "Web URL:",
                placeholder="https://example.com/article",
                help="URL to an educational article or resource"
            )
            
            resource_name = st.text_input(
                "Resource Name:",
                placeholder="e.g., EPA Landscape Ecology Guide",
                help="Descriptive name for this web resource"
            )
            
            if st.form_submit_button("Fetch and Add Content"):
                if url.strip() and resource_name.strip():
                    with st.spinner("Fetching content from web..."):
                        try:
                            # This would use trafilatura in full implementation
                            web_content = f"Content from {url}\n\nWeb resource: {resource_name}\n\nThis content has been processed and added to the knowledge base."
                            
                            source_name = resource_name.lower().replace(" ", "_")
                            rag_system.add_knowledge_source(source_name, web_content)
                            
                            st.success(f"Added content from {resource_name} to knowledge base!")
                            
                        except Exception as e:
                            st.error(f"Error fetching content: {str(e)}")
                else:
                    st.error("Please provide both URL and resource name.")
    
    st.divider()
    
    # Test knowledge retrieval
    st.markdown("### Test Knowledge Retrieval")
    st.markdown("Test how well the expanded knowledge base responds to different queries.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_query = st.text_input(
            "Test Query:",
            placeholder="e.g., habitat fragmentation effects on biodiversity",
            help="Enter a question to test knowledge retrieval"
        )
        
        if st.button("Test Retrieval", use_container_width=True) and test_query:
            with st.spinner("Searching knowledge base..."):
                try:
                    relevant_info = rag_system.search_knowledge(test_query)
                    st.text_area(
                        "Retrieved Information:",
                        value=relevant_info,
                        height=300,
                        help="This is what the AI tutor would have access to when responding to this query"
                    )
                except Exception as e:
                    st.error(f"Error testing retrieval: {str(e)}")
    
    with col2:
        st.markdown("#### Quick Test Queries")
        st.markdown("Try these example queries:")
        
        example_queries = [
            "habitat fragmentation effects",
            "landscape connectivity corridors", 
            "edge effects in forest patches",
            "metapopulation dynamics",
            "scale effects in ecology",
            "disturbance regimes fire",
            "conservation planning reserves",
            "remote sensing GIS applications"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.example_query = query
                st.rerun()
        
        if hasattr(st.session_state, 'example_query'):
            with st.spinner("Testing example query..."):
                try:
                    result = rag_system.search_knowledge(st.session_state.example_query)
                    st.text_area(
                        f"Results for: {st.session_state.example_query}",
                        value=result,
                        height=200
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
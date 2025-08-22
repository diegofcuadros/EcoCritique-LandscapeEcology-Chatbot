import streamlit as st
import os
import json
from datetime import datetime
from components.auth import initialize_auth, get_current_user, is_authenticated
from components.research_agent import get_research_agent

def main():
    st.set_page_config(
        page_title="Research Manager - Landscape Ecology Tutor",
        page_icon="🔬",
        layout="wide"
    )
    
    initialize_auth()
    
    if not is_authenticated():
        st.error("Please log in to access research management.")
        return
    
    user = get_current_user()
    
    if user['type'] != 'Professor':
        st.error("Only professors can access research management.")
        return
    
    st.title("🔬 AI Research Manager")
    st.markdown("View and manage AI-researched information for uploaded articles.")
    
    research_agent = get_research_agent()
    
    # Get list of researched articles
    researched_articles = research_agent.list_researched_articles()
    
    if not researched_articles:
        st.info("📄 No articles have been researched yet. Upload an article with AI Research enabled to get started!")
        return
    
    # Display overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Articles Researched", len(researched_articles))
    
    with col2:
        total_concepts = sum(article['concepts_found'] for article in researched_articles)
        st.metric("Total Concepts Analyzed", total_concepts)
    
    with col3:
        total_searches = sum(article['searches_performed'] for article in researched_articles)
        st.metric("Web Searches Performed", total_searches)
    
    st.divider()
    
    # Article selection and detailed view
    st.markdown("### 📋 Researched Articles")
    
    # Create a selectbox for articles
    article_options = {
        f"{article['title']} (Week {article['article_id'][:5]})": article
        for article in researched_articles
    }
    
    selected_article_key = st.selectbox(
        "Select an article to view research details:",
        list(article_options.keys())
    )
    
    if selected_article_key:
        selected_article = article_options[selected_article_key]
        
        st.markdown(f"### 📖 Research Details: {selected_article['title']}")
        
        # Display article info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Research Date", selected_article['research_date'][:10])
        
        with col2:
            st.metric("Concepts Analyzed", selected_article['concepts_found'])
        
        with col3:
            st.metric("Web Searches", selected_article['searches_performed'])
        
        # Load detailed research data
        folder_path = selected_article['folder_path']
        summary_file = os.path.join(folder_path, "research_summary.json")
        
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    research_data = json.load(f)
                
                # Display tabs for different aspects of research
                tab1, tab2, tab3, tab4 = st.tabs(["🎯 Analysis", "🔍 Search Queries", "📚 Gathered Knowledge", "📁 Files"])
                
                with tab1:
                    st.markdown("#### Article Analysis")
                    
                    analysis = research_data['analysis']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Key Concepts Found:**")
                        for concept in analysis['key_concepts']:
                            st.write(f"• {concept.replace('_', ' ').title()}")
                        
                        st.markdown("**Study System:**")
                        st.write(analysis['study_system'])
                    
                    with col2:
                        st.markdown("**Methods Identified:**")
                        if analysis['methods']:
                            for method in analysis['methods']:
                                st.write(f"• {method}")
                        else:
                            st.write("No specific methods identified")
                        
                        st.markdown("**Temporal Aspects:**")
                        if analysis['temporal_aspects']:
                            for aspect in analysis['temporal_aspects']:
                                st.write(f"• {aspect}")
                        else:
                            st.write("No temporal aspects identified")
                
                with tab2:
                    st.markdown("#### Search Queries Performed")
                    
                    for i, query in enumerate(research_data['search_queries'], 1):
                        st.write(f"{i}. **{query}**")
                
                with tab3:
                    st.markdown("#### Gathered Knowledge")
                    
                    if 'organized_knowledge' in research_data:
                        for i, chunk in enumerate(research_data['organized_knowledge'][:5], 1):  # Show first 5 chunks
                            with st.expander(f"Knowledge Chunk {i}"):
                                st.text_area(
                                    f"Chunk {i}",
                                    value=chunk,
                                    height=200,
                                    key=f"chunk_{i}_{selected_article['article_id']}"
                                )
                        
                        if len(research_data['organized_knowledge']) > 5:
                            st.info(f"Showing first 5 of {len(research_data['organized_knowledge'])} knowledge chunks. View all files in the article folder for complete information.")
                    
                    # Show gathered knowledge file content
                    knowledge_file = os.path.join(folder_path, "gathered_knowledge.txt")
                    if os.path.exists(knowledge_file):
                        st.markdown("#### Complete Gathered Knowledge")
                        
                        try:
                            with open(knowledge_file, 'r', encoding='utf-8') as f:
                                knowledge_content = f.read()
                            
                            st.text_area(
                                "Complete Knowledge (first 2000 characters)",
                                value=knowledge_content[:2000] + ("..." if len(knowledge_content) > 2000 else ""),
                                height=400,
                                key=f"full_knowledge_{selected_article['article_id']}"
                            )
                            
                            if st.button("📥 Download Complete Knowledge File"):
                                st.download_button(
                                    label="Download gathered_knowledge.txt",
                                    data=knowledge_content,
                                    file_name=f"knowledge_{selected_article['article_id']}.txt",
                                    mime="text/plain"
                                )
                        except Exception as e:
                            st.error(f"Error reading knowledge file: {str(e)}")
                
                with tab4:
                    st.markdown("#### Research Files")
                    st.markdown(f"**Folder Location:** `{folder_path}`")
                    
                    # List all files in the research folder
                    if os.path.exists(folder_path):
                        files = os.listdir(folder_path)
                        
                        st.markdown("**Files Created:**")
                        for file in sorted(files):
                            file_path = os.path.join(folder_path, file)
                            file_size = os.path.getsize(file_path)
                            
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.write(f"📄 {file}")
                            
                            with col2:
                                st.write(f"{file_size} bytes")
                            
                            with col3:
                                if st.button("📥", key=f"download_{file}", help=f"Download {file}"):
                                    try:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            file_content = f.read()
                                        
                                        st.download_button(
                                            label=f"Download {file}",
                                            data=file_content,
                                            file_name=file,
                                            mime="text/plain",
                                            key=f"download_button_{file}"
                                        )
                                    except Exception as e:
                                        st.error(f"Error downloading {file}: {str(e)}")
                    
                    # Option to re-run research
                    st.divider()
                    st.markdown("#### Research Actions")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔄 Re-run Research", help="Run the research agent again for this article"):
                            st.info("Re-running research would require the original article content. This feature could be implemented with article storage.")
                    
                    with col2:
                        if st.button("🗑️ Delete Research", help="Delete all research data for this article"):
                            if st.checkbox("Confirm deletion", key=f"confirm_delete_{selected_article['article_id']}"):
                                try:
                                    import shutil
                                    shutil.rmtree(folder_path)
                                    st.success("Research data deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting research data: {str(e)}")
            
            except Exception as e:
                st.error(f"Error loading research data: {str(e)}")
        
        else:
            st.error("Research summary file not found.")
    
    st.divider()
    
    # Research statistics and insights
    st.markdown("### 📊 Research Insights")
    
    if researched_articles:
        # Analyze research patterns
        all_concepts = []
        for article in researched_articles:
            # Load detailed data to get concepts
            summary_file = os.path.join(article['folder_path'], "research_summary.json")
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_concepts.extend(data['analysis']['key_concepts'])
            except:
                continue
        
        if all_concepts:
            from collections import Counter
            concept_counts = Counter(all_concepts)
            
            st.markdown("#### Most Common Research Concepts")
            
            # Display top concepts
            for concept, count in concept_counts.most_common(10):
                st.write(f"• **{concept.replace('_', ' ').title()}**: {count} articles")
        
        # Research coverage metrics
        total_articles = len(researched_articles)
        avg_concepts = sum(article['concepts_found'] for article in researched_articles) / total_articles
        avg_searches = sum(article['searches_performed'] for article in researched_articles) / total_articles
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Concepts per Article", f"{avg_concepts:.1f}")
        
        with col2:
            st.metric("Average Searches per Article", f"{avg_searches:.1f}")

if __name__ == "__main__":
    main()
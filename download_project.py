import streamlit as st
import os
import tarfile
import zipfile
from io import BytesIO

st.set_page_config(page_title="Download Complete Project", page_icon="📁")

st.title("📁 Download Complete Socratic Chatbot Project")

st.markdown("""
This page allows you to download the complete Socratic AI Chatbot project including all components:

- **Core Application** (`app.py`, pages, components)
- **AI Systems** (chat engine, RAG system, assessment quality)
- **Student Engagement** (progress tracking, badges, concept mapping)
- **Professor Tools** (dashboard, grading, reports)
- **Knowledge Base** (landscape ecology content)
- **Research Agent** (intelligent web search)
""")

# Check if archive exists
if os.path.exists("socratic_chatbot_complete.tar.gz"):
    # Get file size
    file_size = os.path.getsize("socratic_chatbot_complete.tar.gz")
    file_size_mb = file_size / (1024 * 1024)
    
    st.success(f"✅ Project archive ready! Size: {file_size_mb:.1f} MB")
    
    # Read the tar.gz file
    with open("socratic_chatbot_complete.tar.gz", "rb") as f:
        archive_data = f.read()
    
    # Download button for tar.gz
    st.download_button(
        label="📦 Download Complete Project (.tar.gz)",
        data=archive_data,
        file_name="socratic_chatbot_complete.tar.gz",
        mime="application/gzip",
        use_container_width=True
    )
    
    st.divider()
    
    # Create ZIP version as alternative
    st.markdown("### Alternative: ZIP Format")
    
    if st.button("🔄 Convert to ZIP format", use_container_width=True):
        with st.spinner("Converting to ZIP..."):
            # Create ZIP from tar.gz contents
            zip_buffer = BytesIO()
            
            with tarfile.open("socratic_chatbot_complete.tar.gz", "r:gz") as tar:
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for member in tar.getmembers():
                        if member.isfile():
                            # Extract file from tar
                            f = tar.extractfile(member)
                            if f:
                                # Add to zip
                                zipf.writestr(member.name, f.read())
            
            zip_buffer.seek(0)
            zip_data = zip_buffer.getvalue()
            
            st.download_button(
                label="📦 Download Complete Project (.zip)",
                data=zip_data,
                file_name="socratic_chatbot_complete.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    st.divider()
    
    # Show archive contents
    st.markdown("### 📋 Archive Contents")
    
    if st.button("👁️ View Archive Contents", use_container_width=True):
        with tarfile.open("socratic_chatbot_complete.tar.gz", "r:gz") as tar:
            members = tar.getmembers()
            
            st.markdown(f"**Total Files:** {len(members)}")
            
            # Group by directory
            dirs = {}
            for member in members:
                if member.isfile():
                    dir_name = os.path.dirname(member.name) or "Root"
                    if dir_name not in dirs:
                        dirs[dir_name] = []
                    dirs[dir_name].append(os.path.basename(member.name))
            
            for dir_name, files in sorted(dirs.items()):
                with st.expander(f"📁 {dir_name} ({len(files)} files)"):
                    for file in sorted(files):
                        st.text(f"  📄 {file}")

else:
    st.error("❌ Project archive not found. Please wait while it's being created...")
    
    if st.button("🔄 Refresh Page", use_container_width=True):
        st.rerun()

st.divider()

st.markdown("""
### 📚 What's Included

Your complete Socratic AI Chatbot system includes:

#### **🎯 Core Features**
- Socratic dialogue engine for guided learning
- RAG (Retrieval-Augmented Generation) system
- Article processing and analysis
- Student authentication and session management

#### **📈 Student Engagement**
- Visual progress tracking through cognitive levels
- Interactive concept mapping
- Achievement badge system (6 different badges)
- Peer learning insights with question sharing

#### **🎓 Assessment Quality**
- Automated rubric scoring (5 criteria)
- Participation quality metrics
- Weekly progress reports
- Grade suggestions and analytics

#### **👨‍🏫 Professor Tools**
- Comprehensive dashboard with analytics
- Session monitoring and transcript viewing
- Automated report generation
- Excel export for grading

#### **🔬 AI Research Agent**
- Intelligent web search for article context
- Knowledge synthesis and summaries
- Multi-source information gathering
- Real-time research capabilities

#### **🗄️ Technical Components**
- SQLite database with full schema
- Streamlit multi-page application
- Environment configuration
- Knowledge base and prompts
- Research data and summaries

### 🚀 Setup Instructions

1. **Extract** the downloaded archive
2. **Install** Python dependencies: `pip install -r requirements.txt`
3. **Set** your `GROQ_API_KEY` environment variable
4. **Run** the application: `streamlit run app.py`
5. **Access** at `http://localhost:8501`

The system is ready to handle 40+ students with full engagement tracking and automated assessment!
""")
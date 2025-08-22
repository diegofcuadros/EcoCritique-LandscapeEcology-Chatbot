# Landscape Ecology Socratic Chatbot

## Overview

This is a Streamlit-based educational application designed for landscape ecology courses. The system provides an AI-powered Socratic chatbot that guides students through critical analysis of academic articles. Students can upload and discuss research papers with an intelligent tutor that uses progressive questioning techniques to deepen understanding across four cognitive levels: comprehension, analysis, synthesis, and evaluation. The professor can manage weekly article uploads, monitor student interactions, and export data for grading purposes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Multi-Page Application**: Built using Streamlit's native page system with separate interfaces for students, professors, and article management
- **Three Main Interfaces**: Student chat interface, professor dashboard for analytics, and article upload/management system
- **Session-Based Authentication**: Simple role-based access control with weekly access codes for students and password authentication for professors
- **Responsive Layout**: Wide layout configuration with sidebar navigation and tabbed interfaces for organized content presentation

### Backend Architecture
- **Socratic Chat Engine**: Core educational component that implements four-level questioning strategy (comprehension → analysis → synthesis → evaluation)
- **Article Processing System**: PDF text extraction and content analysis using PyPDF2 for processing uploaded research articles
- **RAG (Retrieval-Augmented Generation) System**: Knowledge base integration using sentence transformers for semantic search and context-aware responses
- **Authentication Manager**: Simple credential-based system with role differentiation (Student, Professor, Guest)

### Data Storage Solutions
- **SQLite Database**: Local database for storing chat sessions, messages, user interactions, and article metadata
- **File-Based Storage**: PDF articles stored in local filesystem with structured directory organization
- **Session State Management**: Streamlit's session state for maintaining user context and chat history during sessions
- **JSON Configuration**: Socratic prompts and system configuration stored in structured JSON files

### AI Integration
- **OpenAI GPT Integration**: Uses OpenAI API (specifically gpt-4o model) for generating Socratic responses and educational guidance
- **Sentence Transformers**: Local embedding model (all-MiniLM-L6-v2) for semantic similarity and knowledge base retrieval
- **Progressive Learning Logic**: Multi-level conversation system that adapts questioning complexity based on student progress

## External Dependencies

### AI Services
- **OpenAI API**: Primary language model for Socratic dialogue generation (requires OPENAI_API_KEY environment variable)
- **Hugging Face Transformers**: Sentence transformer models for local embedding generation and semantic search

### Python Libraries
- **Streamlit**: Web application framework for the entire user interface
- **PyPDF2**: PDF processing and text extraction from uploaded academic articles
- **SQLite3**: Database operations for interaction logging and data persistence
- **Pandas**: Data manipulation for analytics and export functionality
- **Plotly**: Interactive charts and visualizations for the professor dashboard
- **SentenceTransformers**: Semantic similarity and embedding generation for RAG system
- **NumPy**: Numerical operations for embedding calculations
- **Pickle**: Serialization for caching computed embeddings

### File Dependencies
- **Knowledge Base**: Text-based landscape ecology knowledge stored in `data/landscape_ecology_kb.txt`
- **Socratic Prompts**: Question templates organized by cognitive level in `data/socratic_prompts.json`
- **Local Database**: SQLite database for persistent storage of all interactions and metadata

### Deployment Requirements
- **Environment Variables**: Requires OPENAI_API_KEY for AI functionality
- **File System Access**: Needs write permissions for database, article storage, and embedding cache
- **Python 3.8+**: Compatible with modern Python versions supporting all listed dependencies
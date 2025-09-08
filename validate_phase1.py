#!/usr/bin/env python3
"""
Phase 1 Validation Script - Checks that all critical fixes have been applied correctly
Run this script to verify that Phase 1 implementation is complete
"""

import os
import sys
import re

def check_database_fix():
    """Check that database health check fix has been applied"""
    print("Checking database health check fix...")
    
    try:
        with open('components/database_init.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the line with required_tables has been fixed
        if 'required_tables = ["articles", "chat_sessions", "chat_messages", "student_progress"]' in content:
            print("  [+] Database health check fixed - 'users' table removed")
            return True
        else:
            print("  [!] Database health check fix not found")
            return False
    except Exception as e:
        print(f"  [!] Error checking database fix: {e}")
        return False

def check_app_cleanup():
    """Check that redundant database calls have been removed from app.py"""
    print("Checking app.py cleanup...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that redundant import and call are removed
        redundant_import = "from components.database import initialize_database"
        redundant_call = "initialize_database()"
        
        has_redundant_import = redundant_import in content
        has_redundant_call = redundant_call in content
        
        if not has_redundant_import and not has_redundant_call:
            print("  [+] App cleanup complete - redundant calls removed")
            return True
        else:
            print(f"  [!] App cleanup incomplete - redundant import: {has_redundant_import}, redundant call: {has_redundant_call}")
            return False
    except Exception as e:
        print(f"  [!] Error checking app cleanup: {e}")
        return False

def check_anthropic_fix():
    """Check that Anthropic client initialization has been fixed"""
    print("Checking Anthropic client fix...")
    
    try:
        with open('components/chat_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the fixed initialization code
        if "anthropic_key = os.environ.get('ANTHROPIC_API_KEY')" in content:
            print("  [+] Anthropic client fix applied - graceful fallback implemented")
            return True
        else:
            print("  [!] Anthropic client fix not found")
            return False
    except Exception as e:
        print(f"  [!] Error checking Anthropic fix: {e}")
        return False

def check_requirements_update():
    """Check that requirements.txt has been updated with necessary dependencies"""
    print("Checking requirements.txt updates...")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_packages = ['groq', 'anthropic', 'scikit-learn', 'matplotlib', 'seaborn']
        missing_packages = []
        
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if not missing_packages:
            print("  [+] Requirements.txt updated with all necessary dependencies")
            return True
        else:
            print(f"  [!] Missing packages in requirements.txt: {missing_packages}")
            return False
    except Exception as e:
        print(f"  [!] Error checking requirements: {e}")
        return False

def check_database_indexes():
    """Check that database performance indexes have been added"""
    print("Checking database indexes...")
    
    try:
        with open('components/database_init.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for index creation statements
        expected_indexes = [
            "idx_session_user",
            "idx_messages_session", 
            "idx_articles_active",
            "idx_progress_student"
        ]
        
        missing_indexes = []
        for index in expected_indexes:
            if index not in content:
                missing_indexes.append(index)
        
        if not missing_indexes:
            print("  [+] Database performance indexes added")
            return True
        else:
            print(f"  [!] Missing database indexes: {missing_indexes}")
            return False
    except Exception as e:
        print(f"  [!] Error checking database indexes: {e}")
        return False

def check_pdf_enhancement():
    """Check that PDF processing has been enhanced"""
    print("Checking PDF processing enhancements...")
    
    try:
        with open('pages/1_Student_Chat.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for enhanced error handling features
        enhancements = [
            "load_article_safely",
            "progress_bar",
            "file_size",
            "successful_pages"
        ]
        
        missing_enhancements = []
        for enhancement in enhancements:
            if enhancement not in content:
                missing_enhancements.append(enhancement)
        
        if not missing_enhancements:
            print("  [+] PDF processing enhancements implemented")
            return True
        else:
            print(f"  [!] Missing PDF enhancements: {missing_enhancements}")
            return False
    except Exception as e:
        print(f"  [!] Error checking PDF enhancements: {e}")
        return False

def check_directory_structure():
    """Check that required directories exist"""
    print("Checking directory structure...")
    
    required_dirs = [
        "data",
        "article_research", 
        "uploads",
        "exports",
        "logs",
        "data/cache",
        ".streamlit"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if not missing_dirs:
        print("  [+] All required directories exist")
        return True
    else:
        print(f"  [!] Missing directories: {missing_dirs}")
        return False

def check_knowledge_base():
    """Check that knowledge base exists and has content"""
    print("Checking knowledge base...")
    
    kb_path = "data/landscape_ecology_kb.txt"
    
    try:
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 1000:  # Should have substantial content
                print(f"  [+] Knowledge base exists with {len(content)} characters")
                return True
            else:
                print(f"  [!] Knowledge base exists but is too small ({len(content)} characters)")
                return False
        else:
            print(f"  [!] Knowledge base not found at {kb_path}")
            return False
    except Exception as e:
        print(f"  [!] Error checking knowledge base: {e}")
        return False

def main():
    """Main validation function"""
    
    print("Phase 1 Implementation Validation")
    print("=" * 40)
    
    checks = [
        check_database_fix,
        check_app_cleanup,
        check_anthropic_fix,
        check_requirements_update,
        check_database_indexes,
        check_pdf_enhancement,
        check_directory_structure,
        check_knowledge_base
    ]
    
    passed = 0
    total = len(checks)
    
    for check_func in checks:
        try:
            if check_func():
                passed += 1
            print()  # Add spacing between checks
        except Exception as e:
            print(f"  [!] Check failed with exception: {e}")
            print()
    
    print("=" * 40)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("SUCCESS: Phase 1 implementation is complete!")
        print("\nReady for deployment with Groq API key.")
        print("The application should now run without critical errors.")
        return 0
    else:
        print(f"WARNING: {total - passed} issues need to be addressed.")
        print("Please review the failed checks above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
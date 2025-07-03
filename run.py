#!/usr/bin/env python3
"""
JobSniper AI - Main Entry Point
Run this file to start the application
"""

import os
import sys
import logging
import streamlit as st
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    try:
        from utils.config import validate_config
        
        config_status = validate_config()
        
        if not config_status["valid"]:
            st.error("⚠️ Configuration Issues Found:")
            for issue in config_status["issues"]:
                st.error(f"• {issue}")
            
            st.info("📝 Please check your .env file and ensure all required variables are set.")
            st.info("📋 See .env.example for reference.")
            return False
        
        st.success(f"✅ Configuration valid! Using {config_status['ai_provider']} as AI provider")
        st.info(f"🚀 {config_status['features_enabled']} features enabled")
        return True
    except ImportError as e:
        st.error(f"❌ Configuration module error: {e}")
        return False

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="JobSniper AI - Fixed Version",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("🎯 JobSniper AI - Fixed Version")
    st.markdown("### Professional Resume & Career Intelligence Platform")
    
    try:
        # Check environment first
        if not check_environment():
            st.stop()
        
        st.success("🎉 All systems operational! The application is ready to use.")
        st.info("📁 Navigate to the original ui/app.py to run the full application interface.")
        
        # Show configuration status
        from utils.config import load_config
        config = load_config()
        
        with st.expander("📊 Configuration Status"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**AI Providers:**")
                st.write(f"• Gemini: {'✅' if config.get('gemini_available') else '❌'}")
                st.write(f"• Mistral: {'✅' if config.get('mistral_available') else '❌'}")
                st.write(f"• Active: {config.get('ai_provider', 'None').title()}")
            
            with col2:
                st.write("**Features:**")
                features = config.get('features', {})
                for feature, enabled in features.items():
                    st.write(f"• {feature.replace('_', ' ').title()}: {'✅' if enabled else '❌'}")
        
        st.markdown("---")
        st.markdown("### 🚀 Quick Start")
        st.code("""
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your API keys
# 4. Run the application
streamlit run ui/app.py
        """)
        
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.error("Please ensure all dependencies are installed: `pip install -r requirements.txt`")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"❌ Application Error: {e}")
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()
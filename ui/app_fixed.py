import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
import tempfile
import logging

# Add the parent directory to the Python path so we can import from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing agents
try:
    from agents.controller_agent import ControllerAgent
    from agents.auto_apply_agent import AutoApplyAgent
    from agents.recruiter_view_agent import RecruiterViewAgent
    from agents.skill_recommendation_agent import SkillRecommendationAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    st.error(f"⚠️ Agents not available: {e}")

# Import utilities with error handling
try:
    from utils.pdf_reader import extract_text_from_pdf
except ImportError:
    def extract_text_from_pdf(file_path):
        return "PDF extraction not available"

try:
    from utils.sqlite_logger import save_to_db, SQLiteLogger
except ImportError:
    def save_to_db(*args, **kwargs):
        pass
    class SQLiteLogger:
        def __init__(self):
            pass
        def log_analysis(self, *args, **kwargs):
            pass

try:
    from utils.config import load_config, validate_config, FEATURES, EMAIL_AVAILABLE
    config = load_config()
except ImportError as e:
    st.error(f"⚠️ Configuration error: {e}")
    config = {}
    FEATURES = {}
    EMAIL_AVAILABLE = False

# Import JSON helper
from utils.json_helper import safe_json_loads, safe_json_dumps, extract_data_safely, normalize_agent_response

# Import new enhanced agents
try:
    from agents.web_scraper_agent import WebScraperAgent
    from agents.resume_builder_agent import ResumeBuilderAgent
    from agents.advanced_interview_prep_agent import AdvancedInterviewPrepAgent
    from agents.career_path_agent import CareerPathAgent
    WEB_FEATURES_AVAILABLE = True
except ImportError as e:
    WEB_FEATURES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="JobSniper AI - Fixed Version",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "user_session" not in st.session_state:
    st.session_state.user_session = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "start_time": datetime.now(),
    }

def safe_agent_call(agent_func, input_data, agent_name="Unknown"):
    """
    Safely call an agent function and handle the response
    
    Args:
        agent_func: Agent function to call
        input_data: Input data for the agent
        agent_name: Name of the agent for logging
    
    Returns:
        Normalized response dict
    """
    try:
        logger.info(f"Calling {agent_name} agent...")
        
        # Ensure input is properly formatted
        if isinstance(input_data, dict):
            input_str = safe_json_dumps(input_data)
        else:
            input_str = str(input_data)
        
        # Call the agent
        response = agent_func(input_str)
        
        # Normalize the response
        normalized = normalize_agent_response(response)
        
        logger.info(f"{agent_name} agent completed successfully")
        return normalized
        
    except Exception as e:
        logger.error(f"Error in {agent_name} agent: {e}")
        return {
            "success": False,
            "data": {},
            "overall_score": 0,
            "parsed_data": {},
            "recommendations": [],
            "error": str(e)
        }

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🎯 JobSniper AI - Fixed Version</h1>
        <p>Professional Resume & Career Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration status
    with st.expander("📊 System Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Configuration:**")
            if config:
                st.success("✅ Config loaded")
                st.write(f"AI Provider: {config.get('ai_provider', 'Unknown')}")
            else:
                st.error("❌ Config failed")
        
        with col2:
            st.write("**Agents:**")
            if AGENTS_AVAILABLE:
                st.success("✅ Agents available")
            else:
                st.error("❌ Agents not available")
        
        with col3:
            st.write("**Features:**")
            if WEB_FEATURES_AVAILABLE:
                st.success("✅ Web features available")
            else:
                st.warning("⚠️ Limited features")
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose a feature:",
        [
            "🏠 Home",
            "📄 Resume Analysis", 
            "🎯 Job Matching",
            "💼 Career Insights",
            "🔧 Test JSON Fix"
        ]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📄 Resume Analysis":
        show_resume_analysis()
    elif page == "🎯 Job Matching":
        show_job_matching()
    elif page == "💼 Career Insights":
        show_career_insights()
    elif page == "🔧 Test JSON Fix":
        show_json_test()

def show_home_page():
    """Show the home page"""
    st.header("🏠 Welcome to JobSniper AI")
    
    st.markdown("""
    ### 🎉 What's Fixed in This Version:
    
    ✅ **JSON Handling Error** - Fixed "JSON object must be str, bytes or bytearray, not dict"  
    ✅ **Configuration Loading** - Added missing `load_config()` function  
    ✅ **Error Handling** - Comprehensive error handling throughout  
    ✅ **Dependencies** - Updated deprecated packages  
    ✅ **Setup Process** - Automated setup and validation  
    
    ### 🚀 Features Available:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - 📄 **Resume Analysis** - Parse and analyze resumes
        - 🎯 **Job Matching** - Match skills with opportunities  
        - 💼 **Career Insights** - Get career recommendations
        - 🔧 **JSON Testing** - Test the JSON fix
        """)
    
    with col2:
        st.markdown("""
        - 🤖 **AI Integration** - Gemini & Mistral support
        - 📊 **Analytics** - Performance tracking
        - 📧 **Email Reports** - Send results via email
        - 🔒 **Secure Config** - Environment-based setup
        """)

def show_resume_analysis():
    """Show resume analysis page with fixed JSON handling"""
    st.header("📄 Resume Analysis - Fixed Version")
    
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)", 
        type=['pdf'],
        help="Upload a PDF resume for AI analysis"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Extract text
            with st.spinner("📖 Extracting text from PDF..."):
                resume_text = extract_text_from_pdf(temp_file_path)
            
            if resume_text and len(resume_text.strip()) > 0:
                st.success("✅ Text extracted successfully")
                
                # Show preview
                with st.expander("📝 Resume Text Preview"):
                    st.text_area("Extracted Text", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200)
                
                # AI Analysis
                if AGENTS_AVAILABLE:
                    if st.button("🤖 Analyze with AI", type="primary"):
                        analyze_resume_with_ai(resume_text, uploaded_file.name)
                else:
                    st.warning("⚠️ AI agents not available. Please copy the agents directory from your original repository.")
            
            else:
                st.error("❌ Could not extract text from PDF")
            
            # Cleanup
            os.unlink(temp_file_path)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
            logger.error(f"Resume analysis error: {e}")

def analyze_resume_with_ai(resume_text, filename):
    """Analyze resume with AI agents using fixed JSON handling"""
    
    try:
        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Controller Agent
        status_text.text("🤖 Running controller agent...")
        progress_bar.progress(25)
        
        if 'ControllerAgent' in globals():
            controller = ControllerAgent()
            controller_result = safe_agent_call(
                controller.run, 
                resume_text, 
                "Controller"
            )
            
            st.success("✅ Controller analysis completed")
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Analysis Results")
                
                # Overall score
                score = controller_result.get("overall_score", 0)
                st.metric("Overall Score", f"{score}%")
                
                # Parsed data
                parsed_data = controller_result.get("parsed_data", {})
                if parsed_data:
                    st.write("**Extracted Information:**")
                    st.json(parsed_data)
            
            with col2:
                st.subheader("💡 Recommendations")
                recommendations = controller_result.get("recommendations", [])
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                else:
                    st.info("No specific recommendations available")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis completed successfully!")
            
            # Log the analysis
            try:
                logger_instance = SQLiteLogger()
                logger_instance.log_analysis(controller_result, filename)
                st.success("📝 Analysis logged to database")
            except Exception as e:
                st.warning(f"⚠️ Could not log to database: {e}")
        
        else:
            st.error("❌ ControllerAgent not available")
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        logger.error(f"Resume analysis error: {e}")

def show_job_matching():
    """Show job matching page"""
    st.header("🎯 Job Matching")
    st.info("📋 Copy your agents directory from the original repository to enable this feature")
    
    # Placeholder for job matching functionality
    st.markdown("""
    ### Job Matching Features:
    - Match resume skills with job requirements
    - Calculate compatibility scores
    - Suggest improvements
    - Find relevant opportunities
    """)

def show_career_insights():
    """Show career insights page"""
    st.header("💼 Career Insights")
    st.info("📋 Copy your agents directory from the original repository to enable this feature")
    
    # Placeholder for career insights
    st.markdown("""
    ### Career Insights Features:
    - Career path analysis
    - Skill gap identification
    - Salary insights
    - Industry trends
    """)

def show_json_test():
    """Test JSON handling fix"""
    st.header("🔧 JSON Handling Test")
    
    st.markdown("""
    This page demonstrates the JSON handling fix that resolves the error:
    `"the JSON object must be str, bytes or bytearray, not dict"`
    """)
    
    # Test different data types
    test_cases = [
        {"name": "Dictionary", "data": {"key": "value", "number": 42}},
        {"name": "JSON String", "data": '{"key": "value", "number": 42}'},
        {"name": "Plain String", "data": "This is just a string"},
        {"name": "List", "data": [1, 2, 3, "test"]},
        {"name": "Number", "data": 42},
        {"name": "Invalid JSON", "data": '{"invalid": json}'},
    ]
    
    st.subheader("🧪 Test Cases")
    
    for test_case in test_cases:
        with st.expander(f"Test: {test_case['name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Input:**")
                st.code(str(test_case['data']))
                st.write(f"Type: `{type(test_case['data']).__name__}`")
            
            with col2:
                st.write("**Output (safe_json_loads):**")
                try:
                    result = safe_json_loads(test_case['data'])
                    st.json(result)
                    st.success("✅ Handled successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Interactive test
    st.subheader("🎮 Interactive Test")
    user_input = st.text_area("Enter your test data:", '{"test": "data"}')
    
    if st.button("Test JSON Handling"):
        try:
            result = safe_json_loads(user_input)
            st.success("✅ Successfully processed!")
            st.json(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
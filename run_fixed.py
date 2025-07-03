#!/usr/bin/env python3
"""
JobSniper AI - Fixed Version Runner
This script runs the fixed version of the application with proper error handling
"""

import os
import sys
import logging
import subprocess
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

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_configuration():
    """Check if configuration is valid"""
    try:
        from utils.config import validate_config
        
        config_status = validate_config()
        
        if not config_status["valid"]:
            print("⚠️ Configuration Issues Found:")
            for issue in config_status["issues"]:
                print(f"  • {issue}")
            
            print("\n📝 Please check your .env file and ensure all required variables are set.")
            print("📋 See .env.example for reference.")
            return False
        
        print(f"✅ Configuration valid! Using {config_status['ai_provider']} as AI provider")
        print(f"🚀 {config_status['features_enabled']} features enabled")
        return True
        
    except ImportError as e:
        print(f"❌ Configuration module error: {e}")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting JobSniper AI Fixed Version...")
        
        # Run the fixed app
        app_path = project_root / "ui" / "app_fixed.py"
        
        if not app_path.exists():
            print(f"❌ App file not found: {app_path}")
            return False
        
        # Start Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
        
        print(f"📱 Running: {' '.join(cmd)}")
        print("🌐 The app will open in your browser automatically")
        print("🛑 Press Ctrl+C to stop the application")
        
        subprocess.run(cmd)
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

def show_help():
    """Show help information"""
    print("""
🎯 JobSniper AI - Fixed Version

Usage:
  python run_fixed.py [options]

Options:
  --help, -h     Show this help message
  --check, -c    Check configuration and dependencies only
  --setup, -s    Run setup script first

Examples:
  python run_fixed.py           # Run the application
  python run_fixed.py --check   # Check configuration
  python run_fixed.py --setup   # Run setup first

Features Fixed:
  ✅ JSON handling error resolved
  ✅ Configuration loading fixed  
  ✅ Error handling improved
  ✅ Dependencies updated
  ✅ Setup automated

For more information, see README.md
    """)

def main():
    """Main function"""
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        show_help()
        return
    
    if "--setup" in args or "-s" in args:
        print("🔧 Running setup first...")
        try:
            subprocess.run([sys.executable, "setup.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Setup failed")
            return
    
    print("🎯 JobSniper AI - Fixed Version")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Run setup to install dependencies:")
        print("   python setup.py")
        return
    
    # Check configuration
    if not check_configuration():
        print("\n💡 Configuration help:")
        print("   1. Copy .env.example to .env")
        print("   2. Edit .env with your API keys")
        print("   3. Run this script again")
        
        if "--check" in args or "-c" in args:
            return
        
        # Ask if user wants to continue anyway
        try:
            response = input("\n❓ Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return
        except KeyboardInterrupt:
            print("\n🛑 Cancelled by user")
            return
    
    if "--check" in args or "-c" in args:
        print("\n✅ Check completed successfully!")
        return
    
    # Run the application
    print("\n" + "=" * 50)
    success = run_streamlit_app()
    
    if success:
        print("\n✅ Application completed successfully!")
    else:
        print("\n❌ Application failed to start")

if __name__ == "__main__":
    main()
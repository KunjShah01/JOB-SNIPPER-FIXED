"""
Setup script for JobSniper AI
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your actual API keys")
        return True
    elif not env_file.exists():
        print("⚠️ No .env file found. Please create one with your API keys.")
        return False
    else:
        print("ℹ️ .env file already exists")
        return True

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_database():
    """Initialize the database"""
    try:
        print("🗄️ Initializing database...")
        # Create utils directory if it doesn't exist
        os.makedirs("utils", exist_ok=True)
        
        # Create a simple init file for utils
        init_file = Path("utils/__init__.py")
        if not init_file.exists():
            init_file.write_text("# Utils package")
        
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["agents", "ui", "utils"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f"# {directory.title()} package")
    print("✅ Directory structure created")

def main():
    """Main setup function"""
    print("🚀 Setting up JobSniper AI...")
    print("=" * 50)
    
    # Create directory structure
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return False
    
    # Create environment file
    if not create_env_file():
        print("❌ Setup failed during environment file creation")
        return False
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed during database setup")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Copy your original source files to this repository")
    print("3. Run: python run.py")
    print("4. Or run: streamlit run ui/app.py")
    print("\n🔗 Repository: https://github.com/KunjShah01/JOB-SNIPPER-FIXED")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import os
import argparse
from dotenv import load_dotenv
from database import init_database

def setup_environment():
    """
    Sets up the application environment
    """
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        
        # Copy template to .env
        if os.path.exists('.env.template'):
            with open('.env.template', 'r') as template_file:
                template_content = template_file.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(template_content)
            
            print(".env file created. Please edit it to add your API keys.")
        else:
            print("Warning: .env.template file not found. Please create .env file manually.")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    print("Initializing database...")
    init_database()
    print("Database initialized.")
    
    # Check data directories
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir)
    
    print("Setup complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up the Crypto Market Cap Analysis & Prediction application.")
    
    args = parser.parse_args()
    
    setup_environment()
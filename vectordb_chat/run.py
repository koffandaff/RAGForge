#!/usr/bin/env python3
"""
Run script for VectorDB Chat App
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    print("Starting VectorDB Chat App...")
    print("Open your browser to http://localhost:8501")
    print("Upload page: http://localhost:8501/Upload")
    print("Chat page: http://localhost:8501/Chat")
    print("\nMake sure Ollama is running with:")
    print("  ollama run deepseek-coder:6.7b")
    print("\nPress Ctrl+C to stop the app\n")
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_path, "--server.port=8501", "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\nApp stopped by user.")

if __name__ == "__main__":
    main()

"""
SigmaBot - Main entry point
Launches Streamlit GUI
"""
import sys
import subprocess


def main():
    """Launch Streamlit GUI."""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/Home.py"])


if __name__ == "__main__":
    main()

"""
SigmaBot - Main entry point
Launches Streamlit GUI
"""
import sys
import subprocess
import queue

# Create a global event queue (can be used by Streamlit pages)
EVENT_QUEUE = queue.Queue()


def main():
    """Launch Streamlit GUI."""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/Home.py"])


if __name__ == "__main__":
    main()

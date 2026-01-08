# Import modules
import inquirer
from src import indicators, log_return
import sys
from src.event_manager import EventManager
from src.logger import Logger


def start_gui():
    """Start the Streamlit GUI application."""
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/Home.py"])


def display_menu():
    """Display a menu for the user to select commands."""
    choices = [
        "🖥️  Launch GUI (Streamlit)",
        " Run indicators module",
        "📉 Run log_return module",
        "❌ Exit",
    ]

    questions = [
        inquirer.List(
            "command",
            message="Select a command to execute",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    return answer["command"]


def execute_command(command):
    """Execute the selected command."""
    if command == "🖥️  Launch GUI (Streamlit)":
        print("Launching Streamlit GUI...")
        start_gui()
    elif command == " Run indicators module":
        indicators.main()
    elif command == "📉 Run log_return module":
        log_return.main()
    elif command == "❌ Exit":
        print("Exiting...")
        exit()


def main():
    event_manager = EventManager()
    logger = Logger()
    event_manager.subscribe(logger)

    while True:
        command = display_menu()
        execute_command(command)


if __name__ == "__main__":
    main()

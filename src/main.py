# Import modules
import inquirer
from src import backtest_rsi_ema, indicators, log_return
import sys
print(sys.executable)
from src.event_manager import EventManager
from src.logger import Logger


def display_menu():
    """Display a menu for the user to select commands."""
    choices = [
        "Run backtest_rsi_ema module",
        "Run indicators module",
        "Run log_return module",
        "Exit",
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
    if command == "Run backtest_rsi_ema module":
        backtest_rsi_ema.main()
    elif command == "Run indicators module":
        indicators.main()
    elif command == "Run log_return module":
        log_return.main()
    elif command == "Exit":
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

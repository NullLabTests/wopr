from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

import json
import os
import sys
from typing import Optional

import requests
from rich import print
from rich.prompt import Prompt
from rich.console import Console

# Constants
WOPR_KEY = os.getenv("WOPR_KEY")
API_URL = os.getenv("WOPR_API_URL")
SESSION_FILE = "wopr_session.json"

# Initialize Rich Console
console = Console()

def load_session() -> Optional[str]:
    """Load the session ID from a file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("session_id")
    return None

def save_session(session_id: str):
    """Save the session ID to a file."""
    with open(SESSION_FILE, "w") as f:
        json.dump({"session_id": session_id}, f)

def remove_session():
    """Remove the session file."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def make_game_request(message: str, session_id: Optional[str] = None) -> requests.Response:
    """Send a POST request to the WOPR API."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": WOPR_KEY,
    }
    body = {
        "message": message,
        "session_id": session_id,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=body)
        return response
    except requests.RequestException as e:
        console.print(f"[red]Error communicating with WOPR API: {e}[/red]")
        sys.exit(1)

def echo(line: str, state: dict) -> dict:
    """Echo command functionality."""
    return {
        "output": [line],
        "exit_status": 0,
        "new_state": state,
    }

class WOPR:
    def __init__(self):
        self.state = {"phase": "init"}

    def run(self):
        while True:
            if self.state["phase"] == "init":
                self.init_phase()
            elif self.state["phase"] == "login":
                self.login_phase()
            elif self.state["phase"] == "ready":
                self.ready_phase()
            else:
                console.print("[red]Unknown phase. Exiting.[/red]")
                break

    def init_phase(self):
        """Handle the init phase."""
        remove_session()
        console.print("\n".join([
            "WOPR", "Loading...", "", ""
        ]))
        self.state = {"phase": "login"}
        console.print("[bold green]Phase: INIT -> LOGIN[/bold green]")
        console.print("LOGON:", end=" ")

    def login_phase(self):
        """Handle the login phase."""
        username = Prompt.ask("LOGON").strip()
        if username.lower() == "joshua":
            console.print("\n".join([
                "LOGON SUCCESSFUL",
                "",
                "GREETINGS, PROFESSOR FALKEN.",
                "CAN YOU EXPLAIN THE REMOVAL OF YOUR USER ACCOUNT",
                "ON JUNE 23, 1973?",
            ]))
            self.state = {"phase": "ready"}
            console.print("\n[bold green]Phase: LOGIN -> READY[/bold green]")
        else:
            console.print("\n[indianred1]IDENTIFICATION NOT RECOGNIZED BY SYSTEM[/indianred1]")
            console.print("[indianred1]--CONNECTION TERMINATED--[/indianred1]")
            sys.exit(1)

    def ready_phase(self):
        """Handle the ready phase."""
        try:
            user_input = Prompt.ask("$ ").strip()
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold yellow]Exiting WOPR. Goodbye![/bold yellow]")
                sys.exit(0)
            elif user_input.lower().startswith("echo "):
                # Simple echo command
                line = user_input[5:]
                result = echo(line, self.state)
                for output_line in result["output"]:
                    console.print(output_line)
            else:
                # Make game request
                session_id = load_session()
                response = make_game_request(user_input, session_id)
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message", "")
                    session_id_new = data.get("session_id")
                    if session_id_new:
                        save_session(session_id_new)
                    for line in message.split("\n"):
                        console.print(line)
                else:
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", "An error occurred.")
                        console.print(f"[red]{detail}[/red]")
                    except json.JSONDecodeError:
                        console.print("[red]An unknown error occurred.[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Exiting WOPR. Goodbye![/bold yellow]")
            sys.exit(0)

if __name__ == "__main__":
    wopr = WOPR()
    wopr.run()

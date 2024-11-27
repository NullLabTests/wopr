Sure! Below is a Python script that replicates the functionality of your React `wopr` command-line interface. It uses the `rich` library for enhanced terminal output and manages the game state across different phases (`init`, `login`, and `ready`). The script handles user input, communicates with the WOPR API using the `make_game_request` function, and maintains the session ID using a local file for persistence.

### Requirements

Before running the script, ensure you have the necessary packages installed:

```bash
pip install rich requests
```

### Python Script

```python
import json
import os
import sys
from typing import Optional

import requests
from rich import print
from rich.prompt import Prompt
from rich.console import Console

# Constants
WOPR_KEY = "dc55c2dbd26f87d653e2dcc1b496dc65"
API_URL = "https://wopr.us.davidsingleton.org/game/message"
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
```

### Script Explanation

1. **Imports and Constants**:
    - **Libraries**: The script uses `requests` for HTTP requests and `rich` for enhanced terminal output. 
    - **Constants**: `WOPR_KEY` is your API key, `API_URL` is the endpoint, and `SESSION_FILE` is the filename used to store the session ID locally.

2. **Session Management**:
    - **`load_session`**: Loads the session ID from a JSON file if it exists.
    - **`save_session`**: Saves the session ID to a JSON file.
    - **`remove_session`**: Deletes the session file to reset the session.

3. **`make_game_request` Function**:
    - Sends a POST request to the WOPR API with the user's message and the current session ID.
    - Handles exceptions and exits the program if a request fails.

4. **`echo` Function**:
    - Mimics the `echo` binary from your React code by returning the input line.

5. **`WOPR` Class**:
    - Manages the game state (`init`, `login`, `ready`).
    - **`run` Method**: Main loop that handles transitions between phases.
    - **`init_phase` Method**: Resets the session and transitions to the login phase.
    - **`login_phase` Method**: Prompts the user for a username. If the username is "joshua" (case-insensitive), it proceeds to the ready phase; otherwise, it terminates.
    - **`ready_phase` Method**: 
        - Prompts the user for commands.
        - Handles `echo` commands internally.
        - Sends other commands to the WOPR API and displays the response.
        - Handles exiting the application gracefully on `exit`, `quit`, or keyboard interrupts.

6. **Running the Script**:
    - The script initializes the `WOPR` class and starts the main loop.

### Usage

1. **Start the Application**:
    ```bash
    python wopr_terminal.py
    ```

2. **Initialization**:
    - The application will display "WOPR Loading..." and transition to the login phase.

3. **Login Phase**:
    - You'll be prompted with `LOGON:`.
    - Enter `joshua` (case-insensitive) to log in successfully.
    - Entering any other username will terminate the connection.

4. **Ready Phase**:
    - After a successful login, you'll see a greeting and be presented with a `$ ` prompt.
    - You can enter commands:
        - **Echo Command**: Type `echo your message` to have the message echoed back.
        - **WOPR Commands**: Any other input will be sent to the WOPR API, and the response will be displayed.
    - **Exit**: Type `exit` or `quit` to terminate the application.

### Example Session

```
WOPR
Loading...


Phase: INIT -> LOGIN
LOGON: joshua

LOGON SUCCESSFUL

GREETINGS, PROFESSOR FALKEN.
CAN YOU EXPLAIN THE REMOVAL OF YOUR USER ACCOUNT
ON JUNE 23, 1973?

Phase: LOGIN -> READY
$ echo Hello, WOPR!
Hello, WOPR!
$ whoami
[Response from WOPR API]
$ exit
Exiting WOPR. Goodbye!
```

### Notes

- **Session Persistence**: The session ID is stored in a `wopr_session.json` file in the same directory as the script. This allows the session to persist across multiple runs of the application.
- **Error Handling**: The script includes basic error handling for HTTP requests and user interruptions.
- **Extensibility**: You can extend the script by adding more commands or improving the state management as needed.

This script should provide a solid foundation for interacting with the WOPR game API directly from your terminal, closely mirroring the functionality of your React web application.
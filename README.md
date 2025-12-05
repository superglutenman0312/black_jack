# Black Jack ♠️♥️

A multiplayer Black Jack game featuring both **CLI (Command Line Interface)** and **GUI (Graphical User Interface)** versions. This project demonstrates the implementation of **Client-Server Architecture**, **Socket Programming**, and **Multi-threading** in Python.

## 🚀 Features

* **Client-Server Architecture**: Centralized server manages game logic and player states.
* **Multi-threading**: Supports multiple players connecting and playing simultaneously.
* **Dual Interfaces**:
    * **CLI**: Lightweight text-based interface.
    * **GUI**: User-friendly graphical interface built with `tkinter`.
* **Real-time Interaction**: Instant updates for card drawing and game status broadcasting.

## 📸 Screenshots

### CLI Interface
![CLI Demo](screenshots/CLI.png)

### GUI Interface
![GUI Demo](screenshots/GUI.png)

## 🛠️ Tech Stack

* **Language**: Python 3
* **Networking**: Python `socket` (TCP/IP)
* **Concurrency**: Python `threading`
* **GUI Framework**: `tkinter`

## 📂 Project Structure

* `server.py` / `client.py`: Source code for the CLI version.
* `server_gui.py` / `client_gui.py`: Source code for the GUI version.
* `cards/`: (Ensure your card images are in this folder if applicable for GUI)

## 📖 How to Run

### 1. Start the Server
First, initialize the server to accept connections.
```bash
# For CLI version
python server.py

# For GUI version
python server_gui.py
```

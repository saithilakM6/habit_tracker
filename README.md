# Habit Tracker

A simple and effective Python-based Habit Tracker application designed to help you build and maintain good habits. This project allows you to log, monitor, and visualize your daily habits, making it easier to stay consistent and achieve your goals.

## Features

- Add, edit, and delete habits
- Track daily progress for each habit
- Visualize habits with charts and statistics
- Simple command-line interface (CLI) or graphical user interface (GUI) *(describe as per your implementation)*
- Data stored locally (e.g., JSON, CSV, or SQLite database)
- Streaks and habit history

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/saithilakM6/habit_tracker.git
    cd habit_tracker
    ```

2. **Create a virtual environment (optional but recommended)**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

- **CLI usage:**
    ```bash
    python main.py
    ```

- **GUI usage:**  
    *(If GUI is available, describe how to launch it. e.g.,)*
    ```bash
    python gui.py
    ```

- Follow on-screen instructions to add and track your habits!

## Example

```bash
$ python main.py
Welcome to Habit Tracker!
1. Add Habit
2. Mark Habit as Done
3. View Progress
4. Exit
Select option:
```

## Configuration

- All user data is stored in the `data/` directory as JSON/CSV/SQLite files.
- You can modify settings in the `config.py` file (if available).

## Dependencies

- Python 3.7+
- See [requirements.txt](requirements.txt) for a full list

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Inspired by [Atomic Habits](https://jamesclear.com/atomic-habits) by James Clear
- Thanks to all contributors and users!

# Space Invaders - Break Aware

A Space Invaders game with built-in break reminders to promote healthy gaming habits.

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

There are several ways to run the game:

### Option 1: Using the run script (Recommended)
```bash
python run_game.py
```

### Option 2: Using the batch file (Windows)
Double-click `run_game.bat` or run it from the command line:
```bash
run_game.bat
```

### Option 3: Running as a module
```bash
python -m src.main
```

## Game Features

- Classic Space Invaders gameplay
- Break reminders to promote healthy gaming habits
- Two game modes:
  - Normal Mode: Classic gameplay with break reminders
  - Break-Aware Mode: Enforces breaks when ignored
- Weekly statistics and leaderboard
- Dynamic break timing based on play patterns

## Controls

- Left/Right Arrow Keys: Move spaceship
- Space: Shoot
- ESC: Exit game
- L: Show leaderboard
- P: Take a voluntary break

## Project Structure

```
breakinvaders/
├── src/
│   ├── game/          # Game mechanics and entities
│   ├── ui/            # User interface components
│   ├── states/        # Game state management
│   └── utils/         # Utility functions
├── img/               # Game assets
├── run_game.py        # Main run script
├── run_game.bat       # Windows batch file
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install development dependencies:
```bash
pip install -e .
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

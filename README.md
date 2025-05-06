# Break Invaders

A Space Invaders game with built-in break reminders to promote healthy gaming habits.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/NurulhudaAlfares/breakinvaders.git
cd breakinvaders
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Game

### Windows
Simply double-click the `run_game.bat` file.

### Manual Run
```bash
python src/main.py
```

## Game Controls

- **Left Arrow**: Move spaceship left
- **Right Arrow**: Move spaceship right
- **Space**: Shoot
- **ESC**: Quit game
- **L**: Show leaderboard

## Game Features

- Classic Space Invaders gameplay
- Break reminders to promote healthy gaming habits
- Dynamic difficulty adjustment
- Score tracking and leaderboard
- Multiple game modes:
  - Normal Mode
  - Break-Aware Mode (with progressive cooldown)

## Game Modes

1. **Normal Mode**: Classic gameplay without break reminders
2. **Break-Aware Mode**: Includes break reminders and progressive cooldown if breaks are ignored

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

This project is licensed under the MIT License - see the LICENSE file for details.

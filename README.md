# Break Invaders

A Space Invaders game with break awareness features to promote healthy gaming habits.

## Features
- Classic Space Invaders gameplay
- Break reminder system
- Progressive cooldown effects
- Break-aware and normal modes
- Weekly statistics tracking

## Setup Instructions

### Local Development
1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

### Web Deployment
To deploy this game on the web, you'll need to:
1. Use Pygbag (Pygame Web Assembly) to convert the game to web format
2. Host the generated files on a web server

#### Using Pygbag
1. Install Pygbag:
   ```bash
   pip install pygbag
   ```
2. Build the web version:
   ```bash
   pygbag main.py
   ```
3. The build files will be in the `build/web` directory

#### Hosting
1. Upload the contents of the `build/web` directory to your web server
2. Ensure the server is configured to serve .wasm files with the correct MIME type
3. Access the game through your web server's URL

## Controls
- Left/Right Arrow Keys: Move spaceship
- Space: Shoot
- P: Take a voluntary break
- L: Show leaderboard
- ESC: Exit game

## Game Modes
- Normal Mode: Standard gameplay with break reminders
- Break-Aware Mode: Enforces breaks when ignored

## License
This project is licensed under the MIT License.

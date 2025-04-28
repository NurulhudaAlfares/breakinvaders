import json
import os
from typing import List
from datetime import datetime

# Session durations
SESSION_FILE = "session_data.json"


def load_session_durations() -> List[float]:
    """Load previous session durations from JSON."""
    try:
        if not os.path.exists(SESSION_FILE):
            return []
        with open(SESSION_FILE, "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        return []


def save_session_duration(duration: float):
    """Save a session duration (in seconds)."""
    try:
        sessions = load_session_durations()
        sessions.append(duration)
        sessions = sessions[-10:]  # Keep only the last 10
        with open(SESSION_FILE, "w") as file:
            json.dump(sessions, file)
    except Exception as e:
        pass


def calculate_break_trigger_time(session_durations):
    """Calculate the break trigger time based on session durations"""
    if not session_durations:
        return 160  # Default 2 minutes and 40 seconds
    
    # Calculate average session duration
    avg_duration = sum(session_durations) / len(session_durations)
    
    # Calculate break threshold (1.5x average)
    break_threshold = avg_duration * 1.5
    
    return break_threshold


# Gameplay stats
GAME_STATS_FILE = "game_data.json"


def save_game_stats(mode: str, duration: float, took_break: bool, level: int, breaks_ignored: int):
    """
    Save gameplay session statistics to a JSON file.

    Parameters:
    - mode: 'normal' or 'break-aware'
    - duration: session duration in seconds
    - took_break: whether a break was taken
    - level: final level reached
    - breaks_ignored: number of break prompts ignored
    """
    data = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "duration": duration,
        "took_break": took_break,
        "level": level,
        "breaks_ignored": breaks_ignored
    }

    if os.path.exists(GAME_STATS_FILE):
        with open(GAME_STATS_FILE, "r") as f:
            all_stats = json.load(f)
    else:
        all_stats = []

    all_stats.append(data)

    with open(GAME_STATS_FILE, "w") as f:
        json.dump(all_stats, f, indent=2)

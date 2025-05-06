import os
import sys
from pathlib import Path

def setup_environment():
    # Get the absolute path of the project root directory
    project_root = Path(__file__).resolve().parent
    
    # Add both the project root and src directory to the Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    src_path = str(project_root / 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Change to the project root directory
    os.chdir(project_root)

if __name__ == '__main__':
    setup_environment()
    from src.main import main
    main() 
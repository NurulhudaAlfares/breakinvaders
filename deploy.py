import os
import shutil
import subprocess

def build_web_version():
    print("Building web version...")
    try:
        # Install pygbag if not already installed
        subprocess.run(["pip", "install", "pygbag"], check=True)
        
        # Build the web version using the correct command for GitHub
        subprocess.run(["python", "-m", "pygbag", "--build", "."], check=True)
        
        print("Build successful! Files are in build/web directory")
        
        # Create a zip file of the build
        shutil.make_archive("breakinvaders_web", 'zip', "build/web")
        print("Created breakinvaders_web.zip for easy distribution")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    build_web_version() 
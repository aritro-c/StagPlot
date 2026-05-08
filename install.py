import os
import subprocess
import sys
import platform

def run_command(command):
    """Run a command and handle errors."""
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed: {' '.join(command)}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n[ERROR] Command not found: {command[0]}")
        sys.exit(1)

def main():
    print("========================================")
    print("     StagPlot Installation Script       ")
    print("========================================")
    
    # 1. Create virtual environment
    venv_name = "myenv"
    print(f"\n[*] Creating virtual environment: {venv_name}...")
    run_command([sys.executable, "-m", "venv", venv_name])
    
    # 2. Determine paths for pip and python based on OS
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_name, "Scripts", "pip.exe")
        python_path = os.path.join(venv_name, "Scripts", "python.exe")
        activate_cmd = f".\\{venv_name}\\Scripts\\activate"
    else:
        pip_path = os.path.join(venv_name, "bin", "pip")
        python_path = os.path.join(venv_name, "bin", "python")
        activate_cmd = f"source {venv_name}/bin/activate"
        
    # 3. Install/Upgrade pip
    print("[*] Upgrading pip...")
    run_command([pip_path, "install", "--upgrade", "pip"])
    
    # 4. Install dependencies
    dependencies = ["stagpy", "cmcrameri", "numpy", "matplotlib"]
    print(f"[*] Installing dependencies: {', '.join(dependencies)}...")
    run_command([pip_path, "install"] + dependencies)
    
    # 5. Check for FFmpeg
    print("\n[*] Checking for FFmpeg...")
    try:
        subprocess.check_call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] FFmpeg is already installed and available in PATH.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] FFmpeg NOT found. It is required for 'field_batch.py' animations.")
        print("    Please install it using the following command:")
        if platform.system() == "Linux":
            print("    sudo apt update && sudo apt install ffmpeg")
        elif platform.system() == "Darwin": # macOS
            print("    brew install ffmpeg")
        elif platform.system() == "Windows":
            print("    winget install ffmpeg")

    # 6. Final Instructions
    print("\n" + "="*40)
    print("      INSTALLATION SUCCESSFUL!          ")
    print("="*40)
    print(f"\nTo start using StagPlot, activate your environment:")
    print(f"\n    {activate_cmd}")
    print("\nThen you can run scripts, for example:")
    print(f"    python info.py")
    print("="*40)

if __name__ == "__main__":
    main()

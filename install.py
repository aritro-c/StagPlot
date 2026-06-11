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
    # 0. Check Python version (f-strings require 3.6+)
    if sys.version_info < (3, 6):
        print("[ERROR] StagPlot requires Python 3.6 or newer.")
        print(f"Current version: {sys.version}")
        sys.exit(1)

    print("========================================")
    print("     StagPlot Installation Script       ")
    print("========================================")

    # Prompt user for StagPy version
    print("\nWhich version of StagPy would you like to install?")
    print("1: Release version (stable, via PyPI)")
    print("2: Development version (latest, via GitHub)")
    
    choice = ""
    while choice not in ['1', '2']:
        choice = input("Enter 1 or 2 [default: 1]: ").strip()
        if not choice:
            choice = '1'

    stagpy_version_label = "Release (stable)" if choice == '1' else "Development (GitHub)"
    is_dev = (choice == '2')
    
    # 1. Create virtual environment
    venv_name = "StagPlot"
    print(f"\n[*] Creating virtual environment: {venv_name}...")
    run_command([sys.executable, "-m", "venv", venv_name])
    
    # 2. Determine paths and OS label
    os_name = platform.system()
    if os_name == "Windows":
        pip_path = os.path.join(venv_name, "Scripts", "pip.exe")
        python_path = os.path.join(venv_name, "Scripts", "python.exe")
        activate_cmd = f".\\{venv_name}\\Scripts\\activate"
        system_label = "Windows"
    else:
        pip_path = os.path.join(venv_name, "bin", "pip")
        python_path = os.path.join(venv_name, "bin", "python")
        activate_cmd = f"source {venv_name}/bin/activate"
        system_label = "Linux/macOS"
        
    # 3. Install/Upgrade pip
    print("[*] Upgrading pip...")
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 4. Install dependencies
    stagpy_dep = "git+https://github.com/StagPython/StagPy.git" if is_dev else "stagpy"
    dependencies = [stagpy_dep, "cmcrameri", "numpy", "matplotlib"]
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
        if os_name == "Linux":
            print("    sudo apt update && sudo apt install ffmpeg")
        elif os_name == "Darwin": # macOS
            print("    brew install ffmpeg")
        elif os_name == "Windows":
            print("    winget install ffmpeg")

    # 6. Final Instructions
    print("\n" + "="*40)
    print("      INSTALLATION SUCCESSFUL!          ")
    print("="*40)
    print(f"\nDetected OS: {system_label}")
    print(f"StagPy Version Installed: {stagpy_version_label}")
    print(f"  ")
    print(f"Open VScode in the current directory and ensure your Python Interpreter is set to '{venv_name}' (VSCode should automatically detect that). Now you can start using StagPlot. Enjoy ;)")
    print(f"  ")
    print(f"You can also use StagPlot directly from command line. Just activate your environment first:")
    print(f"\n    {activate_cmd}")
 
    print("="*40)

if __name__ == "__main__":
    main()

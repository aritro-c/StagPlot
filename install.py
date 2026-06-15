import os
import subprocess
import sys
import platform

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message):
    print(f"{Colors.OKBLUE}[*]{Colors.ENDC} {message}")

def print_success(message):
    print(f"{Colors.OKGREEN}[✓]{Colors.ENDC} {message}")

def print_warning(message):
    print(f"{Colors.WARNING}[!]{Colors.ENDC} {message}")

def print_error(message):
    print(f"{Colors.FAIL}[✗] ERROR:{Colors.ENDC} {message}")

def run_command(command, description=None):
    """Run a command and handle errors with better feedback."""
    if description:
        print_status(f"{description}...")
    
    try:
        # We don't capture output here so the user can see progress (e.g. pip installing)
        subprocess.check_call(command)
        if description:
            print_success(f"{description} successfully.")
    except subprocess.CalledProcessError:
        print("\n" + "="*50)
        print_error(f"Command failed: {' '.join(command)}")
        print("Please check the output above for details.")
        print("="*50 + "\n")
        sys.exit(1)
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")
        sys.exit(1)

def main():
    # 0. Check Python version
    if sys.version_info < (3, 6):
        print_error("StagPlot requires Python 3.6 or newer.")
        print(f"Current version: {sys.version}")
        sys.exit(1)

    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("==================================================")
    print("         StagPlot Installation Script             ")
    print("==================================================")
    print(f"{Colors.ENDC}")

    # Prompt user for StagPy version
    print(f"{Colors.BOLD}Configure Installation:{Colors.ENDC}")
    print("Which version of StagPy would you like to install?")
    print("  1: Release version (stable, via PyPI)")
    print("  2: Development version (latest, via GitHub)")
    
    choice = ""
    while choice not in ['1', '2']:
        choice = input(f"\n{Colors.OKCYAN}Enter 1 or 2 [default: 1]: {Colors.ENDC}").strip()
        if not choice:
            choice = '1'

    stagpy_version_label = "Release (stable)" if choice == '1' else "Development (GitHub)"
    is_dev = (choice == '2')
    
    # 1. Create virtual environment
    venv_name = "StagPlot"
    run_command([sys.executable, "-m", "venv", venv_name], f"Creating virtual environment: {venv_name}")
    
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
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")
    
    # 4. Install dependencies
    stagpy_dep = "git+https://github.com/StagPython/StagPy.git" if is_dev else "stagpy"
    dependencies = [stagpy_dep, "cmcrameri", "numpy", "matplotlib"]
    run_command([pip_path, "install"] + dependencies, f"Installing dependencies: {', '.join(dependencies)}")
    
    # 5. Check for FFmpeg
    print_status("Checking for FFmpeg...")
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print_success("FFmpeg is already installed and available in PATH.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("FFmpeg NOT found. It is required for 'field_batch.py' animations.")
        print(f"    {Colors.BOLD}Recommendation:{Colors.ENDC} Please install it using:")
        if os_name == "Linux":
            print(f"    {Colors.OKCYAN}sudo apt update && sudo apt install ffmpeg{Colors.ENDC}")
        elif os_name == "Darwin": # macOS
            print(f"    {Colors.OKCYAN}brew install ffmpeg{Colors.ENDC}")
        elif os_name == "Windows":
            print(f"    {Colors.OKCYAN}winget install ffmpeg{Colors.ENDC}")

    # 6. Final Instructions
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}" + "="*50)
    print("          INSTALLATION SUCCESSFUL!            ")
    print("="*50 + f"{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  - Detected OS: {Colors.OKCYAN}{system_label}{Colors.ENDC}")
    print(f"  - StagPy Version: {Colors.OKCYAN}{stagpy_version_label}{Colors.ENDC}")
    print(f"  - Environment: {Colors.OKCYAN}{venv_name}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. Open VS Code in this directory.")
    print(f"  2. Ensure your Python Interpreter is set to {Colors.OKGREEN}'{venv_name}'{Colors.ENDC}.")
    print(f"     (VS Code usually detects this automatically).")
    
    print(f"\n  To use StagPlot from the command line, activate the environment:")
    print(f"  {Colors.BOLD}{Colors.OKGREEN}{activate_cmd}{Colors.ENDC}")
 
    print(f"\n{Colors.HEADER}{Colors.BOLD}Enjoy using StagPlot! ;){Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}" + "="*50 + f"{Colors.ENDC}")

if __name__ == "__main__":
    # Support for Windows ANSI color support
    if platform.system() == "Windows":
        os.system('color')
    
    main()

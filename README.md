# StagPlot

StagPlot is a suite of Python scripts designed for post-processing and visualizing output from **StagYY**, a numerical mantle convection code. It uses the [StagPy](https://stagpython.github.io/StagPy/) library as a backend to interface with simulation data.

---

## 🚀 Quick Start (Automated Installation)

The easiest way to get started is to use the automated installation script. This will download the latest version, create a virtual environment, and install all necessary dependencies.

### Linux & macOS
```bash
curl -LO https://github.com/aritro-c/StagPlot/archive/refs/heads/main.zip
unzip main.zip
cd StagPlot-main
python3 install.py
rm ../main.zip
```

### Windows
```powershell
Invoke-WebRequest -Uri "https://github.com/aritro-c/StagPlot/archive/refs/heads/main.zip" -OutFile "main.zip"
Expand-Archive -Path "main.zip" -Force
cd StagPlot-main
python install.py
```

---

## 🛠️ Manual Installation

If you prefer to set up the environment manually, follow these steps:

### 1. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.

**Linux & macOS:**
```bash
python3 -m venv StagPlot
```

**Windows:**
```powershell
python -m venv StagPlot
```

### 2. Activate the Environment

**Linux & macOS:**
```bash
source StagPlot/bin/activate
```

**Windows:**
```powershell
.\StagPlot\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install stagpy cmcrameri numpy matplotlib rich
```

---

## 🎬 FFmpeg Installation (Required for Movies)

FFmpeg is required by `field_batch.py` to stitch individual frames into a movie file.

*   **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install ffmpeg`
*   **Linux (Fedora/RHEL):** `sudo dnf install ffmpeg`
*   **Linux (Arch Linux):**   You're on your own. Good luck ;)
*   **macOS:** `brew install ffmpeg`
*   **Windows:** `winget install ffmpeg` (Note: You may need to restart your terminal after installation)

---

## 💻 Visual Studio Code Setup

If you use VS Code for development:
1.  Open the `StagPlot-main` folder in VS Code.
2.  Set the Python Interpreter:
    *   Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS).
    *   Type **"Python: Select Interpreter"** and select it.
    *   Choose the environment you created (e.g., `StagPlot`).

**Linux Users:** It is **NOT recommended** to use the Flatpak or Snap version of VS Code. Their sandboxed nature often causes issues with finding system Python binaries or virtual environments. Use the system package manager instead (`apt` for Ubuntu/Debian and `dnf` for Fedora/RHEL; Arch users can do it on their own :) )

---

## 📜 Core Scripts

| Script | Description |
| :--- | :--- |
| `info.py` | Quickly inspect StagYY simulation metadata. |
| `field.py` | Plot a single 2D scalar field for a specific snapshot. |
| `field_batch.py` | Generate 2D field frames over a range of snapshots and stitch them into a movie. |
| `rprof.py` | Plot 1D radial profiles (depth vs. value) for a specific snapshot. |
| `rprof_time.py` | Create a spacetime plot (Hovmöller diagram) of a radial-profile parameter. |
| `surf2D_time.py` | Create a spacetime plot (Hovmöller diagram) of surface parameters. |
| `time.py` | Plot the evolution of global diagnostic parameters over time. |
| `tseries_export.py`| Extract multiple time-series fields and export them to a structured text file. |

---

## 📚 References

*   [StagPy Documentation](https://stagpython.github.io/StagPy/) - The backend library for data access.

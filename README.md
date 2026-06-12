# StagPlot 
### (CONSTRUCTION SITE AHEAD!)

A suite of Python scripts for post-processing and visualizing output from **StagYY**, a numerical mantle convection code. Most of the scripts use the **StagPy** library as a backend to interface with simulation data.

## Prerequisites

### Automated Installation

You can use one single command to automatically download all the files, create a virtual environment and install all dependencies:

**Linux and macOS:**
```bash
curl -LO https://github.com/aritro-c/StagPlot/archive/refs/heads/main.zip && unzip main.zip && cd StagPlot-main && python3 install.py && rm ../main.zip
```

**Windows:**
```powershell
Invoke-WebRequest -Uri "https://github.com/aritro-c/StagPlot/archive/refs/heads/main.zip" -OutFile "main.zip"; Expand-Archive -Path "main.zip" -Force; cd main\StagPlot-main; python install.py
```

Important for Linux users: If you use VSCode, it is NOT RECCOMMENDED to use the Flatpak/Snap version. Because of it's sandboxed nature it may cause errors finding the proper Python binary. Install VSCode as a system package instead. Check their documentation.

### Manual Installation
If you prefer to set it up manually:

### Linux and macOS

```bash
# Create a virtual environment
python3 -m venv myenv

# Activate it
source myenv/bin/activate

# Install StagPy
pip install stagpy

# Install Scientific Colourmap by Fabio Crameri (Optional)
pip install cmcrameri
```

### Windows

```powershell
# Create a virtual environment
python -m venv myenv

# Activate it
.\myenv\Scripts\activate

# Install StagPy
pip install stagpy

# Install Scientific Colourmap by Fabio Crameri (Optional)
pip install cmcrameri
```

If you are using VSCode, ensure your Python Interpreter is set to the `myenv` you created.
Press ctrl+shift+p (or type ">" in the search box) and select the Python Interpreter as "myenv".

Now you can run the scrips in VSCode.

### FFmpeg Installation

FFmpeg is used by `field_batch.py` if you want to create a movie of the evolution.

#### Linux (Debain based distros such as Ubuntu)
```bash
sudo apt update && sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Windows
```powershell
winget install ffmpeg
```
*Note: You may need to restart your terminal after installation.*

## Core Scripts

### 1. `info.py`
A quick utility to inspect StagYY simulation metadata.

### 2. `field.py`
Plots a single 2D scalar field for a specific point in time/snapshot.

### 3. `field_batch.py`
Generates a sequence of frames for 2D fields over a range of time/snapshots and stitch those plots and make a movie (FFmpeg must be installed on your device).

### 4. `rprof.py`
Plots 1D radial profiles (depth vs. value) for a specific point in time/snapshot.

### 5. `rprof_time.py`
Creates a spcetime plot of a radial-profile parameter (Hovmöller diagram).

### 6. `surf2D_time.py`
Creates spcetime plot of surface parameters (Hovmöller diagram).

### 7. `time.py`
Plots the evolution of global diagnostic parameters over time.

## Reference

For more details on the physics and parameters being plotted, refer to the **StagYY User Guide** and the **StagPy Documentation**.

# StagPlot 
### (UNDER CONSTRUCTION!)

A suite of Python scripts for post-processing and visualizing output from **StagYY**, a numerical mantle convection code. Most of the scripts use the **StagPy** library as a backend to interface with simulation data.

## Prerequisites

### Automated Installation

You can use the provided `install.py` script to automatically create a virtual environment and install all dependencies.

**Linux and macOS:**
```bash
python3 install.py
```

**Windows:**
```powershell
python install.py
```

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

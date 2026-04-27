# StagPlot 
### (UNDER CONSTRUCTION!)

A suite of Python scripts for post-processing and visualizing output from **StagYY**, a numerical mantle convection code. These scripts use the **StagPy** library as a backend to interface with simulation data.

## Prerequisites

It is recommended to use a virtual environment to manage dependencies:

```bash
# Create a virtual environment
python3 -m venv myenv

# Activate it
source myenv/bin/activate

# Install StagPy
pip install stagpy
```

If you are using VSCode, ensure your Python Interpreter is set to the `myenv` you created.
Press ctrl+shift+p (or type ">" in the search box) and select the Python Interpreter as "myenv".

Now you can run the scrips in VSCode using the virtual environment you created.

## Core Scripts

### 1. `info.py`
A quick utility to inspect StagYY simulation metadata.

### 2. `field.py`
Plots a single 2D scalar field for a specific point in time/snapshot.

### 3. `field_batch.py`
Generates a sequence of frames for 2D fields over a range of time/snapshots.

### 4. `rprof.py`
Plots 1D radial profiles (depth vs. value) for a specific point in time/snapshot.

### 5. `rprof_time.py`
Creates a spcetime plot of a radial-profile parameter (Hovmöller diagram).

### 6. `time.py`
Plots the evolution of global diagnostic parameters over time.

## Reference

For more details on the physics and parameters being plotted, refer to the **StagYY User Guide** and the **StagPy Documentation**.

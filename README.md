# StagPlot 
### (UNDER CONSTRUCTION! Expect bugs that will be ironed out)

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

If using VSCode, ensure your Python Interpreter is set to the `myenv` you created.
Press ctrl+shift+p (or type ">" in the search box) and select the Python Interpreter as "myenv".

Now you can run the scrips in VSCode using the virtual environment you created.

## Core Scripts

### 1. `info.py` (Simulation Overview)
A quick utility to inspect StagYY simulation metadata without loading full datasets.

### 2. `field.py` (2D Field Visualization)
Plots a single 2D scalar field (e.g., Temperature, Viscosity, Composition) for a specific point in time.

### 3. `field_batch.py` (Batch 2D Visualization)
Generates a sequence of frames for 2D fields over a range of snapshots.

### 4. `rprof.py` (Radial Profile Analysis)
Plots 1D radial profiles (depth vs. value).

### 5. `rprof_time.py` (Temporal Radial Evolution)
Visualizes how a radial profile evolves over the entire duration of a simulation.

### 6. `time.py` (Time-Series Analysis)
Plots the evolution of global diagnostic parameters over time.

## Reference

For more details on the physics and parameters being plotted, refer to the **StagYY User Guide** and the **StagPy Documentation**.

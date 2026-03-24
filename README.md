# StagPlot

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
- **Features**: Displays run name, path, total snapshots, time span, model geometry, and resolution.
- **Categorization**: Lists all available 2D/3D fields, surface fields, radial profiles, and time-series variables present in the run.
- **Optimization**: Fast execution by only reading the first and last snapshots.

### 2. `field.py` (2D Field Visualization)
Plots a single 2D scalar field (e.g., Temperature, Viscosity, Composition) for a specific point in time.
- **Modes**: Can target a specific snapshot index or the closest snapshot to a target time (in **Myr**).
- **Styling**: Automatic log-scaling for relevant fields (viscosity, strain rate), consistent colorbar labeling, and time-stamping on the plot.

### 3. `field_multi.py` (Batch 2D Visualization)
Generates a sequence of frames for 2D fields over a range of snapshots.
- **Use Case**: Perfect for creating animations or studying temporal evolution of spatial structures.
- **Modes**: supports `constant_frame` (every N snapshots) or `constant_time` (interpolated to target time intervals in **Myr**).
- **Output**: Saves frames to a dedicated directory for easy video encoding.

### 4. `rprof.py` (Radial Profile Analysis)
Plots 1D radial profiles (depth vs. value).
- **Modes**: 
    - `SNAPSHOTS`: Compare different times within a single simulation run.
    - `RUNS`: Compare the same time/snapshot across multiple simulation runs.
- **Styling**: Supports scientific colormaps (Crameri) and handles logarithmic axes for physical variables like viscosity.

### 5. `rprof_time.py` (Temporal Radial Evolution)
Visualizes how a radial profile evolves over the entire duration of a simulation.
- **Visualization**: Creates a 2D pseudocolor plot where the X-axis is Time and the Y-axis is Depth/Radius.
- **Use Case**: Identifying the timing of phase transitions, boundary layer changes, or thermal evolution.

### 6. `time.py` (Time-Series Analysis)
Plots the evolution of global diagnostic parameters over time.
- **Features**: Visualizes parameters like maximum temperature, Nusselt number, root-mean-square velocity, and heat flux.
- **Comparison**: Can plot multiple variables on the same figure or compare variables across different runs.

## Usage

Most scripts contain a `--- USER INPUT ---` section at the top. Update the `data_path` and target variables before running:

```bash
python info.py
python field.py
python time.py
```

## Reference

For more details on the physics and parameters being plotted, refer to the **StagYY User Guide** and the **StagPy Documentation**.

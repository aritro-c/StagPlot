import matplotlib
matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from stagpy.stagyydata import StagyyData
from stagpy import field as sp_field

"""
--- REFERENCE: STAGYY FIELDS ---
PHYSICAL/THERMODYNAMIC:
    T: Temperature                  p: Pressure
    rho: Density                    eta: Viscosity (Log)
    Tcond: Thermal Conductivity     rho4rhs: Density term in RHS
    age: Material age               fSiO2, fMgO, fFeO, fXO, fFeR: Mineral/Oxide fractions

KINEMATICS & DYNAMICS:
    v1, v2, v3: Velocity (x, y, z)  edot: Strain rate (Log)
    sII: 2nd Stress Invariant (Log) s1val: Principal stress eigenvalue
    sx1, sx2, sx3: Stress vectors   stream: Stream function (2D)
    meltvel: Melt velocity (Log)

COMPOSITION & MELTING:
    c: Composition (prim/basalt)    basalt: Basalt fraction
    harzburgite: Harzburgite frac   prim: Primordial layer
    meltfrac: Current melt degree   meltrate: Melting rate
    meltcompo: Melt composition     nmelt: N melt
    cFe: FeO content                hpe: HPE content
    wtr: Water concentration (Log)  contID: ID of continents

NUMERICS:
    rs1, rs2, rs3: Momentum residue rsc: Continuity residue
"""

# --- USER INPUT ---
plot_mode = "snapshot"   # Set to "time" or "snapshot" 
target_time_Myr = 4500    # Used if plot_mode is "time"
target_snapshot = 1872  # Used if plot_mode is "snapshot"

field_to_plot = "T"    

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = True  # Set to True for transparent PNG background

# --- CONFIGURATION ---
# Auto-detect log scale for these fields
LOG_FIELDS = ["eta", "edot", "sII", "v1", "v2", "v3", "meltvel", "wtr", "meltrate"]

# FIELD LIMITS
FIELD_LIMITS = {
    "T": (300, 4000),
    "basalt": (0.0, 1.0),
    "eta": (1e18, 1e25),
    "edot": (1e-18, 1e-12),
    "meltfrac": (0.0, 0.2),
}

FIELD_LABELS = {
    "T": "Temperature",
    "v1": "Velocity (x)",
    "v2": "Velocity (y)",
    "v3": "Velocity (z)",
    "p": "Pressure",
    "eta": "Viscosity",
    "rho": "Density",
    "rho4rhs": "Density term in RHS",
    "trarho": "Density from tracer mass",
    "sII": "Second invariant of stress tensor",
    "sx1": "Principal stress eigenvector (x)",
    "sx2": "Principal stress eigenvector (y)",
    "sx3": "Principal stress eigenvector (z)",
    "s1val": "Principal stress eigenvalue",
    "edot": "Strain rate",
    "Tcond": "Thermal conductivity",
    "c": "Composition",
    "cFe": "FeO content",
    "hpe": "HPE content",
    "wtr": "Water concentration",
    "age": "Age",
    "contID": "ID of continents",
    "rs1": "Momentum residue (x)",
    "rs2": "Momentum residue (y)",
    "rs3": "Momentum residue (z)",
    "rsc": "Continuity residue",
    "basalt": "Basalt fraction",
    "harzburgite": "Harzburgite fraction",
    "impactor": "Impactor fraction",
    "prim": "Primordial layer",
    "meltfrac": "Melt fraction",
    "meltcompo": "Melt composition",
    "meltrate": "Melting rate",
    "meltvel": "Melt velocity",
    "nmelt": "N melt",
    "fSiO2": "fSiO2",
    "fMgO": "fMgO",
    "fFeO": "fFeO",
    "fXO": "fXO",
    "fFeR": "fFeR",
}

# --- 0. STARTUP ---
print(f"{'='*60}\n       STAGPLOT: 2D FIELD VISUALIZATION       \n{'='*60}")

# NOTE: Update this path to your StagYY archive directory
data_path = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_i_01/archive/")

if not data_path.exists():
    print(f"[!] CRITICAL ERROR: Data path does not exist:\n    {data_path}")
    exit(1)

sdat = StagyyData(data_path)
folder_name = data_path.parent.name 
SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

print(f"[+] Data Path: {data_path}")
print(f"[+] Run:       {folder_name}")
print(f"[+] Mode:      {plot_mode.upper()}")
print(f"[+] Field:     {field_to_plot}")

# --- 1. SELECTION LOGIC ---
print(f"\n[INFO] Identifying target snapshot...")
snap_number = None
actual_time_Myr = None

if plot_mode == "time":
    print(f"       Target Time: {target_time_Myr} Myr")
    times, indices = [], []
    for snap in sdat.snaps:
        try:
            t = snap.time if snap.time is not None else snap.timeinfo["time"]
            times.append(t); indices.append(snap.isnap)
        except: continue
    
    if not times:
        print(f"[!] ERROR: No snapshots found with time information.")
        exit(1)

    times, indices = np.array(times), np.array(indices)
    idx = np.abs(times - (target_time_Myr * SEC_PER_MYR)).argmin()
    snap_number, actual_time_Myr = int(indices[idx]), times[idx] / SEC_PER_MYR
    print(f"       Closest Match: Snap {snap_number} at {actual_time_Myr:.2f} Myr")
else:
    print(f"       Target Snapshot: {target_snapshot}")
    try:
        snapshot = sdat.snaps[target_snapshot]
        snap_number = target_snapshot
        t = snapshot.time if snapshot.time is not None else snapshot.timeinfo["time"]
        actual_time_Myr = t / SEC_PER_MYR
        print(f"       Snapshot found at {actual_time_Myr:.2f} Myr")
    except Exception as e:
        print(f"[!] ERROR: Could not access snapshot {target_snapshot}: {e}")
        exit(1)

# --- 2. GENERATE THE PLOT ---
if snap_number is not None:
    try:
        print(f"\n[INFO] Loading field data and generating plot...")
        snapshot = sdat.snaps[snap_number]
        
        # Unpack limits (defaults to None, None if field not in dict)
        f_min, f_max = FIELD_LIMITS.get(field_to_plot, (None, None))
        
        if field_to_plot in LOG_FIELDS:
            # Ensure f_min is positive for LogNorm
            log_min = f_min if f_min is not None else 1e-5
            norm = colors.LogNorm(vmin=log_min, vmax=f_max)
            # Pass ONLY norm to avoid Matplotlib conflict
            fig, ax, mesh, cbar = sp_field.plot_scalar(snapshot, field_to_plot, norm=norm)
        else:
            # Linear scaling uses direct limits
            fig, ax, mesh, cbar = sp_field.plot_scalar(snapshot, field_to_plot, vmin=f_min, vmax=f_max)
        
        # Visual Styling
        unit = snapshot.fields[field_to_plot].meta.dim
        label = FIELD_LABELS.get(field_to_plot, field_to_plot)
        cbar.set_label(f"{label} [{unit}]", size=18)
        cbar.ax.tick_params(labelsize=14)
        ax.tick_params(axis='both', which='major', labelsize=14)
        
        # TIME LABEL ON PLOT
        actual_time_Gyr = actual_time_Myr / 1000
        ax.text(0.5, 0.5, f"{actual_time_Gyr:.3f} Gyr", 
                transform=ax.transAxes, ha="center", va="center", 
                fontsize=20, color="black", 
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
        
        fig.set_size_inches(10, 6)
        plt.tight_layout()
        
        # NAMING SCHEME: [folder]_[field]_snap-[number]_[time]-Gyr.png
        save_name = f"{folder_name}_{field_to_plot}_snap-{snap_number}_{actual_time_Gyr:.3f}-Gyr.png"
        print(f"[INFO] Saving figure to: {save_name}")
        fig.savefig(save_name, dpi=300, transparent=TRANSPARENT_PNG)
        
        if EXPORT_SVG:
            svg_save_name = save_name.replace(".png", ".svg")
            print(f"[INFO] Exporting SVG:    {svg_save_name}")
            fig.savefig(svg_save_name, transparent=True, dpi=300)

        plt.close(fig)
        print(f"[SUCCESS] Plot generated successfully.")

    except Exception as e:
        print(f"[!] ERROR: An error occurred during plotting: {e}")
        import traceback
        traceback.print_exc()

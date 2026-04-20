import matplotlib
matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from stagpy.stagyydata import StagyyData
from stagpy import field as sp_field

"""
--- REFERENCE: STAGYY FIELD EXPLANATIONS ---
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
field_to_plot = "T"  
snap_min = 1500
snap_max = 6000

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = True  # Set to True for transparent PNG background

# --- TOGGLE ---
mode = "constant_frame" # Options: "constant_time" or "constant_frame"

# --- CONSTANT_TIME SETTINGS ---
dt_Myr = 1 # Time step in Myr

# --- CONSTANT_FRAME SETTINGS ---
snap_step = 1   # 1 = every snapshot, 10 = every 10th snapshot, etc.

# --- CONFIGURATION ---
# Auto-detect log scale for these fields
LOG_FIELDS = ["eta", "edot", "sII", "v1", "v2", "v3", "meltvel", "wtr", "meltrate"]

# FIELD LIMITS (Min, Max)
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

# --- PLOT SETTINGS ---
fig_width = 7
fig_height = 6

# --- 0. STARTUP ---
print(f"{'='*60}\n       STAGPLOT: MULTI-FIELD VISUALIZATION       \n{'='*60}")

# --- DATA PATH ---
data_path = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_i_01/archive")

if not data_path.exists():
    print(f"[!] CRITICAL ERROR: Data path does not exist:\n    {data_path}")
    exit(1)

sdat = StagyyData(data_path)
folder_name = data_path.parent.name 

print(f"[+] Data Path: {data_path}")
print(f"[+] Run:       {folder_name}")
print(f"[+] Field:     {field_to_plot}")
print(f"[+] Mode:      {mode.upper()}")
if mode == "constant_time":
    print(f"[+] Interval:  {dt_Myr} Myr")
else:
    print(f"[+] Step:      Every {snap_step} snapshot(s)")

# Create Directory: [folder_name]_frames_[field_to_plot]_[mode]
output_dir = Path(f"{folder_name}_frames_{field_to_plot}_{mode}")
output_dir.mkdir(parents=True, exist_ok=True)
print(f"[+] Output:    {output_dir}")

SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

# --- 1. PREPARE THE FRAME LIST ---
frames_to_render = [] 

print(f"\n[INFO] Scanning snapshots {snap_min} to {snap_max}...")
available_snaps = []
available_times = []

for n in range(snap_min, snap_max + 1):
    try:
        snap = sdat.snaps[n]
        # StagPy fix: use snap.time or fallback to snap.timeinfo["time"]
        t = snap.time
        if t is None:
            t = snap.timeinfo["time"]
            
        available_snaps.append(snap.isnap)
        available_times.append(t)
    except:
        continue

available_snaps = np.array(available_snaps)
available_times = np.array(available_times)

if len(available_snaps) == 0:
    print("[!] ERROR: No data found in that snapshot range.")
    exit(1)
else:
    if mode == "constant_time":
        t_start = available_times.min()
        t_end = available_times.max()
        target_times = np.arange(t_start, t_end, dt_Myr * SEC_PER_MYR)
        
        for t_target in target_times:
            idx = np.abs(available_times - t_target).argmin()
            # Store (snapshot_number, actual_time_from_file)
            frames_to_render.append((int(available_snaps[idx]), available_times[idx]))
    else:
        # constant_frame mode
        for i in range(0, len(available_snaps), snap_step):
            frames_to_render.append((int(available_snaps[i]), available_times[i]))

    print(f"[INFO] Prepared {len(frames_to_render)} frames for rendering.")

    # --- 2. RENDER THE FRAMES ---
    print(f"\n[INFO] Starting rendering loop...")
    for i, (snap_number, t_val) in enumerate(frames_to_render):
        try:
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
                fig, ax, mesh, cbar = sp_field.plot_scalar(snapshot, field_to_plot, 
                                                         vmin=f_min, vmax=f_max)
            
            # Colorbar labels
            unit = snapshot.fields[field_to_plot].meta.dim
            display_name = FIELD_LABELS.get(field_to_plot, field_to_plot)
            cbar.set_label(f"{display_name} [{unit}]", size=18)
            cbar.ax.tick_params(labelsize=14)
            ax.tick_params(axis='both', which='major', labelsize=14)
            
            # Time Label on Plot
            time_Gyr = t_val / SEC_PER_GYR
            label_text = f"{time_Gyr:.3f} Gyr"
            
            ax.text(0.5, 0.5, label_text, 
                    transform=ax.transAxes, ha="center", va="center", 
                    fontsize=24, color="black", 
                    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
            
            fig.set_size_inches(fig_width, fig_height)
            plt.tight_layout()
            
            # FILE NAMING SCHEME
            file_name = f"frame_{snap_number:05d}.png"
            fig.savefig(output_dir / file_name, dpi=300, transparent=TRANSPARENT_PNG)

            if EXPORT_SVG:
                svg_file_name = file_name.replace(".png", ".svg")
                fig.savefig(output_dir / svg_file_name, transparent=True, dpi=300)

            plt.close(fig) 
            
            if i % 10 == 0 or i == len(frames_to_render) - 1:
                print(f"   [OK] Saved: {file_name} ({i+1}/{len(frames_to_render)})")
                
        except Exception as e:
            print(f"   [!] Error at Snap {snap_number}: {e}")
            plt.close()

    print(f"\n[SUCCESS] Rendering complete. Frames saved to:\n          {output_dir}")

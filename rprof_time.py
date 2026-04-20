import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
from stagpy.stagyydata import StagyyData
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import LogFormatterSciNotation

# --- COLOURMAP SYSTEM ---
#  Try to import Fabio Crameri's colormaps
try:
    from cmcrameri import cm
    HAS_CRAMERI = True
except ImportError:
    HAS_CRAMERI = False


# --- FULL LIST OF RPROF PARAMETERS ---
# Use these strings in 'FIELDS_TO_PLOT' to change the data being visualized.
ALL_RPROF_FIELDS = [
    "r",            # Radial coordinate [m]
    "Tmean",        # Temperature [K]
    "Tmin",         # Min temperature [K]
    "Tmax",         # Max temperature [K]
    "vrms",         # rms velocity [m/s]
    "vmin",         # Min velocity [m/s]
    "vmax",         # Max velocity [m/s]
    "vzabs",        # Radial velocity [m/s]
    "vzmin",        # Min radial velocity [m/s]
    "vzmax",        # Max radial velocity [m/s]
    "vhrms",        # Horizontal velocity [m/s]
    "vhmin",        # Min horiz velocity [m/s]
    "vhmax",        # Max horiz velocity [m/s]
    "etalog",       # Viscosity [Pa.s]
    "etamin",       # Min viscosity [Pa.s]
    "etamax",       # Max viscosity [Pa.s]
    "elog",         # Strain rate [1/s]
    "emin",         # Min strain rate [1/s]
    "emax",         # Max strain rate [1/s]
    "slog",         # Stress [Pa]
    "smin",         # Min stress [Pa]
    "smax",         # Max stress [Pa]
    "whrms",        # Horizontal vorticity [1/s]
    "whmin",        # Min horiz vorticity [1/s]
    "whmax",        # Max horiz vorticity [1/s]
    "wzrms",        # Radial vorticity [1/s]
    "wzmin",        # Min radial vorticity [1/s]
    "wzmax",        # Max radial vorticity [1/s]
    "drms",         # Divergence [1/s]
    "dmin",         # Min divergence [1/s]
    "dmax",         # Max divergence [1/s]
    "enadv",        # Advection [W/m2]
    "endiff",       # Diffusion [W/m2]
    "enradh",       # Radiogenic heating [W/m2]
    "enviscdiss",   # Viscous dissipation [W/m2]
    "enadiabh",     # Adiabatic heating [W/m2]
    "bsmean",       # Basalt content [1]
    "bsmin",        # Min basalt content [1]
    "bsmax",        # Max basalt content [1]
    "rhomean",      # Density [kg/m3]
    "rhomin",       # Min density [kg/m3]
    "rhomax",       # Max density [kg/m3]
    "airmean",      # Air [1]
    "airmin",       # Min air [1]
    "airmax",       # Max air [1]
    "primmean",     # Primordial [1]
    "primmin",      # Min primordial [1]
    "primmax",      # Max primordial [1]
    "ccmean",       # Continental crust [1]
    "ccmin",        # Min continental crust [1]
    "ccmax",        # Max continental crust [1]
    "fmeltmean",    # Melt fraction [1]
    "fmeltmin",     # Min melt fraction [1]
    "fmeltmax",     # Max melt fraction [1]
    "metalmean",    # Metal [1]
    "metalmin",     # Min metal [1]
    "metalmax",     # Max metal [1]
    "gsmean",       # Grain size [m]
    "gsmin",        # Min grain size [m]
    "gsmax",        # Max grain [m]
    "viscdisslog",  # Viscous dissipation [W/m2]
    "viscdissmin",  # Min visc dissipation [W/m2]
    "viscdissmax",  # Max visc dissipation [W/m2]
    "advtot",       # Advection [W/m2]
    "advdesc",      # Downward advection [W/m2]
    "advasc",       # Upward advection [W/m2]
    "tcondmean",    # Conductivity [W/(m.K)]
    "tcondmin",     # Min conductivity [W/(m.K)]
    "tcondmax",     # Max conductivity [W/(m.K)]
    "impmean",      # Impactor fraction [1]
    "impmin",       # Min impactor fraction [1]
    "impmax",       # Max impactor fraction [1]
    "hzmean",       # Harzburgite fraction [1]
    "hzmin",        # Min harzburgite fraction [1]
    "hzmax",        # Max harzburgite fraction [1]
    "TTGmean",      # TTG fraction [1]
    "TTGmin",       # Min TTG fraction [1]
    "TTGmax",       # Max TTG fraction [1]
    "edismean",     # Dislocation creep fraction [1]
    "edismin",      # Min dislocation creep fraction [1]
    "edismax",      # Max dislocation creep fraction [1]
    "egbsmean",     # Grain boundary sliding fraction [1]
    "egbsmin",      # Min grain boundary sliding fraction [1]
    "egbsmax",      # Max grain boundary sliding fraction [1]
    "ePeimean",     # Peierls creep fraction [1]
    "ePeimin",      # Min Peierls creep fraction [1]
    "ePeimax",      # Max Peierls creep fraction [1]
    "eplamean",     # Plasticity fraction [1]
    "eplamin",      # Min plasticity fraction [1]
    "eplamax",      # Max plasticity fraction [1]
    "dr",           # Cell thicknesses [m]
    "diff",         # Diffusion flux [W/m2]
    "diffs",        # Scaled diffusion flux [W/m2]
    "advts",        # Scaled advection flux [W/m2]
    "advds",        # Scaled downward advection flux [W/m2]
    "advas",        # Scaled upward advection flux [W/m2]
    "energy",       # Total heat flux [W/m2]
]



# --- USER CONFIGURATION ---
# Define the path to your StagYY 'archive' directory.
DATA_ROOT = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_i_01/archive/")

# Fields to visualize ["Tmean", "fmeltmax", "elog"], (Y-axis = Depth, X-axis = Time, Color = Field Value)
FIELDS_TO_PLOT = ["vrms"]   

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = True  # Set to True for transparent PNG background

# Manual limits for specific fields to ensure consistency across different runs.
FIELD_LIMITS = {
    "Tmax": (500, 4000),
    "Tmean": (500, 4000),
    "vmax": (1e-6, 1.2e-3),
   # "vrms": (1e-8, 1e-2), 
    "fmeltmax": (0, 1.0),
    "bsmean": (0, 1.0),
   # "etalog": (1e18, 1e24),
}

# Downsampling: 1 = every step, 10 = every 10th step.
SAMPLE_STEP = 10

# Colormap Preferences
USE_CRAMERI = True
SEQUENTIAL_MAP = "lajolla"   # Good for T, viscosity, composition
DIVERGING_MAP  = "lajolla"  # Good for velocity, divergence, flux

def run_visualizer():
    # --- 1. INITIALIZATION ---
    print(f"{'='*60}\n RPROF-TIME \n{'='*60}")
    
    if USE_CRAMERI and not HAS_CRAMERI:
        print("[!] WARNING: 'cmcrameri' package not found. Using Matplotlib defaults.")
        print("    HINT: To use 'vik' and other scientific colormaps, install it via:")
        print("          pip install cmcrameri")

    if not DATA_ROOT.exists():
        print(f"CRITICAL ERROR: The path '{DATA_ROOT}' does not exist.")
        print("Please check your 'DATA_ROOT' configuration at the top of the script.")
        return

    print(f"[*] Loading StagYY Data at: {DATA_ROOT.name}")
    sdat = StagyyData(DATA_ROOT)
    
    snaps_to_process = sdat.snaps[::SAMPLE_STEP]

    # Data structures for plotting
    times, depths = [], None
    plot_data = {f: [] for f in FIELDS_TO_PLOT}
    field_meta = {f: {"title": "", "log": False} for f in FIELDS_TO_PLOT}

    # --- 2. DATA COLLECTION LOOP ---
    print(f"[*] Reading {len(FIELDS_TO_PLOT)} fields across snapshots...")

    for idx, snap in enumerate(snaps_to_process):
        try:
            # Progress update in console
            if (idx + 1) % 10 == 0:
                print(f"    > Reading Snapshot {idx+1} (Step: {snap.istep})", end='\r')

            # Unit Conversion: Seconds to Megayears (Myr)
            current_time = snap.time / (3600 * 24 * 365.25 * 1e6)
            
            # Temporary storage to ensure ALL fields exist for this snapshot before adding
            temp_field_data = {}
            for field in FIELDS_TO_PLOT:
                rprof = snap.rprofs[field] # This is where 'Details: 0' likely happened
                temp_field_data[field] = rprof.values
                
                # Capture metadata only once
                if not field_meta[field]["title"]:
                    desc, unit = rprof.meta.description, rprof.meta.dim
                    field_meta[field]["title"] = f"{desc} ({unit})" if unit else desc
                    
                    log_keywords = ["log", "eta", "slog", "visc", "vrms", "vmax", "vmin"]
                    if any(k in field.lower() for k in log_keywords):
                        field_meta[field]["log"] = True

                # Calculate depths (m to km) once
                if depths is None:
                    r_surf = np.max(rprof.rad)
                    depths = (r_surf - rprof.rad) / 1e3 

            # If we reached here, all fields were found successfully
            times.append(current_time)
            for field in FIELDS_TO_PLOT:
                plot_data[field].append(temp_field_data[field])
        
        except Exception as e:
            # More descriptive error reporting
            print(f"\n[!] WARNING: Skipping snapshot {idx} (Step {snap.istep})")
            print(f"    Error Type: {type(e).__name__} | Details: {e}")
            continue

    # --- 3. FINAL VALIDATION ---
    if not times:
        print("\n\nERROR: No data was collected. Possible reasons:")
        print(f"1. Fields {FIELDS_TO_PLOT} do not exist in these snapshots.")
        print("2. The StagYY output files are corrupted or empty.")
        return

    print(f"\n[*] Data loading complete ({len(times)} valid snapshots). Generating plots...")

    # --- 4. PLOTTING ENGINE ---
    fig, axes = plt.subplots(len(FIELDS_TO_PLOT), 1, 
                             figsize=(12, 4 * len(FIELDS_TO_PLOT)), 
                             sharex=True, squeeze=False)

    for i, field in enumerate(FIELDS_TO_PLOT):
        ax = axes[i, 0]
        data_matrix = np.array(plot_data[field]).T
        
        vmin, vmax = FIELD_LIMITS.get(field, (None, None))
        
        if field_meta[field]["log"]:
            data_matrix = np.clip(data_matrix, 1e-35, None) 
            if vmin is None or vmin <= 0: 
                vmin = np.nanmin(data_matrix[data_matrix > 0])
            if vmax is None: 
                vmax = np.nanmax(data_matrix)
            norm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            norm = Normalize(vmin=vmin, vmax=vmax)

        diverging_keywords = ["vz", "vh", "drms", "adv"]
        is_diverging = any(k in field.lower() for k in diverging_keywords)
        cmap_name = DIVERGING_MAP if is_diverging else SEQUENTIAL_MAP

        import matplotlib
        if USE_CRAMERI and HAS_CRAMERI:
            try:
                cmap = getattr(cm, cmap_name)
            except AttributeError:
                # Fallback to standard matplotlib if the crameri map is not found
                if cmap_name in matplotlib.colormaps:
                    cmap = cmap_name
                else:
                    cmap = 'RdBu_r' if is_diverging else 'magma'
        else:
            # Not using Crameri or it's not available: check if the requested map is standard
            if cmap_name in matplotlib.colormaps:
                cmap = cmap_name
            else:
                # Use hardcoded fallbacks if the user chose a name not in matplotlib
                # (e.g. they set it to a crameri name but don't have it installed)
                cmap = 'RdBu_r' if is_diverging else 'magma'

        im = ax.pcolormesh(np.array(times), depths, data_matrix, 
                           shading='auto', cmap=cmap, norm=norm)
        
        ax.set_title(field_meta[field]["title"], fontweight='bold', fontsize=13, loc='center')
        ax.set_ylabel("Depth (km)", fontsize=11)
        ax.invert_yaxis() 
        
        if field_meta[field]["log"]:
            formatter = LogFormatterSciNotation(base=10, labelOnlyBase=False)
            cbar = plt.colorbar(im, ax=ax, pad=0.01, aspect=15, format=formatter)
        else:
            cbar = plt.colorbar(im, ax=ax, pad=0.01, aspect=15)
            if (vmax and (vmax > 1000 or vmax < 0.01)):
                cbar.formatter.set_powerlimits((0, 0))

    axes[-1, 0].set_xlabel("Time (Myr)", fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 0.95, 1])

    save_name = f"evol_{'_'.join(FIELDS_TO_PLOT)}.png"
    fig.savefig(save_name, dpi=300, bbox_inches='tight', transparent=TRANSPARENT_PNG)
    print(f"[*] SUCCESS: Plot saved as '{save_name}'")

    if EXPORT_SVG:
        svg_save_name = save_name.replace(".png", ".svg")
        fig.savefig(svg_save_name, bbox_inches='tight', transparent=True, dpi=300)
        print(f"[*] SUCCESS: SVG exported as '{svg_save_name}'")
    
    plt.show()

if __name__ == "__main__":
    try:
        run_visualizer()
    except KeyboardInterrupt:
        print("\n[!] Execution interrupted by user.")
        sys.exit(0)

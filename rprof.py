import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import LogFormatterSciNotation

# StagPy is the primary library for handling StagYY output
from stagpy.stagyydata import StagyyData

# --- 1. CONSTANTS & COMPATIBILITY ---
SECONDS_IN_YEAR = 3.15576e7
YEARS_IN_MYR = 1e6

# Try to import Crameri colormaps for better perceptual scaling
try:
    from cmcrameri import cm
    HAS_CRAMERI = True
except ImportError:
    HAS_CRAMERI = False

# --- 2. CONFIGURATION ---
# MODE: "SNAPSHOTS" (Compare different times in ONE run) 
#       "RUNS" (Compare the same time/snapshot across MULTIPLE runs)
PLOT_MODE = "RUNS" 

# TIME SELECTION:
# If TIME_TARGETS has values, the script ignores 'snapshot_list' and finds 
# the closest available data to these specific times (in Myr).
TIME_TARGETS = [2] # [1, 2, 3]
snapshot_list = [1400] # [1400, 1500] Fallback if TIME_TARGETS is empty

# DATA SOURCE:
# Provide a label and the system path to the StagYY output directory.
RUN_PATHS = {
    "Venus_Imp6": "/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/festus/venus_imp6/archive/",
    "Venus_Imp5": "/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/festus/venus_imp5/archive/", 
}

# PLOT SETTINGS:
field_to_plot = "Tmean"  # Choose from the ALL_RPROF_FIELDS list below

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = True  # Set to True for transparent PNG background

# MANUAL AXIS LIMITS:
FIELD_LIMITS = {
    "etalog": (1e18, 1e22), 
    "vrms": (1e-8, 1e-2),   
    "fmeltmean": (0, 1),
}

# VISUAL STYLING:
LINE_STYLES = ["-", "--", "-.", ":"]
USE_CRAMERI = True
CRAMERI_MAP = "nuuk"

# --- 3. REFERENCE: ALL AVAILABLE RPROF FIELDS ---
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


# --- 4. HELPER FUNCTIONS ---

def find_closest_snap(sdata, target_myr):
    """Finds integer snapshot index closest to target time in Myr."""
    target_sec = target_myr * YEARS_IN_MYR * SECONDS_IN_YEAR
    try:
        times = [s.time for s in sdata.snaps]
        snaps = [s.isnap for s in sdata.snaps]
        idx = np.argmin(np.abs(np.array(times) - target_sec))
        return snaps[idx]
    except Exception as e:
        print(f"   [!] Error mapping time {target_myr} Myr to a snapshot: {e}")
        return None

# --- 5. MAIN EXECUTION BLOCK ---

def main():
    print(f"{'='*60}\n       RPROF       \n{'='*60}")
    print(f"Target Field: {field_to_plot}")
    print(f"Mode:         {PLOT_MODE}")

    if USE_CRAMERI and not HAS_CRAMERI:
        print("[!] WARNING: 'cmcrameri' package not found. Using Matplotlib defaults.")
        print("    HINT: To use 'nuuk' and other scientific colormaps, install it via:")
        print("          pip install cmcrameri")

    try:
        fig, ax = plt.subplots(figsize=(7, 9))
        labels_set = False
        
        print(f"Attempting to load {len(RUN_PATHS)} run(s)...")
        sims = {}
        for name, path in RUN_PATHS.items():
            if not Path(path).exists():
                print(f"   [!] FAILED: Path for '{name}' does not exist: {path}")
                continue
            sims[name] = StagyyData(Path(path))
            print(f"   [+] Loaded: {name}")

        if not sims:
            raise RuntimeError("No valid simulation data could be loaded. Check your RUN_PATHS.")

        # Determine Data Iterator
        iterator = []
        if PLOT_MODE == "SNAPSHOTS":
            run_name = list(sims.keys())[0]
            sdata = sims[run_name]
            active_snaps = [find_closest_snap(sdata, t) for t in TIME_TARGETS] if TIME_TARGETS else snapshot_list
            iterator = [(run_name, snap) for snap in active_snaps if snap is not None]
        else:
            for name, sdata in sims.items():
                active_snaps = [find_closest_snap(sdata, t) for t in TIME_TARGETS] if TIME_TARGETS else snapshot_list
                for s in active_snaps:
                    if s is not None:
                        iterator.append((name, s))

        num_plots = len(iterator)
        import matplotlib
        cmap_obj = None
        if USE_CRAMERI and HAS_CRAMERI:
            try:
                cmap_obj = getattr(cm, CRAMERI_MAP)
            except AttributeError:
                if CRAMERI_MAP in matplotlib.colormaps:
                    cmap_obj = matplotlib.colormaps[CRAMERI_MAP]
        
        if cmap_obj is None and CRAMERI_MAP in matplotlib.colormaps:
            cmap_obj = matplotlib.colormaps[CRAMERI_MAP]
            
        line_colors = [None] * num_plots
        if cmap_obj:
            line_colors = [cmap_obj(i / (num_plots - 1)) if num_plots > 1 else cmap_obj(0.5) for i in range(num_plots)]

        # --- Plotting Loop ---
        print(f"\nProcessing {num_plots} profiles...")
        for idx, (run_label, isnap) in enumerate(iterator):
            try:
                # Step A: Access snapshot and extract the profile directly
                snapshot = sims[run_label].snaps[isnap]
                rprof_obj = snapshot.rprofs[field_to_plot]
                
                # Step B: Data Extraction
                time_myr = snapshot.time / (SECONDS_IN_YEAR * YEARS_IN_MYR)
                radius = rprof_obj.rad / 1e6
                values = rprof_obj.values
                
                # Step C: Styling
                l_style = LINE_STYLES[idx % len(LINE_STYLES)]
                legend_label = f"{run_label} ({time_myr:.1f} Myr)" if PLOT_MODE == "RUNS" else f"{time_myr:.1f} Myr"
                
                ax.plot(values, radius, label=legend_label, linewidth=1.8, linestyle=l_style, color=line_colors[idx])
                print(f"   [OK] {run_label} | Snap {isnap} ({time_myr:.1f} Myr)")

                # Step D: Labels & Formatting
                if not labels_set:
                    description = rprof_obj.meta.description
                    unit = rprof_obj.meta.dim
                    if "eta" in field_to_plot and unit == "Pa": unit = "Pa s"

                    ax.set_xlabel(f"{description} [{unit}]" if unit else description, fontsize=12)
                    ax.set_ylabel("Radius [10$^6$ m]", fontsize=12)
                    
                    log_keywords = ["log", "eta", "slog", "visc", "vrms", "strain"]
                    if any(k in field_to_plot.lower() for k in log_keywords):
                        ax.set_xscale('log')
                        ax.xaxis.set_major_formatter(LogFormatterSciNotation())
                    labels_set = True

            except Exception as e:
                print(f"   [!] Error: Failed to process {run_label} Snap {isnap}. Detail: {e}")
                continue

        # --- Final Polish ---
        if field_to_plot in FIELD_LIMITS:
            ax.set_xlim(FIELD_LIMITS[field_to_plot])
        
        ax.set_ylim(3.0, 6.2)
        ax.legend(loc='best', frameon=True, fontsize=10)
        ax.grid(True, which="both", ls="-", alpha=0.2)
        
        title_mode = f"Comparison of {len(RUN_PATHS)} Runs" if PLOT_MODE == "RUNS" else f"Evolution: {run_label}"
        ax.set_title(f"{title_mode}\nField: {field_to_plot}", fontsize=14)
        
        plt.tight_layout()
        save_name = f"rprof_{field_to_plot}.png"
        fig.savefig(save_name, dpi=300, transparent=TRANSPARENT_PNG)
        print(f"\n[SUCCESS] Figure saved as: {save_name}")

        if EXPORT_SVG:
            svg_save_name = save_name.replace(".png", ".svg")
            fig.savefig(svg_save_name, transparent=True, dpi=300)
            print(f"[SUCCESS] SVG exported as:  {svg_save_name}")

        plt.show()

    except Exception as e:
        print(f"\n{'#'*60}\n CRITICAL ERROR IN MAIN LOOP:\n {e}\n{'#'*60}")

if __name__ == "__main__":
    main()

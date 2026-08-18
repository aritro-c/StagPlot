import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import LogFormatterSciNotation

# StagPy is the primary library for handling StagYY output
from stagpy.stagyydata import StagyyData

from rich.console import Console
console = Console()

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
    "Venus_Imp6": "/run/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/archive_runs/euler/i3D_02/archive/",
   # "Venus_Imp5": "/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/festus/venus_imp5/archive/", 
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

"""
--- REFERENCE: ALL AVAILABLE RPROF FIELDS ---
BASIC PHYSICS & DYNAMICS:
    r: Radial coordinate            vrms/vmin/vmax: Velocity
    vzabs/vzmin/vzmax: Radial vel   vhrms/vhmin/vhmax: Horiz velocity
    whrms/whmin/whmax: Horiz vort   wzrms/wzmin/wzmax: Radial vorticity
    drms/dmin/dmax: Divergence      dr: Cell thicknesses

THERMAL STATE:
    Tmean/Tmin/Tmax: Temperature    tcondmean/min/max: Conductivity
    
RHEOLOGY & STRESS:
    etalog/etamin/etamax: Viscosity elog/emin/emax: Strain rate
    slog/smin/smax: Stress          edismean/min/max: Disloc creep frac
    egbsmean/min/max: GBS frac      ePeimean/min/max: Peierls creep frac
    eplamean/min/max: Plasticity

HEAT FLUX & ENERGY:
    energy: Total heat flux         enadv: Advection
    endiff: Diffusion               enradh: Radiogenic heating
    enviscdiss: Visc dissipation    enadiabh: Adiabatic heating
    viscdisslog/min/max: Visc diss  advtot: Total advection flux
    advdesc: Downward advection     advasc: Upward advection
    diff/diffs: Diffusion flux      advts/advds/advas: Scaled adv fluxes

COMPOSITION, MELT, & MINERALOGY:
    rhomean/rhomin/rhomax: Density  fmeltmean/min/max: Melt fraction
    bsmean/bsmin/bsmax: Basalt      hzmean/hzmin/hzmax: Harzburgite
    primmean/min/max: Primordial    airmean/min/max: Air fraction
    ccmean/min/max: Cont crust      metalmean/min/max: Metal
    impmean/min/max: Impactor       TTGmean/min/max: TTG fraction
    gsmean/gsmin/gsmax: Grain size
"""

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
        console.print(f"   [bold red][!][/bold red] Error mapping time {target_myr} Myr to a snapshot: {e}")
        return None

# --- 5. MAIN EXECUTION BLOCK ---

def main():
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]       RPROF       [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[green][+][/green] Target Field: [bold magenta]{field_to_plot}[/bold magenta]")
    console.print(f"[green][+][/green] Mode:         [bold magenta]{PLOT_MODE}[/bold magenta]")

    if USE_CRAMERI and not HAS_CRAMERI:
        console.print("[bold yellow][!] WARNING:[/bold yellow] 'cmcrameri' package not found. Using Matplotlib defaults.")
        console.print("    [dim]HINT: To use 'nuuk' and other scientific colormaps, install it via:[/dim]")
        console.print("    [dim]      pip install cmcrameri[/dim]")

    try:
        fig, ax = plt.subplots(figsize=(7, 9))
        labels_set = False
        
        console.print(f"Attempting to load [yellow]{len(RUN_PATHS)}[/yellow] run(s)...")
        sims = {}
        for name, path in RUN_PATHS.items():
            if not Path(path).exists():
                console.print(f"   [bold red][!] FAILED:[/bold red] Path for '{name}' does not exist: {path}")
                continue
            sims[name] = StagyyData(Path(path))
            console.print(f"   [bold green][+][/bold green] Loaded: [yellow]{name}[/yellow]")

        if not sims:
            raise RuntimeError("No valid simulation data could be loaded. Check your RUN_PATHS.")

        # Determine Data Iterator
        iterator = []
        with console.status("[bold green]Finding target snapshots...", spinner="dots"):
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
        console.print(f"\nProcessing [yellow]{num_plots}[/yellow] profiles...")
        for idx, (run_label, isnap) in enumerate(iterator):
            try:
                with console.status(f"[bold green]Processing '{run_label}' Snap {isnap}...", spinner="dots"):
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
                
                console.print(f"   [bold green][OK][/bold green] [white]{run_label}[/white] | Snap {isnap} ({time_myr:.1f} Myr)")

            except Exception as e:
                console.print(f"   [bold red][!] Error:[/bold red] Failed to process [yellow]{run_label}[/yellow] Snap {isnap}. [dim]Detail: {e}[/dim]")
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
        console.print(f"\n[bold green][SUCCESS][/bold green] Figure saved as: [yellow]{save_name}[/yellow]")

        if EXPORT_SVG:
            svg_save_name = save_name.replace(".png", ".svg")
            fig.savefig(svg_save_name, transparent=True, dpi=300)
            console.print(f"[bold green][SUCCESS][/bold green] SVG exported as:  [yellow]{svg_save_name}[/yellow]")

        plt.show()

    except Exception as e:
        console.print(f"\n[bold red]{'#'*60}\n CRITICAL ERROR IN MAIN LOOP:\n {e}\n{'#'*60}[/bold red]")

if __name__ == "__main__":
    main()

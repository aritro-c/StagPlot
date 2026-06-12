import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import LogFormatterSciNotation

# StagPy is the primary library for handling StagYY output
from stagpy.stagyydata import StagyyData
from stagpy import phyvars
from rich.console import Console

"""
--- REFERENCE: STAGYY TIME SERIES FIELDS ---
BASIC PHYSICS & DYNAMICS:
    time: Time                      dt: Time increment
    dTdt: T-derivative              Vmin/rms/max: Velocity
    ra_eff: Effective Ra            mobility: Plates mobility
    ebalance: Energy balance

THERMAL STATE:
    Tmin/mean/max: Temperature      Tsurf/cmb: Boundary Temp
    Tpotl: Potential Temp           ts_core/tc_core: Core Temp

HEAT FLUX & NUSSELT:
    F_top/bot: Heat flux            Nu_top/bot: Nusselt number

RHEOLOGY (VISCOSITY):
    eta_min/max: Viscosity          eta_amean/gmean: Avg Viscosity

MELTING & VOLCANISM:
    F_mean/max: Molten fraction     erupt_rate: Eruption rate
    erupta/total: Erupta            erupt_heatflux: Erupta heat
    intruda: Intruda                H_melt: Melting heat flux

HEATING SOURCES/SINKS:
    H_int: Internal heating         H_diffus: Heat diffusion
    H_VD: Viscous dissipation       H_AH: Adiabatic heating
    H_cool: Cooling                 H_impacts: Impact heating

COMPOSITION & TRACERS:
    C_min/mean/max: Concentration   entrainment: Entrainment
    Cmass_error: Cmass error        denstramin/mean/max: Tracer density

VOLATILES & NOBLE GASES:
    mH2O_total/mantle: H2O mass     outgassed_water: H2O outgassed
    outgassed_carbon: CO2 out       outgassed_nitrogen: N2 out
    outgassed_40Ar/4He: Ar/He out

CORE & GEOMETRY:
    r_innercore: Inner core radius  s_core: Core size
    Psurf: Ground pressure
"""

# --- 1. CONFIGURATION ---

# Define your runs, their system paths, and visual styles here.
# Note: 'color' can be a name (e.g., 'red'), None, or "none" to use Crameri's colourmaps.
RUN_CONFIG = {
  
    "HDF": {
        "path": "/home/aritro/Documents/Academia/#PhD/StagYY/archive_runs/hdf/archive/hdf/",
        "style": "-",     
        "color": "red"     
    #},
      #"Scaled (Festus)": {
        #"path": "/run/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/archive_runs/lipwig/v_atm_01/archive/",
        #"style": "--",      
        #"color": "orange"    
    #},
     #"Scaled (Lipwig)": {
      #  "path": "/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/lipwig/v_i_SCLD/archive/",
      #  "style": "--",      
      #  "color": "blue"    
    },
}

field_to_plot = "mobility" 

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = False  # Set to True for transparent PNG background

# --- AXIS LIMITS ---
# Set X_LIMITS to (min, max) in Gyr, or None for automatic scaling
X_LIMITS = None 

# MANUAL Y-AXIS LIMITS:
# Add fields here to force specific Y-axis ranges (min, max).
FIELD_LIMITS = {
    #"Tmean": (500, 4000),
    #"Vrms": (1e-8, 1e-2),
    "F_mean": (0, 0.5),
    "eta_max": (1e21, 1e27),
}

# --- VISUAL OPTIONS ---
USE_CRAMERI = False
SEQUENTIAL_MAP = "roma"
DIVERGING_MAP  = "nuuk"

# --- 3. CONSTANTS ---
SECONDS_IN_GYR = 3.15576e7 * 1e9

# Try to import Fabio Crameri's colormaps; fallback if not installed
try:
    from cmcrameri import cm
    HAS_CRAMERI = True
except ImportError:
    HAS_CRAMERI = False

console = Console()

# --- 4. MAIN EXECUTION ---

def main():
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]                STAGPLOT: TIME-SERIES                [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    
    try:
        display_name = phyvars.TIME[field_to_plot].description
    except KeyError:
        display_name = field_to_plot
        
    console.print(f"[green][+][/green] Target Field: [bold magenta]{display_name}[/bold magenta]")

    if USE_CRAMERI and not HAS_CRAMERI:
        console.print("[bold yellow][!] WARNING:[/bold yellow] 'cmcrameri' package not found. Using Matplotlib defaults.")
        console.print("    [dim]HINT: To use 'roma', 'nuuk' and other scientific colormaps, install it via:[/dim]")
        console.print("    [dim]      pip install cmcrameri[/dim]")

    try:
        # Initialize Figure
        fig, ax = plt.subplots(figsize=(9, 5)) 
        labels_set = False
        
        # Determine if we should use a diverging color map
        diverging_keywords = ["dt", "balance", "cool", "flux", "diff"]
        is_diverging = any(k in field_to_plot.lower() for k in diverging_keywords)
        
        num_runs = len(RUN_CONFIG)
        
        # Handle automatic color generation
        import matplotlib
        cmap_name = DIVERGING_MAP if is_diverging else SEQUENTIAL_MAP
        cmap_obj = None

        if USE_CRAMERI and HAS_CRAMERI:
            try:
                cmap_obj = getattr(cm, cmap_name)
            except AttributeError:
                if cmap_name in matplotlib.colormaps:
                    cmap_obj = matplotlib.colormaps[cmap_name]
        
        if cmap_obj is None and cmap_name in matplotlib.colormaps:
            cmap_obj = matplotlib.colormaps[cmap_name]

        auto_colors = [None] * num_runs
        if cmap_obj:
            auto_colors = [cmap_obj(i / (num_runs - 1)) if num_runs > 1 else cmap_obj(0.5) for i in range(num_runs)]

        # --- Data Processing Loop ---
        for idx, (run_label, cfg) in enumerate(RUN_CONFIG.items()):
            try:
                # 1. Path Validation
                run_path = Path(cfg["path"])
                if not run_path.exists():
                    console.print(f"   [bold red][!] FAILED:[/bold red] Path does not exist for [yellow]{run_label}[/yellow]")
                    continue
                
                with console.status(f"[bold green]Processing '{run_label}'...", spinner="dots"):
                    # 2. Load Data and Access Field
                    sdata = StagyyData(run_path)
                    
                    ts_data = sdata.tseries[field_to_plot]
                    
                    # 3. Extract and Scale
                    time_gyr = ts_data.time / SECONDS_IN_GYR 
                    values = ts_data.values

                    # 4. Plotting
                    # Logic: Use automatic Crameri colors if "color" is None or the string "none"
                    if cfg["color"] is None or str(cfg["color"]).lower() == "none":
                        plot_color = auto_colors[idx]
                    else:
                        plot_color = cfg["color"]

                    ax.plot(time_gyr, values, 
                            label=run_label, 
                            linewidth=1.8, 
                            linestyle=cfg["style"], 
                            color=plot_color)

                    # 5. Axis Labeling
                    if not labels_set:
                        meta = ts_data.meta
                        try:
                            description = phyvars.TIME[field_to_plot].description
                        except KeyError:
                            description = meta.description or field_to_plot
                            
                        unit = getattr(meta, 'dim', '')
                        
                        # Clean up unit display: don't show "1" as a unit
                        ylabel = f"{description} [{unit}]" if unit and unit != "1" else description
                        ax.set_ylabel(ylabel, fontsize=14)
                        ax.set_xlabel("Time [Gyr]", fontsize=16)
                        ax.tick_params(axis='both', which='major', labelsize=12)
                        
                        # Logarithmic scale detection
                        log_criteria = ["log", "eta", "slog", "visc", "vrms", "vmax", "vmin", "velocity"]
                        if any(k in field_to_plot.lower() for k in log_criteria):
                            ax.set_yscale('log')
                            ax.yaxis.set_major_formatter(LogFormatterSciNotation())
                        
                        labels_set = True
                
                console.print(f"   [bold green][+][/bold green] [white]{run_label}[/white]: [bold green]DONE![/bold green]")

            except Exception as e:
                console.print(f"   [bold red][!] Error:[/bold red] Could not process [yellow]{run_label}[/yellow]. [dim]Detail: {e}[/dim]")
                continue

        # --- Final Formatting ---
        
        # Apply manual X-limits if defined
        if X_LIMITS:
            ax.set_xlim(X_LIMITS)
            
        # Apply manual Y-limits if defined for this field
        if field_to_plot in FIELD_LIMITS:
            ax.set_ylim(FIELD_LIMITS[field_to_plot])
            console.print(f"   [bold blue][i][/bold blue] Manual Y-limits applied: [yellow]{FIELD_LIMITS[field_to_plot]}[/yellow]")

        ax.legend(loc='best', frameon=True, fontsize=14)
        ax.grid(True, which="both", ls="-", alpha=0.15)
        
        try:
            field_name = phyvars.TIME[field_to_plot].description
        except KeyError:
            field_name = field_to_plot
        ax.set_title(f"{field_name}", fontsize=18)
        
        plt.tight_layout()

        save_name = f"timeseries_Gyr_{field_to_plot}.png"
        fig.savefig(save_name, dpi=300, transparent=TRANSPARENT_PNG)
        
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold green][SUCCESS][/bold green] Plot saved as: [yellow]{save_name}[/yellow]")
        
        if EXPORT_SVG:
            svg_save_name = save_name.replace(".png", ".svg")
            fig.savefig(svg_save_name, transparent=True, dpi=300)
            console.print(f"[bold green][SUCCESS][/bold green] SVG exported as:  [yellow]{svg_save_name}[/yellow]")

        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

        plt.show()

    except Exception as e:
        console.print(f"\n[bold red][CRITICAL ERROR]:[/bold red] {e}")

if __name__ == "__main__":
    main()

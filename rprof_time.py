import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
from stagpy.stagyydata import StagyyData
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import LogFormatterSciNotation
from rich.console import Console

# --- COLOURMAP SYSTEM ---
#  Try to import Fabio Crameri's colormaps
try:
    from cmcrameri import cm
    HAS_CRAMERI = True
except ImportError:
    HAS_CRAMERI = False

console = Console()


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



# --- USER CONFIGURATION ---
# Define the path to your StagYY 'archive' directory.
DATA_ROOT = Path("/run/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/archive_runs/euler/venus_i_01/archive/")

# Fields to visualize ["Tmean", "fmeltmax", "elog"], (Y-axis = Depth, X-axis = Time, Color = Field Value)
FIELDS_TO_PLOT = ["vrms"]   

# Time Range in Myr (e.g., (0, 1000) or None for all)
TIME_RANGE = (0, 400)

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = True  # Set to True for transparent PNG background
FIG_WIDTH = 9      # Figure width in inches, default is 12
FIG_HEIGHT_PER_FIELD = 4  # Height per field in inches, default is 4

# Manual limits for specific fields to ensure consistency across different runs.
FIELD_LIMITS = {
    "Tmax": (500, 4000),
    "Tmean": (500, 4000),
    "vmax": (1e-6, 1.2e-3),
    "vrms": (1e-11, 1e-3), 
    "fmeltmax": (0, 1.0),
    "bsmean": (0, 1.0),
    "elog": (1e-17, 1e-10),
   # "etalog": (1e18, 1e24),
}

# Downsampling: 1 = every step, 10 = every 10th step.
SAMPLE_STEP = 5

# Colormap Preferences
USE_CRAMERI = True
SEQUENTIAL_MAP = "vik"   # Good for T, viscosity, composition
DIVERGING_MAP  = "vik"  # Good for velocity, divergence, flux

def run_visualizer():
    # --- 1. INITIALIZATION ---
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]                STAGPLOT: RPROF-TIME                [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    
    if USE_CRAMERI and not HAS_CRAMERI:
        console.print("[bold yellow][!] WARNING:[/bold yellow] 'cmcrameri' package not found. Using Matplotlib defaults.")
        console.print("    [dim]HINT: To use 'vik' and other scientific colormaps, install it via:[/dim]")
        console.print("    [dim]      pip install cmcrameri[/dim]")

    if not DATA_ROOT.exists():
        console.print(f"[bold red][!] CRITICAL ERROR:[/bold red] The path '[yellow]{DATA_ROOT}[/yellow]' does not exist.")
        console.print("    Please check your 'DATA_ROOT' configuration at the top of the script.")
        return

    console.print(f"[green][+][/green] Loading StagYY Data at: [yellow]{DATA_ROOT.name}[/yellow]")
    
    fields_str = ", ".join([f"[bold magenta]{f}[/bold magenta]" for f in FIELDS_TO_PLOT])
    console.print(f"[green][+][/green] Processing fields: {fields_str}")

    range_info = f"([yellow]{TIME_RANGE[0]}-{TIME_RANGE[1]} Myr[/yellow])" if TIME_RANGE else "([yellow]All Snapshots[/yellow])"
    console.print(f"[green][+][/green] Selected range: {range_info} (Sample Step: [bold white]{SAMPLE_STEP}[/bold white])")

    # Step 1: Initializing data access
    with console.status("[bold green]Initializing StagyyData...", spinner="dots"):
        sdat = StagyyData(DATA_ROOT)
        # Avoid list() here to keep it lazy
        all_snaps_lazy = sdat.snaps[::SAMPLE_STEP]
        
    SEC_PER_MYR = 3600 * 24 * 365.25 * 1e6

    # Step 2: Filtering and Range Detection
    snaps_in_range = []
    with console.status("[bold green]Filtering snapshots by range...", spinner="dots"):
        for snap in all_snaps_lazy:
            try:
                current_time_myr = snap.time / SEC_PER_MYR
                if TIME_RANGE is not None:
                    if TIME_RANGE[0] <= current_time_myr <= TIME_RANGE[1]:
                        snaps_in_range.append(snap)
                else:
                    snaps_in_range.append(snap)
            except:
                continue

    num_to_process = len(snaps_in_range)
    if num_to_process == 0:
        console.print("\n[bold red][!] ERROR:[/bold red] No snapshots found in the specified range.")
        return

    first_step = snaps_in_range[0].istep
    last_step = snaps_in_range[-1].istep

    console.print(f"[green][+][/green] Found [bold cyan]{num_to_process}[/bold cyan] snapshots in the selected range (Steps: [yellow]{first_step}[/yellow] to [yellow]{last_step}[/yellow])")
    
    # Step 3: Data Collection
    times, depths = [], None
    plot_data = {f: [] for f in FIELDS_TO_PLOT}
    field_meta = {f: {"title": "", "log": False} for f in FIELDS_TO_PLOT}
    
    with console.status("[bold green]Starting data collection...", spinner="dots") as status:
        for idx, snap in enumerate(snaps_in_range):
            try:
                current_time_myr = snap.time / SEC_PER_MYR
                status.update(f"[bold green]Processing snapshot {idx+1}/{num_to_process} (Step {snap.istep}, {current_time_myr:.1f} Myr)...")
                
                # Read Fields
                temp_field_data = {}
                for field in FIELDS_TO_PLOT:
                    rprof = snap.rprofs[field] 
                    temp_field_data[field] = rprof.values
                    
                    # Capture metadata once
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

                # All fields for this snap successfully read
                times.append(current_time_myr)
                for field in FIELDS_TO_PLOT:
                    plot_data[field].append(temp_field_data[field])
            
            except Exception as e:
                console.print(f"[bold yellow][!] WARNING:[/bold yellow] Skipping snapshot Step {getattr(snap, 'istep', 'unknown')}")
                console.print(f"    [dim]{e}[/dim]")
                continue

    # --- 4. FINAL VALIDATION ---
    if not times:
        console.print("\n[bold red][!] ERROR:[/bold red] No data was collected.")
        return

    console.print(f"\n[green][+][/green] Data loading complete ([bold green]{len(times)}[/bold green] valid snapshots). Generating plots...")

    # --- 4. PLOTTING ENGINE ---
    fig, axes = plt.subplots(len(FIELDS_TO_PLOT), 1, 
                             figsize=(FIG_WIDTH, FIG_HEIGHT_PER_FIELD * len(FIELDS_TO_PLOT)), 
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
    if TIME_RANGE is not None:
        axes[-1, 0].set_xlim(TIME_RANGE)
        
    plt.tight_layout(rect=[0, 0, 0.95, 1])

    save_name = f"evol_{'_'.join(FIELDS_TO_PLOT)}.png"
    fig.savefig(save_name, dpi=300, bbox_inches='tight', transparent=TRANSPARENT_PNG)
    console.print(f"[bold green][SUCCESS][/bold green] Plot saved as: [yellow]{save_name}[/yellow]")

    if EXPORT_SVG:
        svg_save_name = save_name.replace(".png", ".svg")
        fig.savefig(svg_save_name, bbox_inches='tight', transparent=True, dpi=300)
        console.print(f"[bold green][SUCCESS][/bold green] SVG exported as: [yellow]{svg_save_name}[/yellow]")
    
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
    plt.show()

if __name__ == "__main__":
    try:
        run_visualizer()
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Execution interrupted by user.[/bold red]")
        sys.exit(0)

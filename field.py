import matplotlib
matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from stagpy.stagyydata import StagyyData
from stagpy import field as sp_field
from stagpy import phyvars
from rich.console import Console

console = Console()

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
# NOTE: Update this path to your StagYY archive directory
data_path = Path("/run/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/archive_runs/euler/venus_i_01/archive/")

plot_mode = "time"   # Set to "time" or "snapshot" 
target_time_Myr = 4500   # Used if plot_mode is "time"
target_snapshot = 500  # Used if plot_mode is "snapshot"

field_to_plot = "eta"    

# --- EXPORT SETTINGS ---
EXPORT_SVG = True  # Set to True to also save as .svg
TRANSPARENT_PNG = False  # Set to True for transparent PNG background

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

# --- 0. STARTUP ---
console.print(f"[bold cyan]{'='*60}[/bold cyan]")
console.print(f"[bold cyan]       STAGPLOT: 2D FIELD VISUALIZATION       [/bold cyan]")
console.print(f"[bold cyan]{'='*60}[/bold cyan]")

if not data_path.exists():
    console.print(f"[bold red][!] CRITICAL ERROR:[/bold red] Data path does not exist:\n    [yellow]{data_path}[/yellow]")
    exit(1)

with console.status("[bold green]Initializing StagyyData...", spinner="dots"):
    sdat = StagyyData(data_path)
folder_name = data_path.parent.name 
SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

try:
    field_name_display = phyvars.FIELD.variables[field_to_plot].description
except KeyError:
    field_name_display = field_to_plot

console.print(f"[green][+][/green] Data Path: [yellow]{data_path}[/yellow]")
console.print(f"[green][+][/green] Run:       [bold white]{folder_name}[/bold white]")
console.print(f"[green][+][/green] Mode:      [bold cyan]{plot_mode.upper()}[/bold cyan]")
console.print(f"[green][+][/green] Field:     [bold magenta]{field_name_display}[/bold magenta]")

# --- 1. SELECTION LOGIC ---
snap_number = None
actual_time_Myr = None

with console.status("[bold green]Identifying target snapshot...", spinner="dots"):
    if plot_mode == "time":
        target_time = target_time_Myr * SEC_PER_MYR
        try:
            snap_before = sdat.snaps.at_time(target_time)
            # Check if snap_after is closer
            try:
                snap_after = sdat.snaps[snap_before.isnap + 1]
                if abs(snap_after.time - target_time) < abs(snap_before.time - target_time):
                    snapshot = snap_after
                else:
                    snapshot = snap_before
            except:
                snapshot = snap_before
                
            snap_number = snapshot.isnap
            actual_time_Myr = snapshot.time / SEC_PER_MYR
        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] Failed to find snapshot at time [yellow]{target_time_Myr}[/yellow] Myr: [dim]{e}[/dim]")
            exit(1)
    else:
        try:
            snapshot = sdat.snaps[target_snapshot]
            snap_number = target_snapshot
            actual_time_Myr = snapshot.time / SEC_PER_MYR
        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] Could not access snapshot [yellow]{target_snapshot}[/yellow]: [dim]{e}[/dim]")
            exit(1)

if plot_mode == "time":
    console.print(f"[green][+][/green] Target Time:  [yellow]{target_time_Myr}[/yellow] Myr")
    console.print(f"[green][+][/green] Closest Match: Snap [bold cyan]{snap_number}[/bold cyan] at [bold cyan]{actual_time_Myr:.2f}[/bold cyan] Myr")
else:
    console.print(f"[green][+][/green] Target Snapshot: [bold cyan]{target_snapshot}[/bold cyan]")
    console.print(f"[green][+][/green] Snapshot found at [bold cyan]{actual_time_Myr:.2f}[/bold cyan] Myr")

# --- 2. GENERATE THE PLOT ---
if snap_number is not None:
    try:
        with console.status("[bold green]Loading field data and generating plot...", spinner="dots"):
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
            try:
                unit = phyvars.FIELD.variables[field_to_plot].dim
                label = phyvars.FIELD.variables[field_to_plot].description
            except KeyError:
                unit = "1"
                label = field_to_plot
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
            fig.savefig(save_name, dpi=300, transparent=TRANSPARENT_PNG)
            
            if EXPORT_SVG:
                svg_save_name = save_name.replace(".png", ".svg")
                fig.savefig(svg_save_name, transparent=True, dpi=300)

        console.print(f"[bold green][SUCCESS][/bold green] Plot generated: [yellow]{save_name}[/yellow]")
        if EXPORT_SVG:
            console.print(f"[bold green][SUCCESS][/bold green] SVG exported:  [yellow]{svg_save_name}[/yellow]")

        plt.close(fig)

    except Exception as e:
        console.print(f"[bold red][!] ERROR:[/bold red] An error occurred during plotting: [dim]{e}[/dim]")
        import traceback
        traceback.print_exc()

import matplotlib
matplotlib.use('Agg')
from pathlib import Path
import subprocess
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from stagpy.stagyydata import StagyyData
from stagpy import field as sp_field
from stagpy import phyvars
from rich.console import Console

console = Console()

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
data_path = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/lipwig/v_atm_01/archive")
field_to_plot = "T"  

# Range Selection
range_mode = "time"  # Options: "snapshot" or "time"
snap_min = 0         # Used if range_mode is "snapshot"
snap_max = 50         # Used if range_mode is "snapshot"
time_min_Myr = 110        # Used if range_mode is "time"
time_max_Myr = 140     # Used if range_mode is "time"

# --- EXPORT SETTINGS ---
EXPORT_SVG = False  # Set to True to also save as .svg
TRANSPARENT_PNG = False  # Set to True for transparent PNG background
MAKE_MOVIE = True   # Set to True to generate an MP4 movie using FFmpeg
MOVIE_FPS = 15      # Frames per second for the movie

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

# --- PLOT SETTINGS ---
fig_width = 8
fig_height = 6

# --- 0. STARTUP ---
console.print(f"[bold cyan]{'='*60}[/bold cyan]")
console.print(f"[bold cyan]       STAGPLOT: MULTI-FIELD VISUALIZATION       [/bold cyan]")
console.print(f"[bold cyan]{'='*60}[/bold cyan]")

if not data_path.exists():
    console.print(f"[bold red][!] CRITICAL ERROR:[/bold red] Data path does not exist:\n    [yellow]{data_path}[/yellow]")
    exit(1)

with console.status("[bold green]Initializing StagyyData...", spinner="dots"):
    sdat = StagyyData(data_path)
folder_name = data_path.parent.name 

try:
    field_name_display = phyvars.FIELD[field_to_plot].description
except KeyError:
    field_name_display = field_to_plot

console.print(f"[green][+][/green] Data Path: [yellow]{data_path}[/yellow]")
console.print(f"[green][+][/green] Run:       [bold white]{folder_name}[/bold white]")
console.print(f"[green][+][/green] Field:     [bold magenta]{field_name_display}[/bold magenta]")
console.print(f"[green][+][/green] Mode:      [bold cyan]{mode.upper()}[/bold cyan] ([bold cyan]{range_mode.upper()}[/bold cyan] range)")
if range_mode == "time":
    console.print(f"[green][+][/green] Range:     [yellow]{time_min_Myr}[/yellow] - [yellow]{time_max_Myr}[/yellow] Myr")
else:
    console.print(f"[green][+][/green] Range:     Snap [yellow]{snap_min}[/yellow] - [yellow]{snap_max}[/yellow]")

if mode == "constant_time":
    console.print(f"[green][+][/green] Interval:  [yellow]{dt_Myr}[/yellow] Myr")
else:
    console.print(f"[green][+][/green] Step:      Every [yellow]{snap_step}[/yellow] snapshot(s)")

# Create Directory: [folder_name]_frames_[field_to_plot]_[mode]
output_dir = Path(f"{folder_name}_frames_{field_to_plot}_{mode}")
output_dir.mkdir(parents=True, exist_ok=True)
console.print(f"[green][+][/green] Output:    [yellow]{output_dir}[/yellow]")

SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

# --- 1. PREPARE THE FRAME LIST ---
frames_to_render = [] 

# Resolve time and snapshot bounds based on range_mode
with console.status("[bold green]Resolving range bounds...", spinner="dots"):
    try:
        if range_mode == "time":
            t_start = time_min_Myr * SEC_PER_MYR
            t_end = time_max_Myr * SEC_PER_MYR
            
            def get_closest_isnap(t):
                sb = sdat.snaps.at_time(t)
                try:
                    sa = sdat.snaps[sb.isnap + 1]
                    return sa.isnap if abs(sa.time - t) < abs(sb.time - t) else sb.isnap
                except:
                    return sb.isnap
            
            snap_min = get_closest_isnap(t_start)
            snap_max = get_closest_isnap(t_end)
        else:
            # Range mode is snapshot
            t_start = sdat.snaps[snap_min].time
            t_end = sdat.snaps[snap_max].time
    except Exception as e:
        console.print(f"[bold red][!] ERROR:[/bold red] Failed to resolve range bounds: [dim]{e}[/dim]")
        exit(1)

if mode == "constant_time":
    with console.status(f"[bold green]Identifying snapshots for constant time interval ({dt_Myr} Myr)...", spinner="dots"):
        try:
            # np.arange might exclude the end point; adding a small epsilon ensures inclusion
            target_times = np.arange(t_start, t_end + (dt_Myr * SEC_PER_MYR) / 100, dt_Myr * SEC_PER_MYR)
            
            for t_target in target_times:
                snap_before = sdat.snaps.at_time(t_target)
                try:
                    snap_after = sdat.snaps[snap_before.isnap + 1]
                    snapshot = snap_after if abs(snap_after.time - t_target) < abs(snap_before.time - t_target) else snap_before
                except:
                    snapshot = snap_before
                
                # For constant_time, we still respect the resolved snap_min/max boundaries
                if snap_min <= snapshot.isnap <= snap_max:
                    if not frames_to_render or frames_to_render[-1][0] != snapshot.isnap:
                        frames_to_render.append((snapshot.isnap, snapshot.time))
        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] Failed to prepare frame list: [dim]{e}[/dim]")
            exit(1)
else:
    # constant_frame mode
    with console.status(f"[bold green]Scanning snapshots {snap_min} to {snap_max} (step {snap_step})...", spinner="dots"):
        for n in range(snap_min, snap_max + 1, snap_step):
            try:
                snap = sdat.snaps[n]
                frames_to_render.append((snap.isnap, snap.time))
            except:
                continue

if len(frames_to_render) == 0:
    console.print("[bold red][!] ERROR:[/bold red] No data found for the given range/settings.")
    exit(1)

console.print(f"[green][+][/green] Prepared [bold cyan]{len(frames_to_render)}[/bold cyan] frames for rendering.")

# --- 2. RENDER THE FRAMES ---
console.print(f"[green][+][/green] Starting rendering loop...")
num_frames = len(frames_to_render)

with console.status("[bold green]Rendering frames...", spinner="dots") as status:
    for i, (snap_number, t_val) in enumerate(frames_to_render):
        try:
            status.update(f"[bold green]Rendering frame {i+1}/{num_frames} (Snap {snap_number})...")
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
            try:
                display_name = phyvars.FIELD[field_to_plot].description
            except KeyError:
                display_name = field_to_plot
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
            
            if (i + 1) % 10 == 0 or i == num_frames - 1:
                console.print(f"   [bold green][+][/bold green] Saved: [white]{file_name}[/white] ({i+1}/{num_frames})")
                
        except Exception as e:
            console.print(f"   [bold red][!] Error at Snap {snap_number}:[/bold red] [dim]{e}[/dim]")
            plt.close()

console.print(f"[bold green][SUCCESS][/bold green] Rendering complete. Frames saved to: [yellow]{output_dir}[/yellow]")

# --- 3. MAKE MOVIE ---
if MAKE_MOVIE:
    movie_name = f"{folder_name}_{field_to_plot}_{mode}.mp4"
    console.print(f"\n[bold cyan]Creating movie:[/bold cyan] [yellow]{movie_name}[/yellow]")
    console.print(f"[green][+][/green] Target FPS: [bold cyan]{MOVIE_FPS}[/bold cyan]")
    
    # Get the start number for FFmpeg
    start_number = frames_to_render[0][0]
    
    # --- Robustness Check: Verify frames exist before calling FFmpeg ---
    with console.status("[bold green]Verifying frame files...", spinner="dots"):
        missing_frames = []
        for snap_num, _ in frames_to_render:
            frame_path = output_dir / f"frame_{snap_num:05d}.png"
            if not frame_path.exists():
                missing_frames.append(snap_num)
    
    if missing_frames:
        console.print(f"[bold red][!] ERROR:[/bold red] Found [bold yellow]{len(missing_frames)}[/bold yellow] missing frames.")
        console.print(f"    [dim]Missing snaps: {missing_frames[:5]}...[/dim]")
        console.print("    [red]Skipping movie creation as the frame sequence is incomplete.[/red]")
    else:
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(MOVIE_FPS),
            "-start_number", str(start_number),
            "-i", str(output_dir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            movie_name
        ]
        
        try:
            with console.status("[bold green]Running FFmpeg...", spinner="dots"):
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"[bold green][SUCCESS][/bold green] Movie created: [yellow]{movie_name}[/yellow]")
            else:
                console.print(f"[bold red][!] ERROR:[/bold red] FFmpeg failed with return code {result.returncode}")
                # Provide snippet of FFmpeg error for debugging
                error_log = result.stderr.split('\n')[-10:] # Last 10 lines
                console.print("[dim]FFmpeg Tail Output:[/dim]")
                for line in error_log:
                    if line.strip(): console.print(f"    [dim]{line.strip()}[/dim]")
                    
        except FileNotFoundError:
            console.print("[bold red][!] ERROR:[/bold red] 'ffmpeg' command not found. Please install FFmpeg to use MAKE_MOVIE.")
        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] An unexpected error occurred during movie creation: [dim]{e}[/dim]")

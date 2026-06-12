import numpy as np
from pathlib import Path
from stagpy.stagyydata import StagyyData
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

"""
info.py: A simplified utility to inspect StagYY simulation snapshot and time ranges.
Optimized for speed by only reading the first and last available snapshots.
"""

# --- CONFIGURATION ---
DATA_DIRECTORY = "/home/aritro/Documents/Academia/#PhD/StagYY/archive_runs/hdf/archive/hdf/" # Put your directory path here

SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

console = Console()

def get_time(snap):
    """Retrieves physical time from a snapshot."""
    try:
        # Prefer direct time attribute
        return snap.time
    except:
        try:
            # Fallback to timeinfo series
            return snap.timeinfo["time"]
        except:
            return 0.0

def format_time(t_seconds):
    """Formats time into Myr or Gyr for readability."""
    if t_seconds >= SEC_PER_GYR:
        return f"{t_seconds / SEC_PER_GYR:.3f} Gyr"
    # Always use Myr for values below 1 Gyr, including zero
    return f"{t_seconds / SEC_PER_MYR:.1f} Myr"

def main():
    # 1. Determine Data Path
    data_path = Path(DATA_DIRECTORY)

    # --- 0. STARTUP HEADER ---
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]             STAGPLOT: SIMULATION INFO               [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    if not data_path.exists():
        console.print(f"[bold red][!] ERROR:[/bold red] Path does not exist: [yellow]{data_path}[/yellow]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        return

    # 2. Initialize StagyyData
    try:
        with console.status("[bold green]fetching simulation info...", spinner="dots"):
            # Check for 'archive' subdirectory commonly used in StagYY runs
            if (data_path / "archive").is_dir() and not any(data_path.glob("par*")):
                sdat = StagyyData(data_path / "archive")
            else:
                sdat = StagyyData(data_path)
            
            run_name = sdat.path.parent.name if sdat.path.name == 'archive' else sdat.path.name
            
            # 3. Optimized Snapshot Analysis
            first_snap = None
            last_snap = None

            # Find first available snapshot using the iterator (stops at first match)
            try:
                first_snap = next(iter(sdat.snaps))
            except (StopIteration, Exception):
                pass

            # Find last available snapshot by searching backwards from the end
            if first_snap:
                num_potential = len(sdat.snaps)
                for i in range(num_potential - 1, -1, -1):
                    try:
                        last_snap = sdat.snaps[i]
                        break
                    except:
                        continue

            # Build the table while still under the spinner context (but don't print yet)
            table = Table(box=None, show_header=False, pad_edge=False)
            table.add_column("Icon", style="green", width=4)
            table.add_column("Property", style="bold magenta", width=12)
            table.add_column("Value", style="white")
            
            table.add_row("[+]", "Run:", f"[white]{run_name}[/]")
            table.add_row("[+]", "Path:", f"[dim]{sdat.path}[/]")

            if first_snap and last_snap:
                t_start = get_time(first_snap)
                t_end = get_time(last_snap)
                
                table.add_row("[+]", "Snapshots:", f"{first_snap.isnap} to {last_snap.isnap}")
                table.add_row("[+]", "Time:", f"{format_time(t_start)} to {format_time(t_end)}")
                table.add_row("", "", f"[dim]({(t_end - t_start)/SEC_PER_MYR:.2f} Myr elapsed)[/]")
                
                # Grid dimensions
                try:
                    g = first_snap.geom
                    grid_str = f"{g.nxtot} x {g.nytot} x {g.nztot}"
                    
                    details = []
                    if g.yinyang:
                        details.append("Yin-Yang")
                    elif g.nbtot > 1:
                        details.append(f"{g.nbtot} blocks")
                    
                    if details:
                        grid_str += f" [dim]({', '.join(details)})[/dim]"
                        
                    table.add_row("[+]", "Grid:", f"[cyan]{grid_str}[/cyan] [dim](nx, ny, nz)[/dim]")
                except:
                    pass
            else:
                table.add_row("[!]", "Snapshots:", "[bold red]None found.[/bold red]")

        # --- DISPLAY RESULTS (After spinner finishes) ---
        console.print(f"[bold green][SUCCESS][/bold green] Simulation info retrieved.")
        console.print(table)
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    except Exception as e:
        console.print(f"\n[bold red][CRITICAL ERROR]:[/bold red]")
        console.print(e)
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

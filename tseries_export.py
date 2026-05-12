import numpy as np
from pathlib import Path
from stagpy.stagyydata import StagyyData
import sys
from rich.console import Console
from rich.progress import track

"""
tseries_export.py: Extracts any time-series data from StagYY output 
and saves it to a structured text file with two columns: Time (Years) and Parameter.
"""

# --- CONFIGURATION ---
# Update this path to your StagYY archive directory
DATA_PATH = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/lipwig/v_atm_01/archive/")

# Parameter to extract (e.g., "outgassed_water", "Tmean", "vrms")
FIELD_TO_EXPORT = "outgassed_water"

SECONDS_IN_YEAR = 3.15576e7

def main():
    console = Console()
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]       STAGPLOT: TSERIES EXPORT       [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    
    # 1. Configuration priority (CLI > Script Variable)
    data_path = DATA_PATH
    field_to_export = FIELD_TO_EXPORT

    if len(sys.argv) > 1:
        # Check if first arg is a path or a field
        arg1 = sys.argv[1]
        if Path(arg1).exists() or "/" in arg1:
            data_path = Path(arg1)
            if len(sys.argv) > 2:
                field_to_export = sys.argv[2]
        else:
            field_to_export = arg1
            if len(sys.argv) > 2:
                data_path = Path(sys.argv[2])

    if not data_path.exists():
        console.print(f"[bold red][!] ERROR:[/bold red] Data path does not exist: {data_path}")
        return

    # 2. Set output filename based on field
    output_filename = f"tseries_{field_to_export}.txt"

    console.print(f"[green][+][/green] Reading from: [yellow]{data_path}[/yellow]")
    console.print(f"[green][+][/green] Exporting field: [bold magenta]{field_to_export}[/bold magenta]")

    # 3. Initialize StagyyData
    try:
        with console.status("[bold green]Initializing StagyyData..."):
            sdata = StagyyData(data_path)
        
        # 4. Extract Time Series
        try:
            with console.status(f"[bold green]Extracting {field_to_export}..."):
                ts = sdata.tseries[field_to_export]
                time_years = ts.time / SECONDS_IN_YEAR
                values = ts.values
        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] Could not extract field '{field_to_export}': {e}")
            return

        if time_years is None or len(time_years) == 0:
            console.print("[bold red][!] ERROR:[/bold red] No time series data found.")
            return

        # 5. Write to Text File with Progress Bar
        num_rows = len(time_years)
        console.print(f"[green][+][/green] Writing data to: [yellow]{output_filename}[/yellow]")
        
        with open(output_filename, "w") as f:
            # Header
            header = f"Time_Years\t{field_to_export}"
            f.write(header + "\n")
            
            # Data rows with progress bar
            for i in track(range(num_rows), description=f"Exporting rows...", console=console):
                f.write(f"{time_years[i]:.6e}\t{values[i]:.6e}\n")

        console.print(f"[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold green][SUCCESS][/bold green] Export complete. {num_rows} rows saved.")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    except Exception as e:
        console.print(f"[bold red][!] CRITICAL ERROR:[/bold red] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

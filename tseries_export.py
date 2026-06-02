import numpy as np
from pathlib import Path
from stagpy.stagyydata import StagyyData
import sys
from rich.console import Console
from rich.progress import track

"""
tseries_export.py: Extracts multiple time-series fields from StagYY output 
and saves them to a structured text file.
Columns: Snapshot (istep), Time (Years), Field1, Field2, ...
"""

# --- CONFIGURATION ---
# Update this path to your StagYY archive directory
DATA_PATH = Path("/run/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/archive_runs/lipwig/hdf/archive/")

# List of parameters to extract, separated by commas (e.g., "Tmean, Vrms, erupt_rate")
FIELDS_TO_EXPORT = "Tmean, Vrms, eta_amean, outgassed_nitrogen"

SECONDS_IN_YEAR = 3.15576e7

def force_hdf5_if_needed(sdata):
    """
    Forces StagyyData to recognize HDF5 mode if TimeSeries.h5 exists
    but Data.xmf (StagPy's default anchor) is missing.
    """
    if sdata.hdf5 is None:
        possible_h5_folders = ["+hdf5", "../+hdf5"]
        for folder in possible_h5_folders:
            h5_path = (sdata.path / folder).resolve()
            if (h5_path / "TimeSeries.h5").is_file():
                object.__setattr__(sdata, "hdf5", h5_path)
                return True
    return sdata.hdf5 is not None

def main():
    console = Console()
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]       STAGPLOT: MULTI-TSERIES EXPORT       [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    
    # 1. Configuration priority (CLI > Script Variable)
    data_path = DATA_PATH
    fields_str = FIELDS_TO_EXPORT

    if len(sys.argv) > 1:
        # Check if first arg is a path or a field list
        arg1 = sys.argv[1]
        if Path(arg1).exists() or "/" in arg1:
            data_path = Path(arg1)
            if len(sys.argv) > 2:
                fields_str = sys.argv[2]
        else:
            fields_str = arg1
            if len(sys.argv) > 2:
                data_path = Path(sys.argv[2])

    # Parse fields into a list
    fields_to_export = [f.strip() for f in fields_str.split(",")]

    if not data_path.exists():
        console.print(f"[bold red][!] ERROR:[/bold red] Data path does not exist: {data_path}")
        return

    # 2. Set output filename
    output_filename = "tseries_multi_export.txt"

    console.print(f"[green][+][/green] Reading from: [yellow]{data_path}[/yellow]")
    console.print(f"[green][+][/green] Exporting fields: [bold magenta]{', '.join(fields_to_export)}[/bold magenta]")

    # 3. Initialize StagyyData
    try:
        with console.status("[bold green]Initializing StagyyData..."):
            sdata = StagyyData(data_path)
            force_hdf5_if_needed(sdata)
        
        # 4. Access the underlying Tseries DataFrame
        try:
            with console.status(f"[bold green]Accessing tseries data..."):
                # Accessing the private _tseries DataFrame for direct multi-column handling
                df = sdata.tseries._tseries 
                
                # Check if required columns exist
                available_cols = df.columns.tolist()
                
                # We always need 'time'
                if 'time' not in available_cols:
                    console.print("[bold red][!] ERROR:[/bold red] 'time' column not found in data.")
                    return
                
                # Filter to only requested fields that actually exist
                valid_fields = []
                for f in fields_to_export:
                    if f in available_cols:
                        valid_fields.append(f)
                    else:
                        console.print(f"[bold yellow][!] WARNING:[/bold yellow] Field '{f}' not found in data. Skipping.")
                
                if not valid_fields:
                    console.print("[bold red][!] ERROR:[/bold red] No valid fields found to export.")
                    return

                # Prepare the final array for export
                # Index is istep, first column is time, rest are fields
                isteps = df.index.to_numpy()
                times = (df['time'] / SECONDS_IN_YEAR).to_numpy()
                field_data = {f: df[f].to_numpy() for f in valid_fields}

        except Exception as e:
            console.print(f"[bold red][!] ERROR:[/bold red] Could not process time series: {e}")
            return

        # 5. Write to Text File with Progress Bar
        num_rows = len(isteps)
        console.print(f"[green][+][/green] Writing data to: [yellow]{output_filename}[/yellow]")
        
        with open(output_filename, "w") as f:
            # Header: Snapshot  Time_Years  Field1  Field2 ...
            header = "Snapshot\tTime_Years\t" + "\t".join(valid_fields)
            f.write(header + "\n")
            
            # Data rows with progress bar
            for i in track(range(num_rows), description=f"Exporting rows...", console=console):
                row_vals = [f"{isteps[i]}", f"{times[i]:.6e}"]
                for field in valid_fields:
                    row_vals.append(f"{field_data[field][i]:.6e}")
                f.write("\t".join(row_vals) + "\n")

        console.print(f"[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold green][SUCCESS][/bold green] Export complete. {num_rows} rows saved.")
        console.print(f"            Output file: [yellow]{output_filename}[/yellow]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    except Exception as e:
        console.print(f"[bold red][!] CRITICAL ERROR:[/bold red] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

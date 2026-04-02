import numpy as np
from pathlib import Path
from stagpy.stagyydata import StagyyData
import sys

"""
info.py: A simplified utility to inspect StagYY simulation snapshot and time ranges.
Optimized for speed by only reading the first and last available snapshots.
"""

# --- CONFIGURATION ---
SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

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
    # Priority: CLI argument > Current Directory > Hardcoded Fallback
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        data_path = Path(sys.argv[1])
    else:
        data_path = Path.cwd()

    # If CWD doesn't look like a StagYY run, try the user's known path
    if not (data_path / "par").exists() and not (data_path / "archive" / "par").exists():
        fallback_path = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_i_01/archive/")
        if fallback_path.exists():
            data_path = fallback_path

    if not data_path.exists():
        print(f"[!] ERROR: Path does not exist: {data_path}")
        return

    # 2. Initialize StagyyData
    try:
        # Check for 'archive' subdirectory commonly used in StagYY runs
        if (data_path / "archive").is_dir() and not any(data_path.glob("par*")):
            sdat = StagyyData(data_path / "archive")
        else:
            sdat = StagyyData(data_path)
            
        print(f"\n{' STAGYY SIMULATION INFO ':=^80}")
        run_name = sdat.path.parent.name if sdat.path.name == 'archive' else sdat.path.name
        print(f"[+] Run:  {run_name}")
        print(f"[+] Path: {sdat.path}")

        # 3. Optimized Snapshot Analysis
        # Finding first and last available snapshots without full iteration
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

        if first_snap and last_snap:
            t_start = get_time(first_snap)
            t_end = get_time(last_snap)
            
            # Note: We don't count every snapshot to keep it fast
            print(f"[+] Snapshots: indices {first_snap.isnap} to {last_snap.isnap}")
            print(f"[+] Time:      {format_time(t_start)} to {format_time(t_end)}")
            print(f"               ({(t_end - t_start)/SEC_PER_MYR:.2f} Myr elapsed)")
        else:
            print("[!] Snapshots: None found.")

    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()

    print("="*80 + "\n")

if __name__ == "__main__":
    main()

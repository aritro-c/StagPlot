import numpy as np
from pathlib import Path
from stagpy.stagyydata import StagyyData
from stagpy import phyvars
import pandas as pd
import sys

"""
info.py: A utility script to quickly inspect StagYY simulation metadata.
Categorizes fields and profiles according to StagPlot conventions.
Optimized for speed and robustness.
"""

# --- USER INPUT ---
data_path = Path("/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_02/archive/")

# --- CONFIGURATION ---
SEC_PER_MYR = 1e6 * 365.25 * 24 * 3600
SEC_PER_GYR = 1e3 * SEC_PER_MYR

def print_header(text):
    print(f"\n{text:─^110}")

def format_grid(available_items, category_items, indent=2):
    """Prints categorized items in a grid, showing only what is available."""
    # Build a lookup set for efficiency, including aliases
    lookup = set(available_items)
    for item in available_items:
        # If available_item has an inverse alias, add it
        for alias, real in phyvars.TIME_ALIAS.items():
            if real == item:
                lookup.add(alias)

    to_show = []
    for item in category_items:
        if item in lookup:
            to_show.append(item)
        elif item in phyvars.FIELD_EXTRA or item in phyvars.RPROF_EXTRA or item in phyvars.TIME_EXTRA:
            to_show.append(item)
        else:
            # Check if category_item is an alias for something available
            alias = phyvars.TIME_ALIAS.get(item)
            if alias and alias in lookup:
                to_show.append(item)

    if not to_show:
        print(" " * indent + "None found.")
        return

    to_show = sorted(list(set(to_show)))
    max_len = 20  # Fixed width for neat columns
    cols = 110 // max_len
    if cols <= 0: cols = 1
    
    for i in range(0, len(to_show), cols):
        row = to_show[i:i+cols]
        print(" " * indent + "".join(str(item).ljust(max_len) for item in row))

# Categories provided by user
CAT_FIELDS = ["T", "v1", "v2", "v3", "p", "eta", "rho", "rho4rhs", "trarho", "sII", "sx1", "sx2", "sx3", "s1val", "edot", "Tcond", "c", "cFe", "hpe", "wtr", "age", "contID", "rs1", "rs2", "rs3", "rsc", "basalt", "harzburgite", "impactor", "prim", "meltfrac", "meltcompo", "meltrate", "meltvel", "nmelt", "fSiO2", "fMgO", "fFeO", "fXO", "fFeR", "stream"]
CAT_SFIELDS = ["topo_top", "geoid_bot", "ftop", "fsbot", "topo_bot", "topo_g_top", "fbot", "crust", "geoid_top", "topo_g_bot", "fstop"]
CAT_RPROFS = ["r", "Tmean", "Tmin", "Tmax", "vrms", "vmin", "vmax", "vzabs", "vzmin", "vzmax", "vhrms", "vhmin", "vhmax", "etalog", "etamin", "etamax", "elog", "emin", "emax", "slog", "smin", "smax", "whrms", "whmin", "whmax", "wzrms", "wzmin", "wzmax", "drms", "dmin", "dmax", "enadv", "endiff", "enradh", "enviscdiss", "enadiabh", "cmean", "cmin", "cmax", "rhomean", "rhomin", "rhomax", "airmean", "airmin", "airmax", "primmean", "primmin", "primmax", "ccmean", "ccmin", "ccmax", "fmeltmean", "fmeltmin", "fmeltmax", "metalmean", "metalmin", "metalmax", "gsmean", "gsmin", "gsmax", "viscdisslog", "viscdissmin", "viscdissmax", "advtot", "advdesc", "advasc", "dr", "diff", "diffs", "advts", "advds", "advas", "energy"]
CAT_TIME = ["t", "ftop", "fbot", "Tmin", "Tmean", "Tmax", "vmin", "vrms", "vmax", "etamin", "etamean", "etamax", "Raeff", "Nutop", "Nubot", "Cmin", "Cmean", "Cmax", "moltenf_mean", "moltenf_max", "erupt_rate", "erupt_tot", "erupt_heat", "entrainment", "Cmass_error", "H_int", "r_ic", "topT_val", "botT_val", "dt", "dTdt", "ebalance", "mobility"]
CAT_REF = ["z", "T", "rho", "expan", "Cp", "Tcond", "P", "grav"]

def main():
    debug = "--debug" in sys.argv

    if not data_path.exists():
        print(f"[!] ERROR: Data path does not exist: {data_path}")
        return

    print(f"\n{' STAGYY SIMULATION INFO ':=^110}")
    
    try:
        sdat = StagyyData(data_path)
        folder_name = data_path.parent.name
        
        print(f"[+] Run Name:  {folder_name}")
        print(f"[+] Path:      {data_path}")
        
        num_snaps = len(sdat.snaps)
        if num_snaps > 0:
            first_snap = sdat.snaps[0]
            last_snap = sdat.snaps[num_snaps - 1]
            
            def get_t(snap):
                try:
                    return snap.time
                except:
                    try: return snap.timeinfo["time"]
                    except: return 0.0

            t_start = get_t(first_snap)
            t_end = get_t(last_snap)
            
            print(f"[+] Snapshots: {num_snaps} (from {first_snap.isnap} to {last_snap.isnap})")
            print(f"[+] Time Span: {t_start/SEC_PER_GYR:.4f} Gyr to {t_end/SEC_PER_GYR:.4f} Gyr")
            print(f"               ({(t_end - t_start)/SEC_PER_MYR:.2f} Myr elapsed)")
        else:
            print("[!] Snapshots: None found.")
            last_snap = None

        # GEOMETRY
        step = sdat.steps[0] if len(sdat.steps) > 0 else (sdat.snaps[0] if num_snaps > 0 else None)
        if step:
            print_header(" geometry & resolution ")
            geom = step.geom
            shape = sdat.par.nml.get('geometry', {}).get('shape', 'Unknown')
            print(f"  Shape:         {shape}")
            print(f"  Grid (Z,X,Y):  {geom.nztot} x {geom.nxtot} x {geom.nytot}")
            print(f"  Z-Range:       {geom.z_walls[0]/1e3:.1f} to {geom.z_walls[-1]/1e3:.1f} km")
            if not geom.cartesian:
                print(f"  R-Inner:       {geom.r_walls[0]/1e3:.1f} km")
                print(f"  R-Outer:       {geom.r_walls[-1]/1e3:.1f} km")

        # FIELDS
        if last_snap:
            print_header(" fields ")
            format_grid(last_snap.fields._all_vars, CAT_FIELDS)
            
            print_header(" surface fields ")
            try:
                format_grid(last_snap.sfields._all_vars, CAT_SFIELDS)
            except Exception as e:
                if debug: print(f"  Error: {e}")
                print("  None found.")

            print_header(" radial profiles ")
            try:
                available_rprofs = set(last_snap.rprofs._rprofs.columns) | set(phyvars.RPROF_EXTRA.keys())
                format_grid(available_rprofs, CAT_RPROFS)
            except Exception as e:
                if debug: print(f"  Error: {e}")
                print("  None found.")

        # TIME SERIES
        print_header(" time series ")
        try:
            # Explicitly trigger data loading
            df_time = sdat.tseries._tseries
            if df_time is not None and not df_time.empty:
                available_time = set(df_time.columns) | set(phyvars.TIME_EXTRA.keys())
                format_grid(available_time, CAT_TIME)
            else:
                print("  Time series data is empty.")
        except Exception as e:
            if debug:
                import traceback
                traceback.print_exc()
            time_h5 = sdat.filename("TimeSeries.h5")
            time_dat = sdat.filename("time.dat")
            print(f"  None found. (Check: {time_h5.name} exists? {time_h5.exists()}, {time_dat.name} exists? {time_dat.exists()})")

        # REFSTATE
        print_header(" refstate ")
        try:
            # refstate.adiabats is a list of DataFrames
            adiabats = sdat.refstate.adiabats
            if adiabats:
                available_ref = set(adiabats[-1].columns)
                format_grid(available_ref, CAT_REF)
            else:
                print("  Refstate adiabats are empty.")
        except Exception as e:
            if debug:
                import traceback
                traceback.print_exc()
            ref_dat = sdat.filename("refstat.dat")
            print(f"  None found. (Check: {ref_dat.name} exists? {ref_dat.exists()})")
        
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        if debug:
            import traceback
            traceback.print_exc()

    print("\n" + "="*110)

if __name__ == "__main__":
    main()

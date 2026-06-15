import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from stagpy.stagyydata import StagyyData
import stagpy.error

# Try to import Crameri colormaps for better perceptual scaling
try:
    from cmcrameri import cm
    HAS_CRAMERI = True
except ImportError:
    HAS_CRAMERI = False

# =============================================================================
# CONFIGURATION
# =============================================================================
# Path to the directory containing StagYY archive files
directory = Path('/home/aritro/Documents/Academia/#PhD/StagYY/archive_runs/hdf/archive/hdf/')
file_name = 'noGI'

start_frame = 471
end_frame = 501
step = 1

# Toggle which fields to process and plot
include_topography = False
include_age        = True
include_strainrate = True
include_velocity   = True
include_crustthick = True

save_svg = False
save_png = True
transparent_png = False

# Field limits (set to None for automatic scaling)
topo_lim    = [-10, 10]
age_lim     = [0, 600]
edot_lim    = [-18, -14] # log10 units
vel_lim     = None
crthick_lim = [0, 80]

# Dimensional scales
Dscale = 0.001                      # depth scale: m to km
tscale = 1/(3600*24*365.24*1e6)     # age scale: s to Myr
vscale = 100*3600*24*365.24         # velocity scale: m/s to cm/year

# --- COLOURMAP PREFERENCES ---
USE_CRAMERI = True  # Set to False to use standard Matplotlib colormaps
# Define preferred Crameri maps (see https://www.fabiocrameri.ch/colourmaps/)
CM_TOPO      = "oleron"
CM_AGE       = "roma"
CM_STRAIN    = "oslo"
CM_VELOCITY  = "lapaz"
CM_CRUST     = "batlow"

# Fallback Matplotlib maps (used if USE_CRAMERI is False or if cmcrameri is not installed)
MP_TOPO      = "coolwarm"
MP_AGE       = "viridis"
MP_STRAIN    = "magma"
MP_VELOCITY  = "plasma"
MP_CRUST     = "inferno"

# =============================================================================
# HELPERS
# =============================================================================

def get_cmap(crameri_name, mpl_name):
    """Helper to select colormap based on user preference and availability."""
    if USE_CRAMERI and HAS_CRAMERI:
        try:
            return getattr(cm, crameri_name)
        except AttributeError:
            print(f"[!] WARNING: Crameri map '{crameri_name}' not found. Using '{mpl_name}'.")
            return mpl_name
    return mpl_name


# =============================================================================
# MAIN PROCESSING LOOP
# =============================================================================

def main():
    print(f"{'='*60}\n       STAGPLOT: SURFACE EVOLUTION (2D)       \n{'='*60}")
    
    if not HAS_CRAMERI:
        print("[!] WARNING: 'cmcrameri' package not found. Using Matplotlib defaults.")
        print("          pip install cmcrameri")
    
    sdat = StagyyData(directory)
    frames = np.arange(start_frame, end_frame + 1, step)
    
    # We will keep only frames that actually exist in the simulation
    available_snaps = {step.isnap for step in sdat.snaps}
    valid_frames = [int(f) for f in frames if int(f) in available_snaps]
    if not valid_frames:
        print(f"[!] ERROR: No snapshots found in the given range. Exiting.")
        return
        
    n_frames = len(valid_frames)
    
    # Determine grid size from first available frame
    try:
        first_snap = sdat.snaps[valid_frames[0]]
        
        # Access the geometry (grid coordinates)
        geom = first_snap.geom
        theta = geom.t_centers
        phi = geom.p_centers
        
        # For 2D annulus, we expect one of theta/phi to be the angular coordinate
        if len(theta) > 1 and len(phi) == 1:
            n_angle = len(theta)
            angle_axis = np.degrees(theta) if theta.max() < 2*np.pi else theta
        else:
            n_angle = len(phi)
            angle_axis = np.degrees(phi) if phi.max() < 2*np.pi else phi
            
        print(f"[INFO] Grid size: {n_angle} angular points, {n_frames} temporal points.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] ERROR determining grid size: {e}")
        return

    times = np.zeros(n_frames)
    
    # Field configuration with colormaps
    # (stagpy_field, include, limits, label, tag, colormap)
    field_configs = [
        ('topo_top', include_topography, topo_lim, 'Surface Topography [km]', 'topo', 
         get_cmap(CM_TOPO, MP_TOPO)),
        ('age', include_age, age_lim, 'Surface Age [Myr]', 'age', 
         get_cmap(CM_AGE, MP_AGE)),
        ('edot', include_strainrate, edot_lim, 'Surface Strain Rate [log10 1/s]', 'strainrate', 
         get_cmap(CM_STRAIN, MP_STRAIN)),
        ('velocity', include_velocity, vel_lim, 'Surface Velocity [cm/yr]', 'velocity', 
         get_cmap(CM_VELOCITY, MP_VELOCITY)),
        ('crust', include_crustthick, crthick_lim, 'Crustal Thickness [km]', 'crustthick', 
         get_cmap(CM_CRUST, MP_CRUST))
    ]
    
    data_storage = {tag: np.zeros((n_angle, n_frames)) for _, inc, _, _, tag, _ in field_configs if inc}
    
    print(f"\n[INFO] Starting data processing...")
    for i, frame in enumerate(valid_frames):
        if (i+1) % 10 == 0 or i == 0:
            print(f"       Processing frame {frame:05d} ({i+1} of {n_frames})...")
        
        snap = sdat.snaps[frame]
        got_time = False
        
        for field_type, include, lim, title, tag, cmap in field_configs:
            if not include:
                continue
            
            try:
                if field_type == 'velocity':
                    # Extract velocity components and calculate magnitude at the surface (last z index)
                    if 'v1' in snap.fields and 'v2' in snap.fields:
                        vx = snap.fields['v1'].values[:, :, -1, :]
                        vy = snap.fields['v2'].values[:, :, -1, :]
                        vh = vscale * np.sqrt(vx**2 + vy**2)
                        
                        # Velocity grids might have ghost nodes (e.g., shape (2, 513) instead of (1, 512))
                        # We need to slice it down to the actual grid size
                        surf_data = vh[:1, :n_angle] 
                    else:
                        continue
                else:
                    if field_type == 'crust' or field_type == 'topo_top':
                        if field_type not in snap.sfields:
                            continue
                        data = snap.sfields[field_type].values
                        # Surface fields are already 2D
                        surf_data = data * Dscale
                    else:
                        if field_type not in snap.fields:
                            continue
                        data = snap.fields[field_type].values
                        # For 3D fields like age or edot, extract the surface layer (last z index)
                        # stagpy field shape is usually (x, y, z, block)
                        nz = data.shape[2]
                        surf_data = data[:, :, nz-1, :]
                        if field_type == 'age':
                            surf_data *= tscale

                val = surf_data.squeeze()
                
                if field_type == 'edot':
                    # Log-scale handling
                    val = np.log10(np.where(val > 0, val, 1e-25))
                
                data_storage[tag][:, i] = val
                
                if not got_time:
                    try:
                        times[i] = snap.timeinfo["time"] * tscale
                    except Exception:
                        times[i] = snap.time * tscale
                    got_time = True
                    
            except Exception as e:
                print(f"       [!] Error processing {field_type} in frame {frame}: {type(e).__name__} - {e}")

    # =========================================================================
    # PLOTTING
    # =========================================================================
    if not any(include for _, include, _, _, _, _ in field_configs):
        print("[!] No fields selected for plotting. Exiting.")
        return

    print(f"\n[INFO] Generating plots...")
    fig_width = 18
    fig_height = 6
    
    for field_type, include, lim, title, tag, cmap in field_configs:
        if not include:
            continue
            
        plt.figure(figsize=(fig_width, fig_height))
        
        plot_data = data_storage[tag]
            
        im = plt.imshow(plot_data, aspect='auto', origin='lower',
                        extent=[times.min(), times.max(), angle_axis.min(), angle_axis.max()],
                        cmap=cmap)
        
        cb = plt.colorbar(im)
        cb.set_label(title.split('[')[-1].replace(']', '') if '[' in title else '', fontsize=18)
        cb.ax.tick_params(labelsize=14)
        
        if lim:
            plt.clim(lim)
            
        plt.title(title, fontsize=24, fontweight='bold', pad=15)
        plt.xlabel('Time [Myr]', fontsize=20, fontweight='bold')
        plt.ylabel('Angle [deg]', fontsize=20, fontweight='bold')
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        
        plt.tight_layout()
        
        # Save results
        base_name = f"{file_name}_{tag}"
        
        if save_svg:
            save_name_svg = f"{base_name}.svg"
            try:
                plt.savefig(save_name_svg, transparent=True, dpi=300)
                print(f"       Saved: {save_name_svg}")
            except Exception as e:
                print(f"       [!] Error saving SVG: {e}")

        if save_png:
            save_name_png = f"{base_name}.png"
            try:
                plt.savefig(save_name_png, transparent=transparent_png, facecolor='white', dpi=300)
                print(f"       Saved: {save_name_png}")
            except Exception as e:
                print(f"       [!] Error saving PNG: {e}")

        plt.close()
    
    print(f"\n[SUCCESS] Surface evolution processing complete.\n{'='*60}")

if __name__ == "__main__":
    main()

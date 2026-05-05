import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

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
directory = Path('/media/aritro/f522493b-003a-404d-a839-3e0925c674b6/Aritro/StagYY/runs/euler/venus_i_01/archive/+op/')
file_name = 'noGI'

start_frame = 0
end_frame = 17000
step = 20

# Toggle which fields to process and plot
include_topography = False
include_age        = False
include_strainrate = True
include_velocity   = False
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
# StagYY READER CLASS
# =============================================================================

class StagYYReader:
    def __init__(self, directory, file_name):
        self.directory = Path(directory)
        self.file_name = file_name

    def read_field(self, frame_number, field_type):
        num_str = f"{frame_number:05d}"
        suffix_map = {
            'velocity': '_vp',
            'temperature': '_t',
            'viscosity': '_eta',
            'composition': '_c',
            'topography': '_cs',
            'crustal thickness': '_cr',
            'age': '_age',
            'strain rate': '_ed',
            'geoid': '_g'
        }
        
        if field_type not in suffix_map:
            raise ValueError(f"Unknown field type: {field_type}")
            
        fname = self.directory / f"{self.file_name}{suffix_map[field_type]}{num_str}"
        
        if not fname.exists():
            raise FileNotFoundError(f"File not found: {fname}")

        is_scalar = (field_type != 'velocity')
        nval = 1 if is_scalar else 4

        with open(fname, 'rb') as f:
            # Read magic number
            magic_bytes = f.read(4)
            if not magic_bytes:
                raise EOFError("Empty file")
            magic = struct.unpack('i', magic_bytes)[0]
            
            if magic > 8000:
                INTSTR = 'q' # int64
                FLTSTR = 'd' # double
                magic -= 8000
                f.read(4) # extra 4 bytes for 64-bit alignment in header? 
            else:
                INTSTR = 'i' # int32
                FLTSTR = 'f' # single

            magic_mod = magic % 100
            xyp = 1 if (magic_mod >= 9 and nval == 4) else 0

            # Header reads
            def read_val(fmt, count=1):
                if count == 0:
                    return np.array([])
                size = struct.calcsize(fmt)
                data = f.read(size * count)
                if not data:
                    return None
                res = struct.unpack(fmt * count, data)
                return res if count > 1 else res[0]

            def read_coords(fmt, count):
                if count == 0:
                    return np.array([])
                size = struct.calcsize(fmt)
                data = f.read(size * count)
                if not data:
                    return np.array([])
                res = struct.unpack(fmt * count, data)
                return np.atleast_1d(np.array(res))

            nxtot = read_val(INTSTR)
            nytot = read_val(INTSTR)
            nztot = read_val(INTSTR)
            nblocks = read_val(INTSTR)
            aspect = read_val(FLTSTR, 2)
            nnx = read_val(INTSTR)
            nny = read_val(INTSTR)
            nnz = read_val(INTSTR)
            nnb = read_val(INTSTR)

            nz2 = nztot * 2 + 1
            zg = read_coords(FLTSTR, nz2)

            nxpn = nxtot // nnx
            nypn = nytot // nny
            nzpn = nztot // nnz
            nbpn = nblocks // nnb
            
            npi = (nxpn + xyp) * (nypn + xyp) * nzpn * nbpn * nval

            rcmb = read_val(FLTSTR)
            istep = read_val(INTSTR)
            time = read_val(FLTSTR)
            erupta = read_val(FLTSTR)
            
            if magic_mod >= 12:
                erupta_TTG = read_val(FLTSTR)
                intruda = read_val(FLTSTR, 2)
                TTGmass = read_val(FLTSTR, 3)
            
            botT_val = read_val(FLTSTR)
            if magic_mod >= 10:
                T_core = read_val(FLTSTR)
            if magic_mod >= 11:
                water_b = read_val(FLTSTR)

            x_coords = read_coords(FLTSTR, nxtot)
            y_coords = read_coords(FLTSTR, nytot)
            z_coords = read_coords(FLTSTR, nztot)

            # Pre-allocate arrays
            if is_scalar:
                data_3d = np.zeros((nxtot, nytot, nztot, nblocks))
            else:
                scalefac = read_val(FLTSTR)
                vx_3d = np.zeros((nxtot, nytot, nztot, nblocks))
                vy_3d = np.zeros((nxtot, nytot, nztot, nblocks))
                vz_3d = np.zeros((nxtot, nytot, nztot, nblocks))
                p_3d = np.zeros((nxtot, nytot, nztot, nblocks))

            # Read parallel blocks
            float_dtype = np.float64 if FLTSTR == 'd' else np.float32
            float_size = struct.calcsize(FLTSTR)
            
            for ibc in range(nnb):
                for izc in range(nnz):
                    for iyc in range(nny):
                        for ixc in range(nnx):
                            raw_data = f.read(npi * float_size)
                            data_cpu = np.frombuffer(raw_data, dtype=float_dtype)
                            
                            if is_scalar:
                                # MATLAB order: [nxpn, nypn, nzpn, nbpn]
                                data_cpu_3d = data_cpu.reshape((nxpn, nypn, nzpn, nbpn), order='F')
                                
                                x_slice = slice(ixc * nxpn, (ixc + 1) * nxpn)
                                y_slice = slice(iyc * nypn, (iyc + 1) * nypn)
                                z_slice = slice(izc * nzpn, (izc + 1) * nzpn)
                                b_slice = slice(ibc * nbpn, (ibc + 1) * nbpn)
                                
                                data_3d[x_slice, y_slice, z_slice, b_slice] = data_cpu_3d
                            else:
                                data_cpu_scaled = data_cpu * scalefac
                                # MATLAB order: [nval, nxpn+xyp, nypn+xyp, nzpn, nbpn]
                                data_cpu_3d = data_cpu_scaled.reshape((nval, nxpn + xyp, nypn + xyp, nzpn, nbpn), order='F')
                                
                                x_slice = slice(ixc * nxpn, (ixc + 1) * nxpn)
                                y_slice = slice(iyc * nypn, (iyc + 1) * nypn)
                                z_slice = slice(izc * nzpn, (izc + 1) * nzpn)
                                b_slice = slice(ibc * nbpn, (ibc + 1) * nbpn)
                                
                                vx_3d[x_slice, y_slice, z_slice, b_slice] = data_cpu_3d[0, :nxpn, :nypn, :, :]
                                vy_3d[x_slice, y_slice, z_slice, b_slice] = data_cpu_3d[1, :nxpn, :nypn, :, :]
                                vz_3d[x_slice, y_slice, z_slice, b_slice] = data_cpu_3d[2, :nxpn, :nypn, :, :]
                                p_3d[x_slice, y_slice, z_slice, b_slice]  = data_cpu_3d[3, :nxpn, :nypn, :, :]

        if is_scalar:
            return x_coords, y_coords, z_coords, data_3d, time
        else:
            return x_coords, y_coords, z_coords, vx_3d, vy_3d, vz_3d, p_3d, time

# =============================================================================
# MAIN PROCESSING LOOP
# =============================================================================

def main():
    print(f"{'='*60}\n       STAGPLOT: SURFACE EVOLUTION (2D)       \n{'='*60}")
    
    if not HAS_CRAMERI:
        print("[!] WARNING: 'cmcrameri' package not found. Using Matplotlib defaults.")
        print("          pip install cmcrameri")
    
    reader = StagYYReader(directory, file_name)
    frames = np.arange(start_frame, end_frame + 1, step)
    n_frames = len(frames)
    
    # Determine grid size from first frame
    try:
        # Try a few fields in case topography is not available
        found_field = False
        for ftype in ['topography', 'crustal thickness', 'temperature', 'age']:
            try:
                res = reader.read_field(frames[0], ftype)
                theta, phi, z = res[0], res[1], res[2]
                found_field = True
                break
            except (FileNotFoundError, ValueError):
                continue
        
        if not found_field:
            print(f"[!] ERROR: Could not read any field from first frame {frames[0]}.")
            return

        # For 2D annulus, we expect one of theta/phi to be the angular coordinate
        if len(theta) > 1 and len(phi) == 1:
            n_angle = len(theta)
            angle_axis = np.degrees(theta) if theta.max() < 2*np.pi else theta
        else:
            n_angle = len(phi)
            angle_axis = np.degrees(phi) if phi.max() < 2*np.pi else phi
            
        print(f"[INFO] Grid size: {n_angle} angular points, {n_frames} temporal points.")
    except Exception as e:
        print(f"[!] ERROR determining grid size: {e}")
        return

    times = np.zeros(n_frames)
    
    # Field configuration with colormaps
    # (field_type, include, limits, label, tag, colormap)
    field_configs = [
        ('topography', include_topography, topo_lim, 'Surface Topography [km]', 'topo', 
         get_cmap(CM_TOPO, MP_TOPO)),
        ('age', include_age, age_lim, 'Surface Age [Myr]', 'age', 
         get_cmap(CM_AGE, MP_AGE)),
        ('strain rate', include_strainrate, edot_lim, 'Surface Strain Rate [log10 1/s]', 'strainrate', 
         get_cmap(CM_STRAIN, MP_STRAIN)),
        ('velocity', include_velocity, vel_lim, 'Surface Velocity [cm/yr]', 'velocity', 
         get_cmap(CM_VELOCITY, MP_VELOCITY)),
        ('crustal thickness', include_crustthick, crthick_lim, 'Crustal Thickness [km]', 'crustthick', 
         get_cmap(CM_CRUST, MP_CRUST))
    ]
    
    data_storage = {tag: np.zeros((n_angle, n_frames)) for _, inc, _, _, tag, _ in field_configs if inc}
    
    print(f"\n[INFO] Starting data processing...")
    for i, frame in enumerate(frames):
        if (i+1) % 10 == 0 or i == 0:
            print(f"       Processing frame {frame:05d} ({i+1} of {n_frames})...")
        
        got_time = False
        
        for field_type, include, lim, title, tag, cmap in field_configs:
            if not include:
                continue
            
            try:
                if field_type == 'velocity':
                    x, y, z, vx, vy, vz, p, time = reader.read_field(frame, 'velocity')
                    nz = vz.shape[2]
                    vh = vscale * np.sqrt(vx[:, :, nz-1, :]**2 + vy[:, :, nz-1, :]**2)
                    surf_data = vh
                else:
                    x, y, z, data, time = reader.read_field(frame, field_type)
                    if field_type == 'topography':
                        surf_data = data[:, :, 1, :] * Dscale
                    elif field_type == 'crustal thickness':
                        surf_data = data.squeeze() * Dscale
                    else:
                        nz = data.shape[2]
                        surf_data = data[:, :, nz-1, :]
                        if field_type == 'age':
                            surf_data *= tscale

                val = surf_data.squeeze()
                
                if field_type == 'strain rate':
                    # Log-scale handling
                    val = np.log10(np.where(val > 0, val, 1e-25))
                
                data_storage[tag][:, i] = val
                
                if not got_time:
                    times[i] = time * tscale
                    got_time = True
                    
            except (FileNotFoundError, ValueError):
                pass

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

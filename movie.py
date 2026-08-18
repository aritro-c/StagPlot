import os
import glob
import subprocess
import sys
import platform
from rich.console import Console

console = Console()

def main():
    # ===================================== USER INPUT =======================================================
    
    INPUT_DIRECTORY = "/home/aritro/Documents/Academia/PhD/post_processing/stagpy/StagPlot-main/venus_i_01_frames_T_constant_time/"  # Directory containing the .png files
    MOVIE_FPS = 20
    MOVIE_LENGTH = None         # in seconds. If this has some value, the script calculates FPS automatically and overrides MOVIE_FPS. Set to "None" to use MOVIE_FPS.
    VIDEO_QUALITY = "Optimal"   # Options: Lossless, Optimal, Potato
    OUTPUT_FILE = "T_test.mp4"

    # =============================== USER EDITS NOTHING BELOW ===============================================

    console.print(f"[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]             MOVIE CREATION SCRIPT             [/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

    # --- DETERMINE FRAMES & FPS ---
    with console.status(f"[bold green]Scanning '{INPUT_DIRECTORY}' for .png files...", spinner="dots"):
        search_pattern = os.path.join(INPUT_DIRECTORY, "*.png")
        png_files = sorted(glob.glob(search_pattern))
        num_frames = len(png_files)

    if num_frames == 0:
        console.print(f"[bold red][!] ERROR:[/bold red] No .png files found in '{INPUT_DIRECTORY}'.")
        sys.exit(1)

    console.print(f"[green][+][/green] Found [bold cyan]{num_frames}[/bold cyan] .png frames.")

    if MOVIE_LENGTH is not None:
        effective_fps = max(1, int(round(num_frames / MOVIE_LENGTH)))
        console.print(f"[green][+][/green] Target length: [yellow]{MOVIE_LENGTH}s[/yellow] -> Using [bold cyan]{effective_fps}[/bold cyan] FPS")
    else:
        effective_fps = MOVIE_FPS
        console.print(f"[green][+][/green] Using [bold cyan]{effective_fps}[/bold cyan] FPS")

    # --- APPLY QUALITY PRESETS ---
    if VIDEO_QUALITY == "Lossless":
        quality_args = ["-crf", "0", "-preset", "veryslow"]
        scale_filter = ""
    elif VIDEO_QUALITY == "Potato":
        quality_args = ["-crf", "35", "-preset", "ultrafast"]
        scale_filter = "scale=trunc(iw*0.5):trunc(ih*0.5),"
    else: # Optimal
        quality_args = ["-crf", "25", "-preset", "medium"]
        scale_filter = "scale=trunc(iw*0.8):trunc(ih*0.8),"

    console.print(f"[green][+][/green] Quality Preset: [bold magenta]{VIDEO_QUALITY}[/bold magenta]")
    console.print(f"[green][+][/green] Output File: [bold yellow]{OUTPUT_FILE}[/bold yellow]")

    # --- RUN FFMPEG ---
    try:
        with console.status("[bold green]Running FFmpeg...", spinner="dots"):
            # On Windows, FFmpeg often lacks glob support, so we use image2pipe.
            # On Linux/macOS, we use the standard glob pattern for efficiency.
            if platform.system() == "Windows":
                cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(effective_fps),
                    "-f", "image2pipe",
                    "-i", "-",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-vf", f"{scale_filter}pad=ceil(iw/2)*2:ceil(ih/2)*2"
                ] + quality_args + [OUTPUT_FILE]
                
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for file in png_files:
                    with open(file, "rb") as f:
                        process.stdin.write(f.read())
                out, err = process.communicate()
                
                class ResultDummy: pass
                result = ResultDummy()
                result.returncode = process.returncode
                result.stderr = err.decode('utf-8', errors='replace')
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(effective_fps),
                    "-pattern_type", "glob",
                    "-i", search_pattern,
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-vf", f"{scale_filter}pad=ceil(iw/2)*2:ceil(ih/2)*2"
                ] + quality_args + [OUTPUT_FILE]
                
                result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            console.print(f"[bold green][SUCCESS][/bold green] Movie created: [yellow]{OUTPUT_FILE}[/yellow]")
        else:
            console.print(f"[bold red][!] ERROR:[/bold red] FFmpeg failed with return code {result.returncode}")
            # Provide snippet of FFmpeg error for debugging
            error_log = result.stderr.split('\n')[-10:] # Last 10 lines
            console.print("[dim]FFmpeg Tail Output:[/dim]")
            for line in error_log:
                if line.strip(): console.print(f"    [dim]{line.strip()}[/dim]")

    except FileNotFoundError:
        console.print("[bold red][!] ERROR:[/bold red] 'ffmpeg' command not found. Please install FFmpeg.")
    except Exception as e:
        console.print(f"[bold red][!] ERROR:[/bold red] An unexpected error occurred: [dim]{e}[/dim]")

if __name__ == "__main__":
    main()

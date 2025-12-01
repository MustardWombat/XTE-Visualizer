import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import matplotlib.cm as cm
from matplotlib.colors import Normalize

def parse_navigation_log(filepath):
    """Parse navigation log file and extract coordinates and Cross Track Error data."""
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        # Skip header lines and find data start
        data_start = False
        for line in lines:
            if line.startswith('2025-'):
                data_start = True
            if data_start and line.strip():
                parts = line.split('\t')
                if len(parts) >= 4:
                    xte = float(parts[1])
                    lat = float(parts[2])
                    lon = float(parts[3])
                    data.append({'xte': xte, 'lat': lat, 'lon': lon})
    return data

def create_ab_line(point_a, point_b):
    """Create line parameters from two points."""
    return {
        'start': point_a,
        'end': point_b,
        'slope': (point_b['lon'] - point_a['lon']) / (point_b['lat'] - point_a['lat']) if point_b['lat'] != point_a['lat'] else float('inf')
    }

def plot_combined_navigation(all_runs_data):
    """Plot all runs combined into a single averaged path."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))  # Shorter height
    
    # Use first run to establish A-B line
    first_data = all_runs_data[0]['data']
    ab_line = create_ab_line(first_data[0], first_data[-1])
    
    # Collect all points from all runs (using actual GPS positions)
    all_lats = []
    all_lons = []
    
    # Process each run
    for run_data in all_runs_data:
        data = run_data['data']
        
        lats = [p['lat'] for p in data]
        lons = [p['lon'] for p in data]
        
        all_lats.extend(lats)
        all_lons.extend(lons)
    
    # Convert to arrays
    all_lats = np.array(all_lats)
    all_lons = np.array(all_lons)
    
    # Plot A-B line
    ax.plot([ab_line['start']['lat'], ab_line['end']['lat']], 
             [ab_line['start']['lon'], ab_line['end']['lon']], 
             'g-', linewidth=4, label='A-B Line', zorder=1)
    
    # Plot actual GPS positions
    ax.scatter(all_lats, all_lons, c='blue', s=25, alpha=0.6, 
              edgecolors='black', linewidth=0.4, zorder=4,
              label='GPS Path')
    
    # Mark A and B points
    ax.plot(ab_line['start']['lat'], ab_line['start']['lon'], 'go', 
             markersize=22, zorder=10)
    ax.text(ab_line['start']['lat'], ab_line['start']['lon'], 'A', 
             color='white', fontsize=14, fontweight='bold', ha='center', va='center', zorder=11)
    
    ax.plot(ab_line['end']['lat'], ab_line['end']['lon'], 'ro', 
             markersize=22, zorder=10)
    ax.text(ab_line['end']['lat'], ab_line['end']['lon'], 'B', 
             color='white', fontsize=14, fontweight='bold', ha='center', va='center', zorder=11)
    
    # Configure plot
    ax.set_xlabel('Latitude', fontsize=14)  # Match histogram font
    ax.set_ylabel('Longitude', fontsize=14)  # Match histogram font
    ax.set_title(f'GPS Path - {len(all_runs_data)} Runs', 
                 fontsize=16, fontweight='bold')  # Match histogram font
    ax.legend(loc='best', fontsize=12)  # Match histogram font
    ax.grid(True, alpha=0.3)  # Match histogram grid
    ax.set_aspect('auto')  # Allow stretching to fill the figure
    
    # Force narrow x-axis to create tall aspect ratio
    lat_range = all_lats.max() - all_lats.min()
    lon_range = all_lons.max() - all_lons.min()
    lat_center = (all_lats.max() + all_lats.min()) / 2
    lon_center = (all_lons.max() + all_lons.min()) / 2
    
    # Set x-axis to be VERY narrow - 1/8 the range of y-axis
    new_lat_range = lon_range / 5  # Wider x-axis for broader graph
    ax.set_xlim(lat_center - new_lat_range/2, lat_center + new_lat_range/2)
    ax.set_ylim(all_lons.min() - lon_range*0.05, all_lons.max() + lon_range*0.05)
    
    # Manually set exactly 3 tick marks on x-axis
    ax.set_xticks([lat_center - new_lat_range/4, lat_center + new_lat_range/4])  # 2 ticks
    # Set 12 evenly spaced ticks on y-axis
    y_ticks = np.linspace(all_lons.min(), all_lons.max(), 12)
    ax.set_yticks(y_ticks)
    
    # Turn off minor ticks completely
    ax.minorticks_off()
    
    # Format axes to show full decimal degrees instead of scientific notation
    ax.ticklabel_format(style='plain', useOffset=False)
    ax.tick_params(labelsize=12)  # Match histogram tick size
    
    # Add simple statistics
    stats_text = f'Runs: {len(all_runs_data)} | Points: {len(all_lats)}'
    ax.text(0.5, 0.01, stats_text, transform=ax.transAxes, 
             verticalalignment='bottom', horizontalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=12)  # Match histogram stats font
    
    # Don't use any automatic layout - force the aspect
    fig.subplots_adjust(left=0.12, right=0.94, top=0.97, bottom=0.03)  # Better margins
    return fig

def main():
    # Get the directory containing the script
    base_dir = Path(__file__).parent
    
    # Create output folder for plots
    output_dir = base_dir / "line_plots"
    output_dir.mkdir(exist_ok=True)
    
    # Find all navigation log files
    log_files = sorted(base_dir.glob('NavigationLog_*.txt'))
    
    if not log_files:
        print("No navigation log files found!")
        return
    
    print(f"Found {len(log_files)} navigation log files")
    
    all_runs_data = []
    
    # Process each log file
    for log_file in log_files:
        print(f"Loading: {log_file.name}")
        
        # Parse the data
        data = parse_navigation_log(log_file)
        
        if len(data) < 2:
            print(f"  Insufficient data in {log_file.name}")
            continue
        
        # Store data for combined plot
        all_runs_data.append({
            'name': log_file.stem,
            'data': data
        })
    
    # Generate combined plot
    if all_runs_data:
        print("\nGenerating combined plot...")
        fig = plot_combined_navigation(all_runs_data)
        
        # Save combined plot
        output_file = output_dir / "Combined_All_Runs.png"
        
        # Delete old file if it exists to force regeneration
        if output_file.exists():
            output_file.unlink()
            print(f"Deleted old plot file")
        
        # Force exact dimensions with same DPI as histogram
        fig.set_size_inches(8, 10)  # Shorter height
        plt.savefig(output_file, dpi=150, facecolor='white', bbox_inches='tight')
        print(f"Saved combined plot: {output_file.relative_to(base_dir)}")
        print(f"File size: {output_file.stat().st_size} bytes")
        
        plt.close(fig)
        
        print(f"\nCombined plot saved to: {output_dir.relative_to(base_dir)}/")
    else:
        print("No valid data found for plotting.")

if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

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

def plot_combined_histogram(all_runs_data, output_file):
    """Create a histogram of Cross Track Error distribution across all runs."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    
    # Collect all Cross Track Error values from all runs
    all_xtes = []
    for run_data in all_runs_data:
        all_xtes.extend([p['xte'] for p in run_data['data']])
    
    all_xtes = np.array(all_xtes)
    
    # Plot: Histogram with statistical distribution
    n, bins, patches = ax.hist(all_xtes, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
    
    # Make the x-axis symmetric around zero
    max_abs_xte = np.max(np.abs(all_xtes))
    ax.set_xlim(-max_abs_xte, max_abs_xte)
    
    # Add vertical lines for mean
    mean_xte = np.mean(all_xtes)
    ax.axvline(mean_xte, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_xte*100:.1f}cm')
    ax.axvline(0, color='black', linestyle='-', linewidth=1.5, label='Zero Cross Track Error')
    
    ax.set_xlabel('Cross Track Error (m)', fontsize=14)
    ax.set_ylabel('Frequency', fontsize=14)
    ax.set_title(f'Cross Track Error Distribution - {len(all_runs_data)} Runs Combined', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=12)
    
    # Add statistics box
    stats_text = (
        f'Total Points: {len(all_xtes)}\n'
        f'Mean: {mean_xte*100:.1f}cm\n'
        f'Std Dev: {np.std(all_xtes)*100:.1f}cm\n'
        f'Mean |Error|: {np.mean(np.abs(all_xtes))*100:.1f}cm\n'
        f'Max |Error|: {np.max(np.abs(all_xtes))*100:.1f}cm\n'
        f'95th %ile: {np.percentile(np.abs(all_xtes), 95)*100:.1f}cm'
    )
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, 
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=12)
    
    # Add note about RTK-GPS uncertainty
    note_text = (
        'Note: Cross Track Error represents the lateral offset from the A-B guidance line.\n'
        'This includes both steering accuracy and RTK-GPS positioning error.\n'
        'Without ground truth, these sources of error cannot be separated.'
    )
    fig.text(0.5, 0.02, note_text, ha='center', fontsize=10, style='italic', 
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(output_file, dpi=150)
    plt.close(fig)
    
    return all_xtes

def main():
    # Get the directory containing the script
    base_dir = Path(__file__).parent
    
    # Create output folder for histogram
    output_dir = base_dir / "histogram_analysis"
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
        
        # Store data for combined analysis
        all_runs_data.append({
            'name': log_file.stem,
            'data': data
        })
    
    # Generate combined histogram
    if all_runs_data:
        print("\nGenerating combined histogram...")
        histogram_file = output_dir / "Combined_XTE_Histogram.png"
        all_xtes = plot_combined_histogram(all_runs_data, histogram_file)
        print(f"Saved combined histogram: {histogram_file.relative_to(base_dir)}")
        
        # Print overall statistics
        print("\n" + "="*60)
        print("COMBINED STATISTICS (All Runs)")
        print("="*60)
        print(f"Total data points: {len(all_xtes)}")
        print(f"Mean Cross Track Error: {np.mean(all_xtes):.3f}m ({np.mean(all_xtes)*100:.1f}cm)")
        print(f"Mean |Cross Track Error|: {np.mean(np.abs(all_xtes)):.3f}m ({np.mean(np.abs(all_xtes))*100:.1f}cm)")
        print(f"Std deviation: {np.std(all_xtes):.3f}m ({np.std(all_xtes)*100:.1f}cm)")
        print(f"Max |Cross Track Error|: {np.max(np.abs(all_xtes)):.3f}m ({np.max(np.abs(all_xtes))*100:.1f}cm)")
        print(f"95th percentile |Cross Track Error|: {np.percentile(np.abs(all_xtes), 95):.3f}m ({np.percentile(np.abs(all_xtes), 95)*100:.1f}cm)")
        print("="*60)
        
        print(f"\nHistogram saved to: {output_dir.relative_to(base_dir)}/")
    else:
        print("No valid data found for histogram generation.")

if __name__ == "__main__":
    main()
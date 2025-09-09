#!/usr/bin/env python3
"""
Create a CSV file with fMRI session timing breakdown.
Updated to reflect 10 TR exploration time for One Target.
Shows minutes instead of seconds, rounded to 2 decimal places.
"""

import csv
import os
from datetime import datetime

# Fixed TR value
TR = 2.01  # seconds

def create_timing_csv():
    """Create a CSV file with timing breakdown for each run."""
    
    # Calculate timing values
    ptsod_trs = 236
    ptsod_time = ptsod_trs * TR
    ptsod_minutes = round(ptsod_time / 60, 2)
    
    # Updated One Target calculation with 10 TR exploration and 10 TR annotation
    one_target_trs = 332  # Updated: 6 × (10 + 10) + other components
    one_target_time = one_target_trs * TR
    one_target_minutes = round(one_target_time / 60, 2)
    
    multi_arena_trs = 632
    multi_arena_time = multi_arena_trs * TR
    multi_arena_minutes = round(multi_arena_time / 60, 2)
    
    # Non-fMRI scans
    anatomy_trs = 448  # 15 minutes = 448 TRs
    anatomy_time = anatomy_trs * TR
    anatomy_minutes = round(anatomy_time / 60, 2)
    rest_trs = 239  # 8 minutes = 239 TRs
    rest_time = rest_trs * TR
    rest_minutes = round(rest_time / 60, 2)
    
    # Create CSV data
    csv_data = [
        # Non-fMRI scans
        ["Anatomy Scan", anatomy_minutes, anatomy_trs, "15 minutes structural scan"],
        ["Rest Scan 1", rest_minutes, rest_trs, "8 minutes rest scan at beginning"],
        ["Rest Scan 2", rest_minutes, rest_trs, "8 minutes rest scan at beginning"],
        
        # fMRI experimental runs
        ["PTSOD fMRI Run 1", ptsod_minutes, ptsod_trs, "PTSOD experiment - first run"],
        ["One Target Run", one_target_minutes, one_target_trs, "One Target experiment with 10 TR exploration + 10 TR annotation"],
        ["Full Arena Run", multi_arena_minutes, multi_arena_trs, "Multi Arena experiment with 60 TR exploration + 30 TR annotation"],
        ["PTSOD fMRI Run 2", ptsod_minutes, ptsod_trs, "PTSOD experiment - second run"],
    ]
    
    # Create CSV file
    output_file = 'fMRI_Session_Timing.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['run', 'minutes', 'TRs', 'notes'])
        
        # Write data
        for row in csv_data:
            writer.writerow(row)
        
        # Add summary rows
        writer.writerow([])  # Empty row for spacing
        
        # Calculate totals
        total_fmri_trs = ptsod_trs * 2 + one_target_trs + multi_arena_trs
        total_fmri_time = total_fmri_trs * TR
        total_fmri_minutes = round(total_fmri_time / 60, 2)
        
        grand_total_trs = total_fmri_trs + anatomy_trs + rest_trs * 2
        grand_total_time = grand_total_trs * TR
        grand_total_minutes = round(grand_total_time / 60, 2)
        
        # Summary rows
        writer.writerow(['TOTAL fMRI SCANNING', total_fmri_minutes, total_fmri_trs, f'{total_fmri_minutes} minutes of experimental scanning'])
        writer.writerow(['TOTAL SESSION', grand_total_minutes, grand_total_trs, f'{grand_total_minutes} minutes including anatomy and rest scans'])
    
    print(f"Timing CSV saved as: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
    
    # Print summary
    print(f"\nSUMMARY:")
    print(f"Total fMRI scanning time: {total_fmri_minutes} minutes ({total_fmri_trs} TRs)")
    print(f"Total session time: {grand_total_minutes} minutes ({grand_total_trs} TRs)")
    print(f"One Target exploration: 10 TRs per trial (updated from 5 TRs)")
    print(f"One Target annotation: 10 TRs per trial")
    
    return output_file

def main():
    """Main function."""
    print("Creating fMRI session timing CSV...")
    print(f"TR = {TR} seconds")
    print("Updated One Target exploration to 10 TRs per trial")
    print("Showing minutes rounded to 2 decimal places")
    
    # Create the CSV
    output_file = create_timing_csv()
    
    print(f"\nCSV creation completed!")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()

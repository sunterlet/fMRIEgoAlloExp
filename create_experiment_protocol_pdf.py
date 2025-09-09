#!/usr/bin/env python3
"""
Create a PDF with the complete fMRI experiment protocol.
Based on the timing calculations and experimental design.
"""

from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, darkblue, red

# Fixed TR value
TR = 2.01  # seconds

def create_experiment_protocol_pdf():
    """Create a comprehensive experiment protocol PDF."""
    
    # Calculate timing values
    ptsod_trs = 236
    ptsod_minutes = round(ptsod_trs * TR / 60, 2)
    
    one_target_trs = 332
    one_target_minutes = round(one_target_trs * TR / 60, 2)
    
    multi_arena_trs = 632
    multi_arena_minutes = round(multi_arena_trs * TR / 60, 2)
    
    anatomy_trs = 448
    anatomy_minutes = round(anatomy_trs * TR / 60, 2)
    rest_trs = 239
    rest_minutes = round(rest_trs * TR / 60, 2)
    
    total_fmri_trs = ptsod_trs * 2 + one_target_trs + multi_arena_trs
    total_fmri_minutes = round(total_fmri_trs * TR / 60, 2)
    
    grand_total_trs = total_fmri_trs + anatomy_trs + rest_trs * 2
    grand_total_minutes = round(grand_total_trs * TR / 60, 2)
    
    # Create PDF document
    output_file = 'fMRI_Experiment_Protocol.pdf'
    doc = SimpleDocTemplate(output_file, pagesize=A4, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=blue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=15,
        textColor=darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=4,
        leading=14,
        leftIndent=20
    )
    
    # Build the story (content)
    story = []
    
    # Title
    story.append(Paragraph("fMRI EXPERIMENT PROTOCOL", title_style))
    story.append(Paragraph("Egocentric-Allocentric Translation Study", title_style))
    story.append(Spacer(1, 20))
    
    # Generation info
    story.append(Paragraph(f"Protocol Version: 1.0", normal_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Paragraph(f"TR Value: {TR} seconds", normal_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    story.append(Paragraph(f"Total Session Duration: {grand_total_minutes} minutes ({grand_total_trs} TRs)", normal_style))
    story.append(Paragraph(f"fMRI Scanning Time: {total_fmri_minutes} minutes ({total_fmri_trs} TRs)", normal_style))
    story.append(Paragraph("Experimental Conditions: PTSOD, One Target, Multi Arena", normal_style))
    story.append(Paragraph("Scanner Requirements: 3T MRI with response box", normal_style))
    story.append(Spacer(1, 20))
    
    # Session Overview
    story.append(Paragraph("SESSION OVERVIEW", heading_style))
    story.append(Paragraph("This fMRI experiment investigates egocentric-allocentric spatial translation using three experimental paradigms:", normal_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1. <b>PTSOD (Path Integration Task)</b>", normal_style))
    story.append(Paragraph("• Tests spatial memory and navigation abilities", bullet_style))
    story.append(Paragraph("• Memory and no-memory conditions", bullet_style))
    story.append(Paragraph("• Fixed target locations", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("2. <b>One Target Experiment</b>", normal_style))
    story.append(Paragraph("• Single target placement and annotation", bullet_style))
    story.append(Paragraph("• Dynamic target placement based on movement", bullet_style))
    story.append(Paragraph("• Exploration + annotation phases", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("3. <b>Multi Arena Experiment</b>", normal_style))
    story.append(Paragraph("• Multiple target annotation in complex environments", bullet_style))
    story.append(Paragraph("• Extended exploration and annotation periods", bullet_style))
    story.append(Paragraph("• Spatial memory and navigation assessment", bullet_style))
    story.append(Spacer(1, 20))
    
    # Session Timeline
    story.append(Paragraph("SESSION TIMELINE", heading_style))
    
    # Pre-scanning
    story.append(Paragraph("<b>Pre-Scanning (30 minutes)</b>", subheading_style))
    story.append(Paragraph("• Participant briefing and consent", bullet_style))
    story.append(Paragraph("• Task instructions and practice", bullet_style))
    story.append(Paragraph("• Response box familiarization", bullet_style))
    story.append(Paragraph("• Safety screening", bullet_style))
    story.append(Spacer(1, 10))
    
    # Scanning session
    story.append(Paragraph("<b>Scanning Session ({grand_total_minutes} minutes)</b>", subheading_style))
    
    # Anatomy scan
    story.append(Paragraph(f"1. <b>Anatomy Scan</b> ({anatomy_minutes} minutes, {anatomy_trs} TRs)", normal_style))
    story.append(Paragraph("• High-resolution T1-weighted structural scan", bullet_style))
    story.append(Paragraph("• Purpose: Brain anatomy and registration", bullet_style))
    story.append(Spacer(1, 8))
    
    # Rest scans
    story.append(Paragraph(f"2. <b>Rest Scan 1</b> ({rest_minutes} minutes, {rest_trs} TRs)", normal_style))
    story.append(Paragraph("• Baseline resting state measurement", bullet_style))
    story.append(Paragraph("• Eyes open, mind wandering", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"3. <b>Rest Scan 2</b> ({rest_minutes} minutes, {rest_trs} TRs)", normal_style))
    story.append(Paragraph("• Second baseline measurement", bullet_style))
    story.append(Paragraph("• Ensures stable baseline", bullet_style))
    story.append(Spacer(1, 8))
    
    # Experimental runs
    story.append(Paragraph(f"4. <b>PTSOD fMRI Run 1</b> ({ptsod_minutes} minutes, {ptsod_trs} TRs)", normal_style))
    story.append(Paragraph("• First PTSOD experimental run", bullet_style))
    story.append(Paragraph("• 4 memory trials + 4 no-memory trials", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"5. <b>One Target Run</b> ({one_target_minutes} minutes, {one_target_trs} TRs)", normal_style))
    story.append(Paragraph("• 6 snake practice blocks + 6 one target blocks", bullet_style))
    story.append(Paragraph("• 10 TR exploration + 10 TR annotation per trial", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"6. <b>Full Arena Run</b> ({multi_arena_minutes} minutes, {multi_arena_trs} TRs)", normal_style))
    story.append(Paragraph("• 6 snake practice blocks + 6 multi arena blocks", bullet_style))
    story.append(Paragraph("• 60 TR exploration + 30 TR annotation per arena", bullet_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"7. <b>PTSOD fMRI Run 2</b> ({ptsod_minutes} minutes, {ptsod_trs} TRs)", normal_style))
    story.append(Paragraph("• Second PTSOD experimental run", bullet_style))
    story.append(Paragraph("• Identical structure to Run 1", bullet_style))
    story.append(Spacer(1, 20))
    
    # Experimental Details
    story.append(Paragraph("EXPERIMENTAL DETAILS", heading_style))
    
    # PTSOD Details
    story.append(Paragraph("<b>PTSOD Experiment</b>", subheading_style))
    story.append(Paragraph("• <b>Memory Trials:</b> 15 TRs memorization + 17 TRs navigation", normal_style))
    story.append(Paragraph("• <b>No-Memory Trials:</b> 17 TRs navigation only", normal_style))
    story.append(Paragraph("• <b>Target Placement:</b> Fixed, predetermined locations", normal_style))
    story.append(Paragraph("• <b>Response:</b> Navigate to remembered target location", normal_style))
    story.append(Paragraph("• <b>Timer Display:</b> Countdown during memory and navigation phases", normal_style))
    story.append(Spacer(1, 10))
    
    # One Target Details
    story.append(Paragraph("<b>One Target Experiment</b>", subheading_style))
    story.append(Paragraph("• <b>Exploration Phase:</b> 10 TRs (20.1 seconds) - participant controlled", normal_style))
    story.append(Paragraph("• <b>Target Placement:</b> Dynamic, based on movement and visited cells", normal_style))
    story.append(Paragraph("• <b>Annotation Phase:</b> 10 TRs (20.1 seconds) - fixed timer", normal_style))
    story.append(Paragraph("• <b>Response:</b> Navigate to target location and annotate", normal_style))
    story.append(Paragraph("• <b>Timer Display:</b> None during exploration, countdown during annotation", normal_style))
    story.append(Spacer(1, 10))
    
    # Multi Arena Details
    story.append(Paragraph("<b>Multi Arena Experiment</b>", subheading_style))
    story.append(Paragraph("• <b>Exploration Phase:</b> 60 TRs (120.6 seconds) - fixed timer", normal_style))
    story.append(Paragraph("• <b>Target Placement:</b> Multiple targets in complex arena", normal_style))
    story.append(Paragraph("• <b>Annotation Phase:</b> 30 TRs (60.3 seconds) - fixed timer", normal_style))
    story.append(Paragraph("• <b>Response:</b> Explore arena and annotate all targets", normal_style))
    story.append(Paragraph("• <b>Timer Display:</b> Countdown during annotation phase (fMRI mode only)", normal_style))
    story.append(Spacer(1, 20))
    
    # Technical Specifications
    story.append(Paragraph("TECHNICAL SPECIFICATIONS", heading_style))
    
    story.append(Paragraph("<b>Scanner Requirements</b>", subheading_style))
    story.append(Paragraph("• 3T MRI scanner", bullet_style))
    story.append(Paragraph("• TR = 2.01 seconds", bullet_style))
    story.append(Paragraph("• EPI sequence for functional scans", bullet_style))
    story.append(Paragraph("• T1-weighted sequence for structural scan", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Stimulus Presentation</b>", subheading_style))
    story.append(Paragraph("• MATLAB (Psychtoolbox) for PTSOD", bullet_style))
    story.append(Paragraph("• Python (Pygame) for One Target and Multi Arena", bullet_style))
    story.append(Paragraph("• MRI-compatible response box", bullet_style))
    story.append(Paragraph("• Projector or LCD display for visual stimuli", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Data Collection</b>", subheading_style))
    story.append(Paragraph("• Continuous logging (frame-by-frame)", bullet_style))
    story.append(Paragraph("• Discrete logging (trial summaries)", bullet_style))
    story.append(Paragraph("• Behavioral responses and timing", bullet_style))
    story.append(Paragraph("• Movement and navigation data", bullet_style))
    story.append(Spacer(1, 20))
    
    # Participant Instructions
    story.append(Paragraph("PARTICIPANT INSTRUCTIONS", heading_style))
    
    story.append(Paragraph("<b>General Instructions</b>", subheading_style))
    story.append(Paragraph("• Stay as still as possible during scanning", bullet_style))
    story.append(Paragraph("• Use response box buttons for navigation", bullet_style))
    story.append(Paragraph("• Follow on-screen instructions carefully", bullet_style))
    story.append(Paragraph("• Ask questions before scanning begins", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Response Box Controls</b>", subheading_style))
    story.append(Paragraph("• Button 7: Rotate left", bullet_style))
    story.append(Paragraph("• Button 8: Move forward", bullet_style))
    story.append(Paragraph("• Button 9: Move backward", bullet_style))
    story.append(Paragraph("• Button 0: Rotate right", bullet_style))
    story.append(Paragraph("• Button 1 or ENTER: Confirm/continue", bullet_style))
    story.append(Spacer(1, 20))
    
    # Data Analysis Plan
    story.append(Paragraph("DATA ANALYSIS PLAN", heading_style))
    
    story.append(Paragraph("<b>Behavioral Analysis</b>", subheading_style))
    story.append(Paragraph("• Navigation accuracy and efficiency", bullet_style))
    story.append(Paragraph("• Response times and movement patterns", bullet_style))
    story.append(Paragraph("• Target annotation accuracy", bullet_style))
    story.append(Paragraph("• Spatial memory performance", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>fMRI Analysis</b>", subheading_style))
    story.append(Paragraph("• Preprocessing: motion correction, normalization", bullet_style))
    story.append(Paragraph("• First-level: task-specific activation maps", bullet_style))
    story.append(Paragraph("• Second-level: group analysis and comparisons", bullet_style))
    story.append(Paragraph("• ROI analysis: hippocampus, parietal cortex", bullet_style))
    story.append(Spacer(1, 20))
    
    # Quality Control
    story.append(Paragraph("QUALITY CONTROL", heading_style))
    
    story.append(Paragraph("<b>Data Quality Checks</b>", subheading_style))
    story.append(Paragraph("• Motion parameters (< 3mm translation, < 3° rotation)", bullet_style))
    story.append(Paragraph("• Signal-to-noise ratio assessment", bullet_style))
    story.append(Paragraph("• Behavioral performance monitoring", bullet_style))
    story.append(Paragraph("• Scanner stability checks", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Participant Monitoring</b>", subheading_style))
    story.append(Paragraph("• Comfort and safety throughout session", bullet_style))
    story.append(Paragraph("• Task comprehension verification", bullet_style))
    story.append(Paragraph("• Fatigue and attention monitoring", bullet_style))
    story.append(Paragraph("• Emergency procedures awareness", bullet_style))
    story.append(Spacer(1, 20))
    
    # Safety Considerations
    story.append(Paragraph("SAFETY CONSIDERATIONS", heading_style))
    
    story.append(Paragraph("<b>MRI Safety</b>", subheading_style))
    story.append(Paragraph("• Standard MRI safety screening", bullet_style))
    story.append(Paragraph("• Metal object removal", bullet_style))
    story.append(Paragraph("• Emergency stop procedures", bullet_style))
    story.append(Paragraph("• Communication system testing", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Participant Safety</b>", subheading_style))
    story.append(Paragraph("• Comfort breaks if needed", bullet_style))
    story.append(Paragraph("• Claustrophobia assessment", bullet_style))
    story.append(Paragraph("• Emergency contact procedures", bullet_style))
    story.append(Paragraph("• Post-scan debriefing", bullet_style))
    story.append(Spacer(1, 20))
    
    # Contact Information
    story.append(Paragraph("CONTACT INFORMATION", heading_style))
    story.append(Paragraph("For questions about this protocol, contact:", normal_style))
    story.append(Paragraph("• Principal Investigator: [Name]", bullet_style))
    story.append(Paragraph("• Research Coordinator: [Name]", bullet_style))
    story.append(Paragraph("• Technical Support: [Name]", bullet_style))
    story.append(Spacer(1, 20))
    
    # Document Information
    story.append(Paragraph("DOCUMENT INFORMATION", heading_style))
    story.append(Paragraph("Generated by: create_experiment_protocol_pdf.py", normal_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    story.append(Paragraph(f"Time: {datetime.now().strftime('%H:%M:%S')}", normal_style))
    story.append(Paragraph("Version: Protocol v1.0", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("This protocol describes the complete fMRI experiment for investigating egocentric-allocentric spatial translation. All timing is based on TR-aligned calculations with TR = 2.01 seconds.", normal_style))
    
    # Build the PDF
    doc.build(story)
    
    print(f"Experiment protocol PDF saved as: {output_file}")
    return output_file

def main():
    """Main function."""
    print("Creating comprehensive fMRI experiment protocol PDF...")
    print(f"TR = {TR} seconds")
    
    # Create the PDF
    output_file = create_experiment_protocol_pdf()
    
    print(f"\nPDF creation completed!")
    print(f"Output file: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")

if __name__ == "__main__":
    main()




import csv
import os
import subprocess

# Define realistic theme colors (customize these as needed)
theme_colors = {
    "Restaurant": "#D35400",   # a realistic deep orange
    "Bakery": "#F1C40F",       # warm golden yellow
    "Library": "#2980B9",      # classic blue
    "Castle": "#8E44AD",       # regal purple
    "Temple": "#27AE60",       # natural green
    "Dungeon": "#34495E",      # dark slate blue/gray
    "Cemetery": "#7F8C8D",     # muted gray
    "Warehouse": "#E67E22",    # burnt orange
    "AmusementPark": "#E74C3C",# vibrant red
    "Highway": "#2C3E50",      # deep navy blue
    "Market": "#16A085",       # cool teal
    "Swamp": "#2ECC71",        # lively green
    "Tundra": "#BDC3C7",       # light cool gray
    "Volcano": "#E74C3C",      # striking red
    "Ski-Resort": "#5DADE2",    # crisp light blue
    "Opera-House": "#9B59B6",  # elegant lavender
    "Mountain": "#95A5A6",     # soft gray
    "Canyon": "#E67E22",       # warm orange
    "Valley": "#27AE60",       # refreshing green
    "Garden": "#7DCEA0",       # gentle mint
    "Junkyard": "#7F8C8D",     # rugged gray
    "Stadium": "#34495E",      # deep blue-gray
    "Laboratory": "#1ABC9C",   # modern turquoise
    "Gym": "#E67E22",          # energetic orange
    "Greenhouse": "#27AE60",   # natural green
    "PoliceStation": "#2C3E50",# authoritative navy
    "FireStation": "#E74C3C",  # emergency red
    "Harbor": "#2980B9",       # maritime blue
    "Sewer": "#2C3E50",        # dark, industrial blue
    "Cinema": "#8E44AD",       # dramatic purple
    "Circus": "#E67E22",       # playful orange
    "Racetrack": "#34495E",    # competitive deep blue
    "Planetarium": "#9B59B6",  # cosmic lavender
    "Waterfall": "#3498DB",    # flowing blue
    "Prison": "#7F8C8D",       # stark gray
    "Classroom": "#2980B9"     # academic blue
}

# File paths and settings
csv_file = "themes_icons.csv"      # CSV file with your list
base_svg_folder = "base_icons"       # Folder with base SVG files (e.g., Menu.svg)
output_folder = "output"             # Root output folder for theme directories
output_resolution = 256              # PNG width in pixels (height scales proportionally)

# Ensure output and temp directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs("temp", exist_ok=True)

with open(csv_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        theme = row["RoundName"]
        icon_name = row["ObjectName"]
        
        # Create theme folder if it doesn't exist
        theme_dir = os.path.join(output_folder, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        # Construct path to the base SVG
        base_svg_path = os.path.join(base_svg_folder, f"{icon_name}.svg")
        if not os.path.exists(base_svg_path):
            print(f"Warning: Base SVG not found for icon: {icon_name}")
            continue
        
        # Read SVG content
        with open(base_svg_path, "r") as file:
            svg_content = file.read()
        
        # Replace the placeholder color (assumed "#000000") with the theme's color
        theme_color = theme_colors.get(theme, "#000000")
        modified_svg = svg_content.replace("#000000", theme_color)
        
        # Save the modified SVG to a temporary file
        temp_svg_path = os.path.join("temp", f"{theme}_{icon_name}.svg")
        with open(temp_svg_path, "w") as file:
            file.write(modified_svg)
        
        # Define the output PNG file path
        output_png_path = os.path.join(theme_dir, f"{icon_name}.png")
        
        # Use Inkscape CLI to export the PNG (ensure Inkscape is installed and in PATH)
        cmd = [
            "inkscape",
            temp_svg_path,
            "--export-type=png",
            f"--export-filename={output_png_path}",
            f"--export-width={output_resolution}"
        ]
        subprocess.run(cmd, check=True)
        
        print(f"Generated {output_png_path}")

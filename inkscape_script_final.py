import os
import subprocess
import xml.etree.ElementTree as ET
import base64

# Paths
original_svg = "exp.svg"
temp_svg = "temp_label.svg"
output_folder = "output_pngs"
datamatrix_folder = "Data_MatrixImages"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Namespace handling
ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
namespaces = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink'
}

# Serial number prefix
serial_prefix = "2506ZLD60XSW"

# Generate labels
for i in range(2643, 3051):
    serial_number = f"{serial_prefix}{i:04d}"

    # Reload SVG each time
    tree = ET.parse(original_svg)
    root = tree.getroot()

    # Update text spans with matching IDs
    for elem in root.iter():
        if elem.tag.endswith("tspan") and elem.attrib.get("id") in {"tspan319", "tspan423"}:
            if elem.text and "serial_number_text" in elem.text:
                elem.text = elem.text.replace("serial_number_text", serial_number)

    # Update image (image27) with base64 image
    image_path = os.path.join(datamatrix_folder, f"{serial_number}.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            href_val = f"data:image/png;base64,{img_base64}"

            for image_elem in root.iter():
                if image_elem.attrib.get("id") == "image1":
                    image_elem.attrib["{http://www.w3.org/1999/xlink}href"] = href_val
                    break

    # Write modified SVG
    tree.write(temp_svg)

    # Export to PNG
    output_png = os.path.join(output_folder, f"label_{serial_number}.png")
    subprocess.run([
        "inkscape",
        temp_svg,
        "--export-type=png",
        "--export-area-page",
        "--export-dpi=600",
        "--export-background=white",
        "--export-background-opacity=255",
        "--export-filename", output_png
    ])

    print(f"Exported {output_png}")

# Cleanup
os.remove(temp_svg)
print("Done!")

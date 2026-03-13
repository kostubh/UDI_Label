import streamlit as st
import os
import io
import base64
import xml.etree.ElementTree as ET
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from pylibdmtx.pylibdmtx import encode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from pypdf import PdfWriter
import subprocess
import re
import requests
import json

# Page config
st.set_page_config(
    page_title="UDI Label Generator",
    page_icon="🏷️",
    layout="wide"
)

# Initialize session state
if 'datamatrix_images' not in st.session_state:
    st.session_state.datamatrix_images = {}
if 'label_pngs' not in st.session_state:
    st.session_state.label_pngs = {}
if 'svg_template' not in st.session_state:
    st.session_state.svg_template = None
if 'config' not in st.session_state:
    st.session_state.config = {
        'serial_prefix': '2506ZLD60XSW',
        'start_number': 1,
        'end_number': 100,
        'image_id': 'image1',
        'use_secondary': False,
        'secondary_image_id': 'image2'
    }

# Upload function for filebin.net
def upload_to_filebin(file_data, filename, file_size_mb):
    """Upload file to filebin.net and return shareable link"""
    try:
        # Generate a unique bin ID based on timestamp and filename
        import time
        import hashlib

        # Create a unique bin name
        timestamp = int(time.time())
        bin_id = hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:12]

        # filebin.net upload API
        url = f"https://filebin.net/{bin_id}/{filename}"

        # Upload file (simple PUT request)
        headers = {'Content-Type': 'application/pdf'}
        response = requests.post(url, data=file_data, headers=headers, timeout=300)

        if response.status_code in [200, 201]:
            # Generate shareable links
            bin_url = f"https://filebin.net/{bin_id}"
            file_url = f"https://filebin.net/{bin_id}/{filename}"

            return {
                'success': True,
                'bin_url': bin_url,
                'file_url': file_url,
                'filename': filename,
                'file_size_mb': file_size_mb
            }
        else:
            return {
                'success': False,
                'error': f"Upload failed: HTTP {response.status_code}. Response: {response.text[:300]}"
            }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': "Upload timed out (>5 min). File might be too large."
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Upload error: {str(e)[:300]}"
        }

# Title
st.title("🏷️ UDI Label Generator")
st.markdown("Generate UDI labels with optional DataMatrix barcodes, merge into PDF, and download.")

# Tabs for each step
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Generate DataMatrix",
    "2️⃣ Generate Labels",
    "3️⃣ Verify Sequence",
    "4️⃣ Create PDF"
])

# ==================== TAB 1: Generate DataMatrix ====================
with tab1:
    st.header("Step 1: Generate DataMatrix Images")
    st.markdown("Create DataMatrix barcode images for your UDI labels. **This step is optional** — skip to Step 2 for serial-only labels.")

    col1, col2 = st.columns([2, 1])

    with col1:
        base_data = st.text_area(
            "Base Data (UDI Information)",
            value="""(01)843041125857
(11)250602
(10)LTTI0625
(21)2506ZLD60XSW""",
            height=120,
            help="Enter the base UDI data. The serial number will be appended automatically."
        )

    with col2:
        start_num = st.number_input("Start Number", min_value=1, value=1, step=1)
        end_num = st.number_input("End Number", min_value=1, value=100, step=1)

        if start_num > end_num:
            st.error("Start number must be less than or equal to end number.")

    if st.button("🔨 Generate DataMatrix Images", type="primary", use_container_width=True):
        if start_num <= end_num:
            with st.spinner(f"Generating {end_num - start_num + 1} DataMatrix images..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                st.session_state.datamatrix_images = {}

                # Extract field (21) value for filename
                field_21_value = base_data.split('(21)')[-1].strip()

                total = end_num - start_num + 1

                # Reduce UI update frequency to avoid connection issues
                update_interval = max(1, total // 20)  # Update max 20 times total

                for i in range(start_num, end_num + 1):
                    # Create serial data
                    data = base_data + f'{i:04d}'

                    # Encode as DataMatrix
                    encoded = encode(data.encode('utf8'))

                    # Create image
                    img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

                    # Scale up 4x for better quality
                    new_size = (encoded.width * 4, encoded.height * 4)
                    img = img.resize(new_size, Image.Resampling.NEAREST)

                    # Save to memory
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG', dpi=(600, 600))
                    img_bytes.seek(0)

                    # Store with serial number as key
                    serial_number = f"{field_21_value}{i:04d}"
                    st.session_state.datamatrix_images[serial_number] = img_bytes.read()

                    # Update progress less frequently
                    current = i - start_num + 1
                    if current % update_interval == 0 or current == total:
                        progress = current / total
                        progress_bar.progress(progress)
                        status_text.text(f"Generating: {current}/{total}")

                progress_bar.empty()
                status_text.empty()

                st.success(f"✅ Generated {len(st.session_state.datamatrix_images)} DataMatrix images!")
                st.session_state.config['serial_prefix'] = field_21_value
                st.session_state.config['start_number'] = start_num
                st.session_state.config['end_number'] = end_num

    # Show status
    if st.session_state.datamatrix_images:
        st.info(f"📊 **Status:** {len(st.session_state.datamatrix_images)} DataMatrix images ready")

        # Preview first image
        with st.expander("🔍 Preview First DataMatrix"):
            first_key = list(st.session_state.datamatrix_images.keys())[0]
            img = Image.open(io.BytesIO(st.session_state.datamatrix_images[first_key]))
            st.image(img, caption=f"Serial: {first_key}", width=200)

        # Download all as ZIP
        if st.button("💾 Download DataMatrix Images (ZIP)"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for serial, img_data in st.session_state.datamatrix_images.items():
                    zip_file.writestr(f"datamatrix/{serial}.png", img_data)

            zip_buffer.seek(0)
            st.download_button(
                label="📥 Download ZIP",
                data=zip_buffer,
                file_name="datamatrix_images.zip",
                mime="application/zip"
            )

# ==================== TAB 2: Generate Labels ====================
with tab2:
    st.header("Step 2: Generate Label PNGs")
    st.markdown("Upload your SVG template and generate final labels. DataMatrix codes will be embedded if generated in Step 1.")

    # Mode indicator
    has_datamatrix = bool(st.session_state.datamatrix_images)
    if has_datamatrix:
        st.success(f"**DataMatrix mode** — {len(st.session_state.datamatrix_images)} DataMatrix images available from Step 1")
    else:
        st.info("**Serial Only mode** — No DataMatrix images generated. Labels will contain serial numbers only.")

    # Upload SVG template
    uploaded_svg = st.file_uploader(
        "Upload SVG Template",
        type=['svg'],
        help="Upload your label template SVG file. Use 'serial_number_text' as placeholder for serial numbers."
    )

    if uploaded_svg is not None:
        st.session_state.svg_template = uploaded_svg.read().decode('utf-8')
        st.success("✅ SVG template loaded")

        # Show SVG preview info
        with st.expander("📄 SVG Template Info"):
            st.code(st.session_state.svg_template[:500] + "...", language="xml")

    if st.session_state.svg_template:
        col1, col2 = st.columns(2)

        with col1:
            serial_prefix = st.text_input(
                "Serial Number Prefix",
                value=st.session_state.config['serial_prefix'],
                help="Prefix for serial numbers (extracted from DataMatrix generation if Step 1 was used)"
            )

            label_start_num = st.number_input(
                "Start Number", min_value=1,
                value=st.session_state.config['start_number'],
                step=1, key="label_start_num",
                help="Starting serial number for label generation"
            )
            label_end_num = st.number_input(
                "End Number", min_value=1,
                value=st.session_state.config['end_number'],
                step=1, key="label_end_num",
                help="Ending serial number for label generation"
            )

            if label_start_num > label_end_num:
                st.error("Start number must be less than or equal to end number.")

            if has_datamatrix:
                image_id = st.text_input(
                    "Primary Image ID (DataMatrix)",
                    value=st.session_state.config['image_id'],
                    help="The ID of the image element in your SVG where DataMatrix will be embedded"
                )
            else:
                image_id = st.session_state.config['image_id']

        with col2:
            export_dpi = st.selectbox(
                "PNG Export DPI",
                options=[300, 600, 1200],
                index=1,  # Default to 600 DPI
                help="Higher DPI = better quality but larger file size"
            )

            use_inkscape = st.checkbox(
                "Use Inkscape for PNG Export",
                value=True,
                help="Generates PNG files using Inkscape (recommended). Uncheck to generate SVG files only."
            )

            if use_inkscape:
                st.info("✅ Inkscape is installed and ready to use")

        st.markdown("---")

        if label_start_num <= label_end_num and st.button("🎨 Generate Label Images", type="primary", use_container_width=True):
            with st.spinner("Generating labels..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                st.session_state.label_pngs = {}

                # Build serial numbers from prefix + range
                serial_numbers = [f"{serial_prefix}{i:04d}" for i in range(label_start_num, label_end_num + 1)]
                total = len(serial_numbers)

                # Warn about missing DataMatrix images if in DataMatrix mode
                if has_datamatrix:
                    missing_dm = [s for s in serial_numbers if s not in st.session_state.datamatrix_images]
                    if missing_dm:
                        st.warning(f"⚠️ {len(missing_dm)} serial(s) in range have no DataMatrix image — those labels will get serial text only.")

                # Reduce UI update frequency to avoid connection issues
                update_interval = max(1, total // 20)  # Update max 20 times total

                for idx, serial_number in enumerate(serial_numbers):
                    # Parse SVG
                    root = ET.fromstring(st.session_state.svg_template)

                    # Replace serial_number_text with actual serial
                    for elem in root.iter():
                        if elem.text and "serial_number_text" in elem.text:
                            elem.text = elem.text.replace("serial_number_text", serial_number)

                    # Embed DataMatrix image only if available for this serial
                    if serial_number in st.session_state.datamatrix_images:
                        datamatrix_data = st.session_state.datamatrix_images[serial_number]
                        img_base64 = base64.b64encode(datamatrix_data).decode('utf-8')
                        href_val = f"data:image/png;base64,{img_base64}"

                        # Find and update image element
                        for image_elem in root.iter():
                            if image_elem.attrib.get("id") == image_id:
                                image_elem.attrib["{http://www.w3.org/1999/xlink}href"] = href_val
                                break

                    # Generate modified SVG
                    svg_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)

                    if use_inkscape:
                        # Try to export PNG with Inkscape
                        try:
                            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as temp_svg:
                                temp_svg.write(svg_bytes)
                                temp_svg_path = temp_svg.name

                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_png:
                                temp_png_path = temp_png.name

                            # Run Inkscape
                            result = subprocess.run([
                                "inkscape",
                                temp_svg_path,
                                "--export-type=png",
                                "--export-area-page",
                                f"--export-dpi={export_dpi}",
                                "--export-background=white",
                                "--export-background-opacity=1.0",
                                "--export-filename", temp_png_path
                            ], capture_output=True, timeout=30)

                            if result.returncode == 0 and os.path.exists(temp_png_path):
                                with open(temp_png_path, 'rb') as f:
                                    st.session_state.label_pngs[serial_number] = f.read()
                            else:
                                st.error(f"Inkscape export failed for {serial_number}")

                            # Cleanup
                            os.unlink(temp_svg_path)
                            if os.path.exists(temp_png_path):
                                os.unlink(temp_png_path)

                        except Exception as e:
                            st.error(f"Error with Inkscape: {str(e)}")
                            # Fallback to SVG
                            st.session_state.label_pngs[serial_number] = svg_bytes
                    else:
                        # Store SVG as-is (can be converted later or downloaded)
                        st.session_state.label_pngs[serial_number] = svg_bytes

                    # Update progress less frequently
                    current = idx + 1
                    if current % update_interval == 0 or current == total:
                        progress = current / total
                        progress_bar.progress(progress)
                        status_text.text(f"Generating: {current}/{total}")

                progress_bar.empty()
                status_text.empty()

                st.success(f"✅ Generated {len(st.session_state.label_pngs)} label files!")

    # Show status
    if st.session_state.label_pngs:
        st.info(f"📊 **Status:** {len(st.session_state.label_pngs)} label files ready")

        # Preview first label
        with st.expander("🔍 Preview First Label"):
            first_key = list(st.session_state.label_pngs.keys())[0]
            first_data = st.session_state.label_pngs[first_key]

            # Check if PNG or SVG
            if first_data.startswith(b'\x89PNG'):
                img = Image.open(io.BytesIO(first_data))
                st.image(img, caption=f"Serial: {first_key}", width=400)
            else:
                st.code(first_data.decode('utf-8')[:500] + "...", language="xml")

        # Download all as ZIP
        if st.button("💾 Download Label Files (ZIP)"):
            zip_buffer = io.BytesIO()
            extension = 'png' if st.session_state.label_pngs[first_key].startswith(b'\x89PNG') else 'svg'

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for serial, data in st.session_state.label_pngs.items():
                    zip_file.writestr(f"labels/label_{serial}.{extension}", data)

            zip_buffer.seek(0)
            st.download_button(
                label="📥 Download ZIP",
                data=zip_buffer,
                file_name=f"label_files.zip",
                mime="application/zip"
            )

# ==================== TAB 3: Verify Sequence ====================
with tab3:
    st.header("Step 3: Verify Sequence")
    st.markdown("Check that all serial numbers are in proper sequence with no gaps or duplicates.")

    if not st.session_state.label_pngs:
        st.warning("⚠️ Please generate labels first (Step 2)")
    else:
        if st.button("🔍 Verify Sequence", type="primary", use_container_width=True):
            serial_numbers = sorted(st.session_state.label_pngs.keys())

            # Extract numbers from serial strings
            numbers = []
            for serial in serial_numbers:
                match = re.search(r'(\d{4})$', serial)
                if match:
                    numbers.append(int(match.group(1)))

            numbers.sort()

            # Check for issues
            missing = []
            duplicates = []

            if len(numbers) > 1:
                expected = numbers[0]
                seen = set()

                for num in numbers:
                    if num in seen:
                        if num not in duplicates:
                            duplicates.append(num)
                    seen.add(num)

                    while expected < num:
                        missing.append(expected)
                        expected += 1
                    expected = num + 1

            # Display results
            if not missing and not duplicates:
                st.success("✅ **Verification Successful!**")
                st.success(f"Perfect sequence: {numbers[0]:04d} to {numbers[-1]:04d} ({len(numbers)} labels)")
            else:
                st.error("❌ **Sequence Issues Found!**")

                if duplicates:
                    st.error(f"**Duplicate numbers:** {', '.join([f'{n:04d}' for n in duplicates])}")

                if missing:
                    st.error(f"**Missing numbers:** {', '.join([f'{n:04d}' for n in missing[:20]])}")
                    if len(missing) > 20:
                        st.error(f"...and {len(missing) - 20} more")

# ==================== TAB 4: Create PDF ====================
with tab4:
    st.header("Step 4: Create PDF")
    st.markdown("Merge all labels into a single PDF file for easy printing and sharing.")

    if not st.session_state.label_pngs:
        st.warning("⚠️ Please generate labels first (Step 2)")
    else:
        # Check if we have PNGs
        first_data = list(st.session_state.label_pngs.values())[0]
        is_png = first_data.startswith(b'\x89PNG')

        if not is_png:
            st.error("❌ PDF generation requires PNG files. Please enable Inkscape export in Step 2.")
        else:
            # Get dimensions of first image to calculate default page size
            first_img = Image.open(io.BytesIO(first_data))
            # Assume 600 DPI for conversion to mm (1 inch = 25.4 mm)
            img_width_mm = round((first_img.width / 600) * 25.4, 1)
            img_height_mm = round((first_img.height / 600) * 25.4, 1)

            col1, col2 = st.columns(2)

            with col1:
                page_format = st.selectbox(
                    "Page Size",
                    ["Image Size", "A4", "Letter", "Custom"],
                    help="Select the page size for the PDF"
                )

                if page_format == "Custom":
                    custom_width = st.number_input("Width (mm)", value=210, min_value=50, max_value=500)
                    custom_height = st.number_input("Height (mm)", value=297, min_value=50, max_value=500)
                elif page_format == "Image Size":
                    st.info(f"📏 Image size: {img_width_mm} × {img_height_mm} mm")

            with col2:
                orientation = st.radio("Orientation", ["Portrait", "Landscape"])
                fit_to_page = st.checkbox("Fit images to page", value=True)

            if st.button("📄 Generate PDF", type="primary", use_container_width=True):
                with st.spinner("Creating PDF..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Determine page size
                    if page_format == "Image Size":
                        # Use actual image dimensions
                        pagesize = (img_width_mm * 2.83465, img_height_mm * 2.83465)
                    elif page_format == "A4":
                        pagesize = A4
                    elif page_format == "Letter":
                        pagesize = letter
                    else:
                        # Convert mm to points
                        pagesize = (custom_width * 2.83465, custom_height * 2.83465)

                    if orientation == "Landscape":
                        pagesize = (pagesize[1], pagesize[0])

                    # Create PDF
                    pdf_buffer = io.BytesIO()
                    writer = PdfWriter()

                    serial_numbers = sorted(st.session_state.label_pngs.keys())
                    total = len(serial_numbers)

                    temp_pdfs = []

                    # Reduce UI update frequency to avoid connection issues
                    update_interval = max(1, total // 20)  # Update max 20 times total

                    for idx, serial in enumerate(serial_numbers):
                        # Create temp PDF for this image
                        temp_pdf = io.BytesIO()
                        c = canvas.Canvas(temp_pdf, pagesize=pagesize)

                        # Load image
                        img_data = st.session_state.label_pngs[serial]
                        img = Image.open(io.BytesIO(img_data))

                        # Create ImageReader for reportlab
                        img_reader = ImageReader(io.BytesIO(img_data))

                        if fit_to_page:
                            # Calculate scaling
                            img_ratio = img.width / img.height
                            page_ratio = pagesize[0] / pagesize[1]

                            if img_ratio > page_ratio:
                                width = pagesize[0]
                                height = width / img_ratio
                            else:
                                height = pagesize[1]
                                width = height * img_ratio

                            x_pos = (pagesize[0] - width) / 2
                            y_pos = (pagesize[1] - height) / 2
                        else:
                            # Use original size (might overflow)
                            width, height = img.size
                            x_pos = (pagesize[0] - width) / 2
                            y_pos = (pagesize[1] - height) / 2

                        # Draw image
                        c.drawImage(img_reader, x_pos, y_pos, width=width, height=height)
                        c.save()

                        # Add to writer
                        temp_pdf.seek(0)
                        writer.append(temp_pdf)
                        temp_pdfs.append(temp_pdf)

                        # Update progress less frequently
                        current = idx + 1
                        if current % update_interval == 0 or current == total:
                            progress = current / total
                            progress_bar.progress(progress)
                            status_text.text(f"Processing: {current}/{total}")

                    # Write final PDF
                    writer.write(pdf_buffer)
                    writer.close()

                    pdf_buffer.seek(0)

                    progress_bar.empty()
                    status_text.empty()

                    # Generate filename based on serial range
                    first_serial = serial_numbers[0]
                    last_serial = serial_numbers[-1]

                    # Extract numeric part from serials
                    import re
                    first_num = re.search(r'(\d{4})$', first_serial)
                    last_num = re.search(r'(\d{4})$', last_serial)

                    if first_num and last_num:
                        # Get prefix (everything before the last 4 digits)
                        prefix = first_serial[:-4]
                        filename = f"{prefix}_{first_num.group(1)}-{last_num.group(1)}.pdf"
                    else:
                        filename = "udi_labels.pdf"

                    # Show file size
                    pdf_size_mb = len(pdf_buffer.getvalue()) / (1024 * 1024)

                    # Store in session state for later access
                    st.session_state.final_pdf = pdf_buffer.getvalue()
                    st.session_state.pdf_filename = filename
                    st.session_state.pdf_size_mb = pdf_size_mb

                    st.success(f"✅ PDF created with {total} pages!")

            # Show download/upload options if PDF exists (OUTSIDE the Generate PDF button)
            if 'final_pdf' in st.session_state and st.session_state.final_pdf:
                st.info(f"📄 Filename: `{st.session_state.pdf_filename}`")
                st.info(f"📊 PDF Size: {st.session_state.pdf_size_mb:.2f} MB")

                col_a, col_b = st.columns(2)

                with col_a:
                    # Download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=st.session_state.final_pdf,
                        file_name=st.session_state.pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

                with col_b:
                    # Upload button
                    if st.button("☁️ Upload & Get Share Link", type="secondary", use_container_width=True):
                        with st.spinner(f"📤 Uploading {st.session_state.pdf_filename} ({st.session_state.pdf_size_mb:.2f} MB) to filebin.net..."):
                            result = upload_to_filebin(
                                st.session_state.final_pdf,
                                st.session_state.pdf_filename,
                                st.session_state.pdf_size_mb
                            )
                            st.session_state.upload_result = result

            # Display upload results if they exist (outside the button to persist across reruns)
            if 'upload_result' in st.session_state and st.session_state.upload_result:
                result = st.session_state.upload_result

                if result['success']:
                    st.success("✅ Upload successful!")
                    st.markdown(f"""
                    ### 🔗 Shareable Links

                    **[📁 View All Files in Bin]({result['bin_url']})**

                    **[📄 Direct File Link]({result['file_url']})**

                    Copy link to share:
                    ```
                    {result['file_url']}
                    ```

                    📊 **File size:** {result['file_size_mb']:.2f} MB
                    🌐 **Service:** filebin.net (free, no registration)
                    ⏱️ **Available:** Until deleted (no automatic expiry mentioned)

                    💡 **Tip:** Share the link with anyone who needs the file. Click the bin link to manage your uploaded files.
                    """)

                    # Add a clear button to hide the results
                    if st.button("Clear Upload Results"):
                        del st.session_state.upload_result
                        st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit • [Documentation](https://github.com/)")

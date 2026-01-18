# Label Generation Suite

A collection of Python tools for generating labels with DataMatrix codes and converting images to PDFs.

## Components

### 1. DataMatrix Generator (`dataMatrix_gen.py`)
Generates DataMatrix barcode images with customizable serial numbers.

**Features:**
- Customizable base data format
- Range-based serial number generation
- Configurable output folder
- Progress tracking
- High-resolution output (600 DPI)

### 2. Inkscape Label Generator (`inkscape_script_optimized.py`)
Creates labels by combining SVG templates with DataMatrix images.

**Features:**
- SVG template support
- Customizable text elements
- DataMatrix image integration
- Secondary barcode image support
- Configurable serial number ranges
- Preview functionality
- Config file for saving settings
- Parallel processing optimization
- Support for both PNG and SVG output formats

### 3. File Sequence Verifier (`verify_labels.py`)
Validates that generated label files have correct sequential numbering.

**Features:**
- Batch file sequence validation
- Duplicate detection
- Missing file detection
- Sequential number verification
- Detailed error reporting

### 4. PNG to PDF Converter (`png_to_pdf.py`)
Converts PNG images to PDF format with customizable page settings.

**Features:**
- Multiple image selection
- Image size detection and preset
- Customizable page size
- Portrait/Landscape orientation
- Progress tracking
- Maintains image aspect ratio
- High-quality output

## Requirements

- Python 3.x
- Required Python packages:
  - tkinter
  - PIL (Pillow)
  - pylibdmtx
  - PyPDF2
  - reportlab
- Inkscape (for label generation)
- Notepad++ (optional, for SVG editing)

## Installation

1. Clone this repository
2. Install required Python packages:
```bash
pip install pillow pylibdmtx PyPDF2 reportlab
```
3. Install Inkscape from [inkscape.org](https://inkscape.org)

## Usage

### DataMatrix Generation
1. Run `dataMatrix_gen.py`
2. Enter the base data format
3. Set the start and end numbers
4. Choose output folder
5. Optional: Enable "Create 'Data_MatrixImages' subfolder"
6. Click "Generate DataMatrix Images"

### Label Generation
1. Run `inkscape_script_optimized.py`
2. Select SVG template file
3. Choose DataMatrix images folder
4. Configure element IDs and serial number range
5. Optional: Enable secondary barcode images
6. Select output format (PNG, SVG, or both)
7. Click "Generate Labels"

### File Sequence Verification
1. Run `verify_labels.py`
2. Click "Select Folder"
3. Choose folder containing generated label files
4. View verification results (checks for duplicates and missing files)

### PNG to PDF Conversion
1. Run `png_to_pdf.py`
2. Select PNG images
3. Configure page size and orientation
4. Click "Convert to PDF"

## Configuration

The label generator saves its configuration in `inkscape_label_gui_config.json`. This includes:
- SVG template path
- DataMatrix folder path
- Element IDs
- Serial number range
- Serial prefix

## Notes

- All tools feature progress tracking and error handling
- Generated images are saved at 600 DPI for high quality
- The label generator requires Inkscape for SVG processing
- Temporary files are automatically cleaned up after processing

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

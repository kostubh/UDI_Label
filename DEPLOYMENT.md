# UDI Label Generator - Web App Deployment Guide

## Overview
This is a web-based version of your Google Colab UDI label generator. It allows you to:
1. Generate DataMatrix barcode images
2. Create label PNGs/SVGs from templates
3. Verify sequence integrity
4. Merge everything into a single PDF

## Features
- ✅ No manual step-by-step execution needed
- ✅ Web-based interface accessible from anywhere
- ✅ Direct PDF download (no Google Drive needed)
- ✅ Handles large files (500MB-few GB)
- ✅ Free hosting options available

## Quick Start (Local Testing)

### Prerequisites
- Python 3.8 or higher
- (Optional) Inkscape - only if you want PNG exports

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd UDI_Label

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment Options

### Option 1: Streamlit Cloud (RECOMMENDED) ⭐

**Best for: 4-5 uses per month**

#### Pros:
- ✅ Completely free
- ✅ No credit card required
- ✅ Easy one-click deployment
- ✅ Automatic updates from GitHub
- ✅ Perfect for your usage pattern

#### Steps:
1. Push this code to GitHub (public or private repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub account
5. Select your repository and branch
6. Set main file path to `app.py`
7. Click "Deploy"

Done! Your app will be live at `https://your-app-name.streamlit.app`

#### Limitations:
- Apps sleep after inactivity (wake up in a few seconds on next visit)
- 1GB RAM limit (should be fine for your use case)
- Public apps are visible to anyone with the link

### Option 2: Hugging Face Spaces

**Best for: More resources needed**

#### Pros:
- ✅ Free tier with 16GB storage
- ✅ Good for larger file processing
- ✅ Nice UI/UX

#### Steps:
1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space (select "Streamlit" as SDK)
3. Upload your files or connect GitHub
4. Add `requirements.txt`
5. Space auto-deploys

Your app: `https://huggingface.co/spaces/your-username/your-space`

### Option 3: Google Cloud Run

**Best for: Need more control**

#### Pros:
- ✅ 2 million requests/month free (way more than you need!)
- ✅ Scalable
- ✅ Can handle very large files

#### Cons:
- ⚠️ More complex setup
- ⚠️ Requires credit card (but won't charge for your usage)

#### Quick Deploy:
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
EOF

# Deploy
gcloud run deploy udi-label-generator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Important Notes

### Inkscape (Optional)
The app can generate SVG files without any additional software. However, if you want PNG exports directly:

- **For local use:** Install [Inkscape](https://inkscape.org/release/) and make sure it's in your PATH
- **For cloud deployment:** Inkscape is NOT available on free tiers
  - **Workaround:** Generate SVG files, download them, and convert locally if needed
  - Or use a service with system package support

### File Storage
All files are stored in memory during the session:
- ✅ DataMatrix images
- ✅ Generated labels
- ✅ Final PDF

Once you download the PDF, you can close the browser. Files are temporary and automatically cleaned up.

### Large Files
For 500MB-few GB PDFs:
- Streamlit Cloud: Should work, but might be slow
- Hugging Face: Better performance
- Google Cloud Run: Best performance (but requires billing enabled)

For files larger than 1GB, consider:
1. Using Google Cloud Run with increased memory
2. Or generating the PDF in batches (multiple smaller PDFs)

## Usage Guide

### Step 1: Generate DataMatrix
1. Enter your base UDI data (01), (11), (10), (21) fields
2. Set start and end numbers for your serial range
3. Click "Generate DataMatrix Images"
4. Wait for completion (progress bar shows status)
5. Optional: Download DataMatrix images as ZIP

### Step 2: Generate Labels
1. Upload your SVG template file
   - Use `serial_number_text` as placeholder for serial numbers
   - Set image ID for DataMatrix placement (default: `image1`)
2. Click "Generate Label Images"
3. Labels will be created with embedded DataMatrix codes
4. Optional: Download all labels as ZIP

### Step 3: Verify Sequence
1. Click "Verify Sequence"
2. System checks for missing numbers or duplicates
3. Fix any issues by regenerating if needed

### Step 4: Create PDF
1. Select page size (A4, Letter, or Custom)
2. Choose orientation (Portrait/Landscape)
3. Click "Generate PDF"
4. Download your final PDF file

## Troubleshooting

### "Inkscape not found" error
- Solution: Either install Inkscape locally, or use SVG generation mode (no PNG export)

### PDF too large to download
- Solution: Use Google Cloud Run with more memory, or generate in smaller batches

### App crashes during PDF generation
- Cause: Out of memory
- Solution: Deploy to Hugging Face or Google Cloud Run for more resources

### DataMatrix images not showing in labels
- Check that your SVG template has correct image ID
- Verify the ID matches what you entered (case-sensitive)

## Cost Analysis

For **4-5 uses per month**:

| Service | Cost | Notes |
|---------|------|-------|
| Streamlit Cloud | $0/month | Perfect for your needs |
| Hugging Face | $0/month | Also great, more resources |
| Google Cloud Run | $0/month | Massive overkill (you'd use 0.0025% of free tier) |

All options are **completely free** for your usage pattern!

## Support

If you encounter issues:
1. Check the error message in the web interface
2. Review the Troubleshooting section above
3. For deployment issues, check provider's documentation
4. For code issues, check GitHub Issues

## Next Steps

1. Test locally first: `streamlit run app.py`
2. Deploy to Streamlit Cloud (easiest option)
3. Share the URL with your team
4. Enjoy automated label generation! 🎉

---

**Recommendation:** Start with Streamlit Cloud. It's the simplest, completely free, and perfect for 4-5 monthly uses!

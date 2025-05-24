import os
from pylibdmtx.pylibdmtx import encode, decode
from PIL import Image

# Create the folder if it doesn't exist
folder = 'Data_MatrixImages'
os.makedirs(folder, exist_ok=True)

# Base data including the (21) field
base_data = """(01)843041125857
(11)250602
(10)LTTI0625
(21)2506ZLD60XSW"""

# 2506ZLD60XSW0001-2506ZLD60XSW3000
# Jun 2, 2025

# Extract the value of field (21) from the base data
# Assuming the format is consistent, we split and take the (21) value
field_21_value = base_data.split('(21)')[-1].strip()

# Loop to create images with incremental changes
for i in range(1, 3051):
    # Update the changing part to be a four-digit number
    data = base_data + f'{i:04d}'
    
    # Encode the data
    encoded = encode(data.encode('utf8'))
    
    # Create an image from the encoded data
    img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    
    new_size = (encoded.width * 4, encoded.height * 4)  # Scale by 4x
    img = img.resize(new_size, Image.Resampling.NEAREST)  # Nearest neighbor for barcodes

    
    # Save the image with field (21) value and unique number
    img_path = os.path.join(folder, f'{field_21_value}{i:04d}.png')
    img.save(img_path,dpi=(600, 600))
    
    # Decode the saved image to verify (optional)
    decoded = decode(Image.open(img_path))
    
    # Print the decoded data for verification (optional)
    print(f'Decoded data for image {i}:', decoded)

print("DataMatrix images created successfully.")

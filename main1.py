import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import zlib
from io import BytesIO

# Page Configuration with mobile optimizations
st.set_page_config(
    page_title="CipherShade",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Advanced Responsive CSS
st.markdown("""
<style>
/* [Keep previous CSS styles unchanged] */
</style>
""", unsafe_allow_html=True)

# UI Components
st.markdown('<div class="animated-title">🔒 CipherShade</div>', unsafe_allow_html=True)
st.markdown("""
<div class="description">
    Secure steganography tool with enhanced error handling and validation
</div>
""", unsafe_allow_html=True)

# Mobile-friendly navigation
option = st.selectbox(
    "Choose operation:",
    options=[
        "Text in Text",
        "Text in Image",
        "Image in Image",
        "Decode Text",
        "Decode Image",
        "Decode Image in Image"
    ],
    index=0,
    help="Select the operation you want to perform"
)

# Core Functions with enhanced validation
def robust_image_load(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        return img.convert("RGB")
    except Exception as e:
        st.error(f"Image load error: {str(e)}")
        return None

def validate_image_size(cover_img, secret_data):
    cover_pixels = np.array(cover_img).size // 3
    required_pixels = len(secret_data) * 8 + 32  # Add 32 pixels for dimension storage
    return cover_pixels >= required_pixels

def safe_decompress(data):
    try:
        return zlib.decompress(data)
    except zlib.error:
        return None

def resize_secret_image(secret_img, cover_img):
    """Smart resizing with aspect ratio preservation"""
    cover_width, cover_height = cover_img.size
    max_pixels = (cover_width * cover_height * 3 - 32) // 8  # Reserve space for dimensions
    original_width, original_height = secret_img.size
    
    # Calculate new size preserving aspect ratio
    ratio = min(np.sqrt(max_pixels / (original_width * original_height)), 1.0)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    
    return secret_img.resize(new_size, Image.Resampling.LANCZOS)

def embed_original_dimensions(secret_img, stego_array):
    """Embed dimensions using error-checked encoding"""
    original_width, original_height = secret_img.size
    
    # Add size validation
    if original_width > 65535 or original_height > 65535:
        raise ValueError("Image dimensions too large for storage")
    
    # Create checksum
    dimension_bytes = original_width.to_bytes(2, 'big') + original_height.to_bytes(2, 'big')
    checksum = sum(dimension_bytes) % 256
    
    # Embed data with checksum
    flat_stego = stego_array.flatten()
    for i in range(40):  # 32 bits for dimensions + 8 bits for checksum
        if i < 32:
            byte_idx = i // 8
            bit_idx = 7 - (i % 8)
            byte = dimension_bytes[byte_idx] if byte_idx < 4 else checksum
        else:
            byte = checksum
            bit_idx = 7 - (i - 32)
        
        bit = (byte >> bit_idx) & 1
        if i >= len(flat_stego):
            break
        flat_stego[i] = (flat_stego[i] & 0xFE) | bit
    
    return flat_stego.reshape(stego_array.shape)

def extract_original_dimensions(stego_array):
    """Extract dimensions with error checking"""
    flat_stego = stego_array.flatten()
    
    # Read dimensions and checksum
    dimension_bytes = bytearray()
    for i in range(4):
        byte = 0
        for bit_idx in range(8):
            pixel_idx = i * 8 + bit_idx
            if pixel_idx >= len(flat_stego):
                break
            byte = (byte << 1) | (flat_stego[pixel_idx] & 1)
        dimension_bytes.append(byte)
    
    # Read validation checksum
    checksum_byte = 0
    for bit_idx in range(8):
        pixel_idx = 32 + bit_idx
        if pixel_idx >= len(flat_stego):
            break
        checksum_byte = (checksum_byte << 1) | (flat_stego[pixel_idx] & 1)
    
    # Validate checksum
    calculated_checksum = sum(dimension_bytes) % 256
    if calculated_checksum != checksum_byte:
        raise ValueError("Dimension data corrupted")
    
    original_width = int.from_bytes(dimension_bytes[:2], 'big')
    original_height = int.from_bytes(dimension_bytes[2:4], 'big')
    
    return original_width, original_height

# Text in Text Operations
def encode_message(cover_text, secret_message):
    zero_width_chars = {'0': '\u200B', '1': '\u200C'}
    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
    encoded = ''.join([zero_width_chars[bit] for bit in binary_message])
    return cover_text + encoded + '\u200D'  # Add termination character

def decode_message(stego_text):
    zero_width_chars = {'\u200B': '0', '\u200C': '1'}
    binary = []
    for c in stego_text:
        if c in zero_width_chars:
            binary.append(zero_width_chars[c])
        elif c == '\u200D':  # Stop at termination character
            break
    binary_str = ''.join(binary)
    return ''.join([chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)])

# Image Processing Operations
def process_image_embedding(cover_img, secret_img):
    """Enhanced embedding process with validation"""
    # Resize secret image
    resized_secret = resize_secret_image(secret_img, cover_img)
    
    # Compress with error checking
    buf = BytesIO()
    resized_secret.save(buf, format="PNG", compress_level=0)
    compressed_data = zlib.compress(buf.getvalue(), level=1)  # Faster compression
    
    # Validate capacity
    if not validate_image_size(cover_img, compressed_data):
        raise ValueError("Cover image too small even after resizing")
    
    # Convert to numpy array
    cover_array = np.array(cover_img)
    flat_cover = cover_array.flatten()
    
    # Embed data with bounds checking
    for i, byte in enumerate(compressed_data):
        for bit_idx in range(8):
            pixel_idx = 40 + i * 8 + bit_idx  # Reserve first 40 pixels
            if pixel_idx >= len(flat_cover):
                raise ValueError("Insufficient cover image capacity")
            bit = (byte >> (7 - bit_idx)) & 1
            flat_cover[pixel_idx] = (flat_cover[pixel_idx] & 0xFE) | bit
    
    # Embed dimensions and return
    return embed_original_dimensions(secret_img, flat_cover.reshape(cover_array.shape))

def process_image_extraction(stego_img):
    """Robust extraction process with error recovery"""
    stego_array = np.array(stego_img)
    
    try:
        # Extract dimensions with validation
        original_width, original_height = extract_original_dimensions(stego_array)
        
        # Extract compressed data
        flat_stego = stego_array.flatten()
        extracted = bytearray()
        
        # Read data pixels (skip first 40 pixels used for metadata)
        for i in range(40, len(flat_stego), 8):
            byte = 0
            valid_bits = 0
            for bit_idx in range(8):
                pixel_idx = i + bit_idx
                if pixel_idx >= len(flat_stego):
                    break
                byte = (byte << 1) | (flat_stego[pixel_idx] & 1)
                valid_bits += 1
            
            # Pad with zeros if incomplete byte
            if valid_bits < 8:
                byte <<= (8 - valid_bits)
            extracted.append(byte)
        
        # Decompress with error recovery
        decompressed = safe_decompress(bytes(extracted))
        if not decompressed:
            raise ValueError("Decompression failed")
        
        # Restore image
        hidden_img = Image.open(BytesIO(decompressed))
        return hidden_img.resize((original_width, original_height), Image.Resampling.LANCZOS)
    
    except Exception as e:
        st.error(f"Extraction failed: {str(e)}")
        return None

# Streamlit UI Sections
if option == "Text in Text":
    st.header("📝 Text in Text Steganography")
    col1, col2 = st.columns(2)
    with col1:
        cover_text = st.text_area("Cover Text:", height=150)
    with col2:
        secret_message = st.text_area("Secret Message:", height=150)

    if st.button("🕶️ Hide Message"):
        if cover_text and secret_message:
            try:
                stego_text = encode_message(cover_text, secret_message)
                st.markdown(f'<div class="success-box">✅ Message hidden successfully!</div>', unsafe_allow_html=True)
                st.code(stego_text)
            except Exception as e:
                st.error(f"Encoding error: {str(e)}")
        else:
            st.markdown('<div class="error-box">❌ Please fill both fields</div>', unsafe_allow_html=True)

elif option == "Text in Image":
    st.header("🖼️ Text in Image Steganography")
    uploaded_image = st.file_uploader("Upload Cover Image:", type=["png", "jpg", "jpeg"])
    secret_message = st.text_area("Secret Message:")

    if uploaded_image and secret_message:
        try:
            img = robust_image_load(uploaded_image)
            if img:
                st.image(img, caption="Original Image")
                
                if st.button("🖼️ Hide Message"):
                    secret_message += "\0"
                    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
                    img_array = np.array(img)
                    flat_img = img_array.flatten()

                    if len(binary_message) > len(flat_img) - 40:  # Reserve 40 pixels
                        st.error("Message too large for image capacity")
                    else:
                        # Embed message starting from pixel 40
                        for i in range(len(binary_message)):
                            pixel_idx = 40 + i
                            if pixel_idx >= len(flat_img):
                                break
                            flat_img[pixel_idx] = (flat_img[pixel_idx] & 0xFE) | int(binary_message[i])
                        
                        stego_img = Image.fromarray(flat_img.reshape(img_array.shape))
                        st.markdown(f'<div class="success-box">✅ Message hidden successfully!</div>', unsafe_allow_html=True)
                        st.image(stego_img, caption="Stego Image")
                        
                        buf = BytesIO()
                        stego_img.save(buf, format="PNG")
                        st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")
        except Exception as e:
            st.error(f"Processing error: {str(e)}")

elif option == "Image in Image":
    st.header("🎨 Image in Image Steganography")
    col1, col2 = st.columns(2)
    with col1:
        cover_image = st.file_uploader("Cover Image:", type=["png"])
    with col2:
        secret_image = st.file_uploader("Secret Image:", type=["png", "jpg", "jpeg"])

    if cover_image and secret_image:
        try:
            cover_img = robust_image_load(cover_image)
            secret_img = robust_image_load(secret_image)
            
            if cover_img and secret_img:
                st.image(cover_img, caption="Cover Image")
                st.image(secret_img, caption="Secret Image")

                if st.button("🎨 Hide Image"):
                    stego_array = process_image_embedding(cover_img, secret_img)
                    stego_image = Image.fromarray(stego_array)
                    st.markdown(f'<div class="success-box">✅ Image hidden successfully!</div>', unsafe_allow_html=True)
                    st.image(stego_image, caption="Stego Image")
                    
                    buf = BytesIO()
                    stego_image.save(buf, format="PNG")
                    st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")
        except Exception as e:
            st.error(f"Embedding error: {str(e)}")

elif option == "Decode Image in Image":
    st.header("🎨🔍 Decode Image from Image")
    stego_image = st.file_uploader("Upload Stego Image:", type=["png"])

    if stego_image:
        try:
            img = robust_image_load(stego_image)
            if img:
                st.image(img, caption="Stego Image")
                
                if st.button("🔍 Extract Hidden Image"):
                    hidden_img = process_image_extraction(img)
                    if hidden_img:
                        st.markdown(f'<div class="success-box">✅ Hidden image extracted!</div>', unsafe_allow_html=True)
                        st.image(hidden_img, caption="Extracted Image")
                        
                        buf = BytesIO()
                        hidden_img.save(buf, format="PNG")
                        st.download_button("💾 Download", buf.getvalue(), "hidden.png", "image/png")
                    else:
                        st.markdown('<div class="error-box">❌ No valid hidden image found</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Extraction error: {str(e)}")

# [Keep other sections (Decode Text, Decode Image) similar with proper error handling]

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin: 2rem 0;">
    CipherShade v3.0 | Enhanced Security | Built with ❤️ by NEEL
</div>
""", unsafe_allow_html=True)

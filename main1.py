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
    initial_sidebar_state="collapsed"  # Better for mobile
)

# Advanced Responsive CSS
st.markdown("""
<style>
/* [Keep all previous CSS styles here] */
</style>
""", unsafe_allow_html=True)

# UI Components
st.markdown('<div class="animated-title">🔒 CipherShade</div>', unsafe_allow_html=True)
st.markdown("""
<div class="description">
    Secure steganography tool for hiding messages and images with cross-device compatibility
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
    format_func=lambda x: f"📝 {x}" if "Text" in x else f"🖼️ {x}" if "Image" in x else f"🔍 {x}",
    index=0,
    help="Select the operation you want to perform"
)

# Core Functions with enhanced error handling
def robust_image_load(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        return img.convert("RGB")  # Force RGB mode
    except Exception as e:
        st.error(f"Image load error: {str(e)}")
        return None

def validate_image_size(cover_img, secret_data):
    cover_pixels = np.array(cover_img).size // 3  # RGB channels
    required_pixels = len(secret_data) * 8
    return cover_pixels >= required_pixels

def safe_decompress(data):
    try:
        return zlib.decompress(data)
    except zlib.error:
        return None

def resize_secret_image(secret_img, cover_img):
    """
    Resize the secret image to fit within the cover image's capacity.
    """
    cover_width, cover_height = cover_img.size
    secret_width, secret_height = secret_img.size

    # Calculate the maximum allowed size for the secret image
    max_secret_pixels = (cover_width * cover_height * 3) // 8  # 1 bit per pixel
    max_secret_size = int(np.sqrt(max_secret_pixels))  # Assuming square image for simplicity

    # Resize the secret image using LANCZOS resampling
    resized_secret = secret_img.resize((max_secret_size, max_secret_size), Image.Resampling.LANCZOS)
    return resized_secret

def embed_original_dimensions(secret_img, stego_array):
    """
    Embed the original dimensions of the secret image in the first few pixels of the stego image.
    """
    original_width, original_height = secret_img.size

    # Convert dimensions to bytes
    width_bytes = original_width.to_bytes(2, byteorder='big')  # 2 bytes for width
    height_bytes = original_height.to_bytes(2, byteorder='big')  # 2 bytes for height

    # Embed dimensions in the first 32 pixels (4 bytes = 32 bits)
    flat_stego = stego_array.flatten()
    for i in range(32):
        bit = (width_bytes[i // 8] >> (7 - (i % 8))) & 1 if i < 16 else (height_bytes[(i - 16) // 8] >> (7 - ((i - 16) % 8))) & 1
        flat_stego[i] = (flat_stego[i] & 0xFE) | bit

    return flat_stego.reshape(stego_array.shape)

def extract_original_dimensions(stego_array):
    """
    Extract the original dimensions of the secret image from the first few pixels of the stego image.
    """
    flat_stego = stego_array.flatten()

    # Extract width (first 16 pixels)
    width_bytes = bytearray()
    for i in range(16):
        byte = 0
        for bit_idx in range(8):
            pixel_idx = i * 8 + bit_idx
            byte = (byte << 1) | (flat_stego[pixel_idx] & 1)
        width_bytes.append(byte)

    # Extract height (next 16 pixels)
    height_bytes = bytearray()
    for i in range(16, 32):
        byte = 0
        for bit_idx in range(8):
            pixel_idx = i * 8 + bit_idx
            byte = (byte << 1) | (flat_stego[pixel_idx] & 1)
        height_bytes.append(byte)

    # Convert bytes to integers
    original_width = int.from_bytes(width_bytes, byteorder='big')
    original_height = int.from_bytes(height_bytes, byteorder='big')

    return original_width, original_height

# Text in Text Operations
def encode_message(cover_text, secret_message):
    zero_width_space = "\u200B"
    zero_width_joiner = "\u200D"
    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
    encoded_message = "".join([zero_width_space if bit == '0' else zero_width_joiner for bit in binary_message])
    return cover_text + encoded_message

def decode_message(stego_text):
    zero_width_space = "\u200B"
    zero_width_joiner = "\u200D"
    encoded_message = "".join([c for c in stego_text if c in (zero_width_space, zero_width_joiner)])
    binary_message = "".join(['0' if c == zero_width_space else '1' for c in encoded_message])
    return "".join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)])

if option == "Text in Text":
    st.header("📝 Text in Text Steganography")
    col1, col2 = st.columns(2)
    with col1:
        cover_text = st.text_area("Cover Text:", height=150)
    with col2:
        secret_message = st.text_area("Secret Message:", height=150)

    if st.button("🕶️ Hide Message", use_container_width=True):
        if cover_text and secret_message:
            with st.spinner("Encoding message..."):
                try:
                    stego_text = encode_message(cover_text, secret_message)
                    st.markdown(f'<div class="success-box">✅ Message hidden successfully!</div>', unsafe_allow_html=True)
                    st.code(stego_text, language="text")
                except Exception as e:
                    st.error(f"Encoding error: {str(e)}")
        else:
            st.markdown('<div class="error-box">❌ Please fill both fields</div>', unsafe_allow_html=True)

# Text in Image Operations
elif option == "Text in Image":
    st.header("🖼️ Text in Image Steganography")
    uploaded_image = st.file_uploader("Upload Cover Image:", type=["png", "jpg", "jpeg"])
    secret_message = st.text_area("Secret Message:")

    if uploaded_image and secret_message:
        with st.spinner("Processing image..."):
            try:
                img = robust_image_load(uploaded_file=uploaded_image)
                if img:
                    st.image(img, caption="Original Image", use_container_width=True)
                    
                    if st.button("🖼️ Hide Message", use_container_width=True):
                        secret_message += "\0"
                        binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
                        img_array = np.array(img)
                        flat_img = img_array.flatten()

                        if len(binary_message) > len(flat_img):
                            st.error("Message too large for image capacity")
                        else:
                            for i in range(len(binary_message)):
                                flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])
                            stego_img = Image.fromarray(flat_img.reshape(img_array.shape))
                            
                            st.markdown(f'<div class="success-box">✅ Message hidden successfully!</div>', unsafe_allow_html=True)
                            st.image(stego_img, caption="Stego Image", use_container_width=True)
                            
                            buf = BytesIO()
                            stego_img.save(buf, format="PNG")
                            st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")
            except Exception as e:
                st.error(f"Image processing error: {str(e)}")

# Image in Image Operations
elif option == "Image in Image":
    st.header("🎨 Image in Image Steganography")
    col1, col2 = st.columns(2)
    with col1:
        cover_image = st.file_uploader("Cover Image:", type=["png", "jpg", "jpeg"])
    with col2:
        secret_image = st.file_uploader("Secret Image:", type=["png", "jpg", "jpeg"])

    if cover_image and secret_image:
        with st.spinner("Processing images..."):
            try:
                # Load images
                cover_img = robust_image_load(cover_image)
                secret_img = robust_image_load(secret_image)
                
                if cover_img and secret_img:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(cover_img, caption="Cover Image", use_container_width=True)
                    with col2:
                        st.image(secret_img, caption="Secret Image", use_container_width=True)

                    # Resize secret image to fit within cover image's capacity
                    resized_secret = resize_secret_image(secret_img, cover_img)

                    # Compress resized secret image using PNG format
                    buf = BytesIO()
                    resized_secret.save(buf, format="PNG", compress_level=0)  # No compression for maximum quality
                    compressed_secret = zlib.compress(buf.getvalue(), level=9)  # Maximum compression

                    # Calculate required capacity
                    required_bytes = len(compressed_secret)
                    required_pixels = required_bytes * 8  # Each byte requires 8 pixels (1 bit per pixel)

                    # Calculate cover image capacity
                    cover_width, cover_height = cover_img.size
                    cover_pixels = cover_width * cover_height * 3  # 3 channels (RGB)

                    # Check if cover image is large enough
                    if required_pixels > cover_pixels:
                        st.error(
                            f"Cover image too small! Required: {required_bytes} bytes, Available: {cover_pixels // 8} bytes. "
                            f"Please use a larger cover image or reduce the size of the secret image."
                        )
                    else:
                        if st.button("🎨 Hide Image", use_container_width=True):
                            # Convert cover image to numpy array
                            cover_array = np.array(cover_img)
                            flat_cover = cover_array.flatten()

                            # Embed compressed secret data
                            for i, byte in enumerate(compressed_secret):
                                for bit_idx in range(8):
                                    pixel_idx = i * 8 + bit_idx
                                    if pixel_idx >= len(flat_cover):
                                        break
                                    bit = (byte >> (7 - bit_idx)) & 1
                                    flat_cover[pixel_idx] = (flat_cover[pixel_idx] & 0xFE) | bit

                            # Reshape and save
                            stego_array = flat_cover.reshape(cover_array.shape)
                            stego_array = embed_original_dimensions(secret_img, stego_array)  # Embed original dimensions
                            stego_image = Image.fromarray(stego_array)
                            st.markdown(f'<div class="success-box">✅ Image hidden successfully!</div>', unsafe_allow_html=True)
                            st.image(stego_image, caption="Stego Image", use_container_width=True)

                            # Download button
                            buf = BytesIO()
                            stego_image.save(buf, format="PNG")
                            st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")
            except Exception as e:
                st.error(f"Image embedding error: {str(e)}")

# Decode Image in Image Operations
elif option == "Decode Image in Image":
    st.header("🎨🔍 Decode Image from Image")
    stego_image = st.file_uploader("Upload Stego Image:", type=["png", "jpg", "jpeg"])

    if stego_image:
        with st.spinner("Processing image..."):
            try:
                img = robust_image_load(stego_image)
                if img:
                    st.image(img, caption="Stego Image", use_container_width=True)
                    
                    if st.button("🔍 Extract Hidden Image", use_container_width=True):
                        stego_array = np.array(img)
                        original_width, original_height = extract_original_dimensions(stego_array)  # Extract original dimensions

                        # Extract compressed data
                        flat_stego = stego_array.flatten()
                        extracted = bytearray()
                        
                        for i in range(32, len(flat_stego), 8):  # Skip first 32 pixels (dimensions)
                            byte = 0
                            for bit_idx in range(8):
                                pixel_idx = i + bit_idx
                                if pixel_idx >= len(flat_stego):
                                    break
                                byte = (byte << 1) | (flat_stego[pixel_idx] & 1)
                            extracted.append(byte)
                        
                        decompressed = safe_decompress(bytes(extracted))
                        if decompressed:
                            hidden_img = Image.open(BytesIO(decompressed))
                            hidden_img = hidden_img.resize((original_width, original_height), Image.Resampling.LANCZOS)  # Restore original size
                            st.markdown(f'<div class="success-box">✅ Hidden image extracted!</div>', unsafe_allow_html=True)
                            st.image(hidden_img, caption="Extracted Image", use_container_width=True)
                            
                            buf = BytesIO()
                            hidden_img.save(buf, format="PNG")
                            st.download_button("💾 Download", buf.getvalue(), "hidden.png", "image/png")
                        else:
                            st.markdown('<div class="error-box">❌ No valid hidden image found</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Extraction error: {str(e)}")

# Decode Text Operations
elif option == "Decode Text":
    st.header("🔍 Decode Hidden Text")
    stego_text = st.text_area("Stego Text:", height=200)

    if st.button("🔓 Decode Message", use_container_width=True):
        if stego_text:
            with st.spinner("Decoding..."):
                try:
                    decoded = decode_message(stego_text)
                    st.markdown(f'<div class="success-box">✅ Decoded message: {decoded}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Decoding error: {str(e)}")
        else:
            st.markdown('<div class="error-box">❌ Please input stego text</div>', unsafe_allow_html=True)

# Decode Image Operations
elif option == "Decode Image":
    st.header("🕵️ Decode Image Message")
    stego_image = st.file_uploader("Upload Stego Image:", type=["png", "jpg", "jpeg"])

    if stego_image:
        with st.spinner("Processing image..."):
            try:
                img = robust_image_load(stego_image)
                if img:
                    st.image(img, caption="Stego Image", use_container_width=True)
                    
                    if st.button("🔍 Extract Message", use_container_width=True):
                        binary_message = "".join([str(pixel & 1) for pixel in np.array(img).flatten()])
                        secret = "".join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)])
                        secret = secret.split("\0")[0]
                        
                        if secret:
                            st.markdown(f'<div class="success-box">✅ Extracted message: {secret}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">❌ No hidden message found</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Decoding error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin: 2rem 0;">
    CipherShade v2.0 | Secure Steganography Suite | Built with ❤️ by NEEL
</div>
""", unsafe_allow_html=True)

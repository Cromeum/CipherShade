import streamlit as st
import numpy as np
from PIL import Image
import io
import struct
import zlib

# Page Configuration
st.set_page_config(page_title="CipherShade", page_icon="🔒", layout="wide")

# Custom CSS for Responsive Design
st.markdown("""
<style>
/* Responsive Design */
@media (max-width: 768px) {
    .stTextArea textarea, .stTextInput input {
        font-size: 16px !important;
    }
    .stButton button {
        width: 100% !important;
        font-size: 16px !important;
    }
    .stSelectbox select {
        font-size: 16px !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 24px !important;
    }
    .stMarkdown p, .stMarkdown div {
        font-size: 16px !important;
    }
    .stImage img {
        max-width: 100% !important;
        height: auto !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Animated Title with Typing Effect
st.markdown('<div class="animated-title">🔒 CipherShade</div>', unsafe_allow_html=True)

# Description
st.markdown("""
<div class="description">
    Welcome to <strong>CipherShade</strong>! Hide text in text, hide text in images, or even hide images in images.
    This app also includes decoding functionality to extract hidden messages.
</div>
""", unsafe_allow_html=True)

# Mobile-Friendly Navigation
option = st.sidebar.selectbox(
    "Choose a Steganography Method:",
    options=[
        "Text in Text",
        "Text in Image",
        "Image in Image",
        "Decode Text",
        "Decode Image",
        "Decode Image in Image"
    ],
    format_func=lambda x: f"📝 {x}" if x == "Text in Text" else
    f"🖼️ {x}" if x == "Text in Image" else
    f"🎨 {x}" if x == "Image in Image" else
    f"🔍 {x}" if x == "Decode Text" else
    f"🕵️ {x}" if x == "Decode Image" else
    f"🎨🔍 {x}"
)

# Functions
def encode_message(cover_text, secret_message):
    zero_width_space = "\u200B"
    zero_width_joiner = "\u200D"
    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
    encoded_message = ""
    for bit in binary_message:
        encoded_message += zero_width_space if bit == '0' else zero_width_joiner
    return cover_text + encoded_message

def decode_message(stego_text):
    zero_width_space = "\u200B"
    zero_width_joiner = "\u200D"
    encoded_message = "".join([c for c in stego_text if c in (zero_width_space, zero_width_joiner)])
    binary_message = "".join(['0' if c == zero_width_space else '1' for c in encoded_message])
    return "".join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)])

def extract_message_from_image(stego_image):
    img_array = np.array(stego_image)
    flat_img = img_array.flatten()
    binary_message = "".join([str(pixel & 1) for pixel in flat_img])
    secret_message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        if byte:
            try:
                char = chr(int(byte, 2))
                if char == "\0":
                    break
                secret_message += char
            except ValueError:
                pass
    return secret_message

# Text in Text Section
if option == "Text in Text":
    st.header("📝 Text in Text Steganography")
    cover_text = st.text_area("Cover Text:", help="Enter the text that will hide your secret message", height=150)
    secret_message = st.text_input("Secret Message:", help="Message you want to hide")

    if st.button("🕶️ Hide Message"):
        if cover_text and secret_message:
            stego_text = encode_message(cover_text, secret_message)
            st.success("Message hidden successfully!")
            st.text_area("Stego Text (Visible Part):", cover_text, height=150)
            st.code(stego_text)
        else:
            st.error("Please fill both fields")

# Text in Image Section
elif option == "Text in Image":
    st.header("🖼️ Text in Image Steganography")
    uploaded_image = st.file_uploader("Upload Cover Image:", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    secret_message = st.text_input("Secret Message:")

    if uploaded_image and secret_message:
        image = Image.open(uploaded_image)
        st.image(image, caption="Cover Image", use_container_width=True)

        if st.button("🖼️ Hide Message"):
            secret_message += "\0"
            img_array = np.array(image)
            flat_img = img_array.flatten()
            binary_message = ''.join(format(ord(char), '08b') for char in secret_message)

            if len(binary_message) > len(flat_img):
                st.error("Message too large for image! Use a larger cover image.")
            else:
                for i in range(len(binary_message)):
                    flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])
                stego_image = Image.fromarray(flat_img.reshape(img_array.shape))
                st.success("Message hidden successfully!")
                st.image(stego_image, caption="Stego Image", use_container_width=True)

                buf = io.BytesIO()
                stego_image.save(buf, format="PNG")
                st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")

# Image in Image Section (Final Fix)
elif option == "Image in Image":
    st.header("🎨 Image in Image Steganography")
    cover_image = st.file_uploader("Cover Image:", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    secret_image = st.file_uploader("Secret Image:", type=["png", "jpg", "jpeg", "bmp", "tiff"])

    if cover_image and secret_image:
        cover_img = Image.open(cover_image).convert("RGB")
        secret_img = Image.open(secret_image).convert("RGB")

        # Compress secret image data using lossless PNG
        buf = io.BytesIO()
        secret_img.save(buf, format="PNG", compress_level=0)  # No compression for maximum quality
        secret_data = buf.getvalue()
        compressed_secret = zlib.compress(secret_data, level=0)  # No compression for maximum quality

        # Calculate required capacity
        required_bytes = len(compressed_secret)
        required_pixels = required_bytes * 8

        # Calculate cover image capacity
        cover_width, cover_height = cover_img.size
        cover_pixels = cover_width * cover_height * 3  # 3 channels (RGB)

        if required_pixels > cover_pixels:
            st.error(
                f"Cover image too small! Required: {required_pixels // 8} bytes, Available: {cover_pixels // 8} bytes.")
        else:
            st.image(cover_img, caption="Cover Image", use_container_width=True)
            st.image(secret_img, caption="Secret Image", use_container_width=True)

            if st.button("🎨 Hide Image"):
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
                stego_image = Image.fromarray(stego_array)
                st.success("Image hidden successfully!")
                st.image(stego_image, caption="Stego Image", use_container_width=True)

                buf = io.BytesIO()
                stego_image.save(buf, format="PNG")
                st.download_button("💾 Download", buf.getvalue(), "stego.png", "image/png")

# Decode Image in Image Section (Final Fix)
elif option == "Decode Image in Image":
    st.header("🎨🔍 Decode Image from Image")
    st.write("Extract a hidden image from a stego image.")

    stego_image_upload = st.file_uploader("Upload Stego Image:", type=["png", "jpg", "jpeg", "bmp", "tiff"])

    if stego_image_upload:
        stego_image = Image.open(stego_image_upload).convert("RGB")
        st.image(stego_image, caption="Stego Image", use_container_width=True)

        if st.button("🔍 Extract Hidden Image"):
            # Extract LSBs from stego image
            stego_array = np.array(stego_image)
            flat_stego = stego_array.flatten()

            # Extract compressed data
            extracted_data = bytearray()
            for i in range(0, len(flat_stego), 8):
                byte = 0
                for bit_idx in range(8):
                    pixel_idx = i + bit_idx
                    if pixel_idx >= len(flat_stego):
                        break
                    bit = flat_stego[pixel_idx] & 1
                    byte = (byte << 1) | bit
                extracted_data.append(byte)

            try:
                # Decompress and load image
                decompressed_data = zlib.decompress(bytes(extracted_data))
                hidden_image = Image.open(io.BytesIO(decompressed_data))
                st.success("Hidden image extracted successfully!")
                st.image(hidden_image, caption="Extracted Hidden Image", use_container_width=True)

                # Download
                buf = io.BytesIO()
                hidden_image.save(buf, format="PNG")
                st.download_button("💾 Download", buf.getvalue(), "hidden.png", "image/png")
            except Exception as e:
                st.error("Failed to extract hidden image. Ensure you used the correct stego image.")

# Decode Text Section
elif option == "Decode Text":
    st.header("🔍 Decode Text Message")
    stego_text = st.text_area("Stego Text:", height=200)

    if st.button("🔓 Decode"):
        if stego_text:
            decoded = decode_message(stego_text)
            st.success(f"Decoded Message: {decoded}")
        else:
            st.error("Please enter stego text")

# Decode Image Section
elif option == "Decode Image":
    st.header("🕵️ Decode Image Message")
    stego_image = st.file_uploader("Upload Stego Image:", type=["png", "jpg", "jpeg", "bmp", "tiff"])

    if stego_image:
        image = Image.open(stego_image)
        st.image(image, caption="Stego Image", use_container_width=True)

        if st.button("🔍 Extract"):
            secret = extract_message_from_image(image)
            if secret:
                st.success(f"Extracted Message: {secret}")
            else:
                st.error("No hidden message found")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Created with ❤️ by NEEL
</div>
""", unsafe_allow_html=True)

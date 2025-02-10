import streamlit as st
import numpy as np
from PIL import Image
import io

# Page Configuration
st.set_page_config(page_title="CipherShade", page_icon="🔒", layout="wide")

# Custom CSS for Enhanced UI
st.markdown("""
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Roboto+Mono:wght@400;600&display=swap');

/* Default Light Mode */
body {
    font-family: 'Poppins', sans-serif;
    background-color: #f5f5f5;
    color: #333333;
}

/* Title Typing Animation */
@keyframes typing {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes blink-caret {
    from, to { border-color: transparent; }
    50% { border-color: #ff7e5f; }
}

.animated-title {
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    font-family: 'Roboto Mono', monospace;
    overflow: hidden; /* Ensures the text is hidden until typed */
    white-space: nowrap; /* Keeps the text on a single line */
    margin: 0 auto; /* Centers the title */
    letter-spacing: 0.15em; /* Adjust spacing for typing effect */
    animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
    border-right: 0.15em solid #ff7e5f; /* Cursor effect */
}

/* Description Styling */
.description {
    font-size: 18px;
    text-align: center;
    color: #555555;
    margin-bottom: 40px;
}

/* Sidebar Styling */
.sidebar .sidebar-content {
    background: linear-gradient(145deg, #1e3c72, #2a5298);
    color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    font-family: 'Poppins', sans-serif;
}

/* Navigation Options Styling */
.sidebar .stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.sidebar .stRadio label {
    display: flex;
    align-items: center;
    padding: 10px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.1);
    transition: background 0.3s ease, transform 0.3s ease;
    cursor: pointer;
}

.sidebar .stRadio label:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateX(5px);
}

.sidebar .stRadio label div {
    margin-left: 10px;
}

/* Icon Styling */
.sidebar .stRadio label i {
    font-size: 18px;
    margin-right: 10px;
    transition: transform 0.3s ease;
}

.sidebar .stRadio label:hover i {
    transform: rotate(10deg);
}

/* Divider Styling */
.sidebar hr {
    border: 0;
    height: 1px;
    background: rgba(255, 255, 255, 0.2);
    margin: 15px 0;
}

/* Footer Styling */
.sidebar .footer {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
}

/* Button Styling */
.stButton button {
    background: linear-gradient(145deg, #1e3c72, #2a5298);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

/* Input Field Styling */
.stTextArea textarea, .stTextInput input {
    border: 1px solid #cccccc;
    border-radius: 5px;
    padding: 10px;
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
}

/* File Uploader Styling */
.stFileUploader label {
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
}

/* Success and Error Messages */
.stSuccess {
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    color: #28a745;
}

.stError {
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    color: #dc3545;
}

/* Image Styling */
.stImage img {
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.stImage img:hover {
    transform: scale(1.02);
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

# Sidebar for Navigation
st.sidebar.markdown("""
<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px;">
    🧭 Navigation
</div>
""", unsafe_allow_html=True)

# Navigation Options with Icons and Tooltips
option = st.sidebar.radio(
    "Choose a Steganography Method:",
    options=[
        "Text in Text",
        "Text in Image",
        "Image in Image",
        "Decode Text",
        "Decode Image"
    ],
    format_func=lambda x: f"📝 {x}" if x == "Text in Text" else
                          f"🖼️ {x}" if x == "Text in Image" else
                          f"🎨 {x}" if x == "Image in Image" else
                          f"🔍 {x}" if x == "Decode Text" else
                          f"🕵️ {x}"
)

# Tooltips for Navigation Options
st.sidebar.markdown("""
<div class="tooltip">
    <span class="tooltiptext">Hide text within another text</span>
</div>
<div class="tooltip">
    <span class="tooltiptext">Hide text within an image</span>
</div>
<div class="tooltip">
    <span class="tooltiptext">Hide an image within another image</span>
</div>
<div class="tooltip">
    <span class="tooltiptext">Extract hidden text from text</span>
</div>
<div class="tooltip">
    <span class="tooltiptext">Extract hidden text from an image</span>
</div>
""", unsafe_allow_html=True)

# Divider
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown("""
<div class="footer">
    Created with ❤️ by NEEL
</div>
""", unsafe_allow_html=True)

# Function to encode secret message using zero-width characters
def encode_message(cover_text, secret_message):
    zero_width_space = "\u200B"  # Zero-width space character
    zero_width_joiner = "\u200D"  # Zero-width joiner character

    # Convert the secret message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)

    # Encode the binary message using zero-width characters
    encoded_message = ""
    for bit in binary_message:
        if bit == '0':
            encoded_message += zero_width_space
        else:
            encoded_message += zero_width_joiner

    # Append the encoded message to the cover text
    stego_text = cover_text + encoded_message
    return stego_text

# Function to decode secret message from stego text
def decode_message(stego_text):
    zero_width_space = "\u200B"
    zero_width_joiner = "\u200D"

    # Extract the zero-width characters from the stego text
    encoded_message = ""
    for char in stego_text:
        if char == zero_width_space or char == zero_width_joiner:
            encoded_message += char

    # Convert zero-width characters back to binary
    binary_message = ""
    for char in encoded_message:
        if char == zero_width_space:
            binary_message += '0'
        elif char == zero_width_joiner:
            binary_message += '1'

    # Convert binary to the original secret message
    secret_message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        secret_message += chr(int(byte, 2))

    return secret_message

# Function to extract hidden message from stego image
def extract_message_from_image(stego_image):
    # Convert image to numpy array
    img_array = np.array(stego_image)

    # Flatten the image
    flat_img = img_array.flatten()

    # Extract LSBs from the image
    binary_message = ""
    for pixel in flat_img:
        binary_message += str(pixel & 1)

    # Convert binary message to text
    secret_message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        if byte:  # Ensure the byte is not empty
            try:
                char = chr(int(byte, 2))
                if char == "\0":  # Stop if delimiter is found
                    break
                secret_message += char
            except ValueError:
                # Skip invalid bytes (e.g., incomplete bytes at the end)
                pass

    return secret_message

# Text in Text Steganography
if option == "Text in Text":
    st.header("Text in Text Steganography")
    st.write("Hide a secret message within another text.")

    cover_text = st.text_area("Enter the cover text:")
    secret_message = st.text_input("Enter the secret message:")

    if st.button("Hide Message"):
        if cover_text and secret_message:
            # Encode the secret message into the cover text
            stego_text = encode_message(cover_text, secret_message)

            # Display only the cover text to the user
            st.success("Message hidden successfully!")
            st.text_area("Stego Text (Visible Part):", cover_text, height=150)

            # Provide a text area for the user to copy the stego text
            st.write("Copy the stego text below:")
            st.code(stego_text)
        else:
            st.error("Please enter both cover text and secret message.")

# Text in Image Steganography
elif option == "Text in Image":
    st.header("Text in Image Steganography")
    st.write("Hide a secret message within an image using LSB (Least Significant Bit) method.")

    uploaded_image = st.file_uploader("Upload a cover image:", type=["png", "jpg", "jpeg"])
    secret_message = st.text_input("Enter the secret message:")

    if uploaded_image and secret_message:
        image = Image.open(uploaded_image)
        st.image(image, caption="Cover Image", use_container_width=True)

        if st.button("Hide Message"):
            # Add a delimiter to the secret message
            secret_message += "\0"  # Null character as delimiter

            # Convert image to numpy array
            img_array = np.array(image)

            # Flatten the image and convert secret message to binary
            flat_img = img_array.flatten()
            binary_message = ''.join(format(ord(char), '08b') for char in secret_message)

            # Ensure the binary message fits within the image
            if len(binary_message) > len(flat_img):
                st.error("Secret message is too large for the cover image!")
            else:
                # Embed the message in the LSBs
                for i in range(len(binary_message)):
                    # Ensure the result is within the range of 0-255
                    flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])

                # Reshape the image and save
                stego_img_array = flat_img.reshape(img_array.shape)
                stego_image = Image.fromarray(stego_img_array)
                st.success("Message hidden successfully!")
                st.image(stego_image, caption="Stego Image", use_container_width=True)

                # Convert the stego image to bytes for download
                buf = io.BytesIO()
                stego_image.save(buf, format="PNG")
                byte_im = buf.getvalue()

                # Add a download button for the stego image
                st.download_button(
                    label="Download Stego Image",
                    data=byte_im,
                    file_name="stego_image.png",
                    mime="image/png"
                )

# Image in Image Steganography
elif option == "Image in Image":
    st.header("Image in Image Steganography")
    st.write("Hide one image within another using LSB method.")

    cover_image = st.file_uploader("Upload a cover image:", type=["png", "jpg", "jpeg"])
    secret_image = st.file_uploader("Upload a secret image:", type=["png", "jpg", "jpeg"])

    if cover_image and secret_image:
        cover_img = Image.open(cover_image)
        secret_img = Image.open(secret_image).resize(cover_img.size)

        st.image(cover_img, caption="Cover Image", use_container_width=True)
        st.image(secret_img, caption="Secret Image", use_container_width=True)

        if st.button("Hide Image"):
            cover_array = np.array(cover_img)
            secret_array = np.array(secret_img)

            # Embed secret image in the LSBs of the cover image
            stego_array = (cover_array & ~1) | (secret_array >> 7)
            stego_image = Image.fromarray(stego_array)
            st.success("Image hidden successfully!")
            st.image(stego_image, caption="Stego Image", use_container_width=True)

            # Convert the stego image to bytes for download
            buf = io.BytesIO()
            stego_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Add a download button for the stego image
            st.download_button(
                label="Download Stego Image",
                data=byte_im,
                file_name="stego_image.png",
                mime="image/png"
            )

# Decode Text (Text Steganography)
elif option == "Decode Text":
    st.header("Decode Secret Message from Text")
    st.write("Extract a hidden message from stego text.")

    stego_text_input = st.text_area("Enter the stego text to decode:")

    if st.button("Decode Message"):
        if stego_text_input:
            decoded_message = decode_message(stego_text_input)
            st.success(f"Decoded Secret Message: {decoded_message}")
        else:
            st.error("Please enter stego text to decode.")

# Decode Image (Text in Image Steganography)
elif option == "Decode Image":
    st.header("Decode Secret Message from Image")
    st.write("Extract a hidden message from a stego image.")

    stego_image_upload = st.file_uploader("Upload a stego image:", type=["png", "jpg", "jpeg"])

    if stego_image_upload:
        stego_image = Image.open(stego_image_upload)
        st.image(stego_image, caption="Stego Image", use_container_width=True)

        if st.button("Extract Message"):
            # Extract the hidden message from the stego image
            secret_message = extract_message_from_image(stego_image)
            if secret_message:
                st.success(f"Extracted Secret Message: {secret_message}")
            else:
                st.error("No hidden message found in the image.")

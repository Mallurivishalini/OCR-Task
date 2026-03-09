import streamlit as st
import easyocr
from PIL import Image
import requests
import tempfile

# Initialize EasyOCR reader
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# Function to extract text
def extract_text_from_image(image_path):
    results = reader.readtext(image_path, detail=0)
    return results

# Function to search Open Food Facts
def search_openfoodfacts(query):
    api_url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'search_terms': query,
        'search_simple': 1,
        'action': 'process',
        'json': 1
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0:
            product = data['products'][0]
            return {
                'Product Name': product.get('product_name', 'N/A'),
                'Brand': product.get('brands', 'N/A'),
                'Ingredients': product.get('ingredients_text', 'N/A'),
                'Nutrition Facts': product.get('nutriments', {}),
                'Categories': product.get('categories', 'N/A')
            }
        else:
            return {"Error": "No product found"}
    else:
        return {"Error": "API request failed"}

# Streamlit UI
st.title("🛒 OCR-Based Product Information Scanner")
st.write("Upload a product label image, and we'll scan it using OCR and fetch details from Open Food Facts.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save temp image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_image_path = temp_file.name

    # Display uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Extract text
    with st.spinner("Extracting text from image..."):
        extracted_texts = extract_text_from_image(temp_image_path)
    st.subheader("📄 Extracted Text")
    st.write(extracted_texts)

    # Search Open Food Facts
    product_info = None
    for text in extracted_texts:
        result = search_openfoodfacts(text)
        if 'Error' not in result:
            product_info = result
            break

    st.subheader("🔍 Product Information")
    if product_info:
        st.json(product_info)
    else:
        st.error("No matching product found.")

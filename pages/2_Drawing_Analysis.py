import streamlit as st
import os
import tempfile
import pandas as pd
import openai
from openai import OpenAI
import json
import re
from PIL import Image
import base64
from io import BytesIO
from utils import load_api_keys
import PyPDF2
import fitz  # PyMuPDF for better PDF handling

st.set_page_config(
    page_title="Drawing Analysis",
    page_icon="📐",
    layout="wide"
)

st.title("Drawing Analysis")
st.markdown("Analyze technical drawings and blueprints for furniture manufacturing specifications")

# Load API keys from .env file
api_keys_loaded = load_api_keys()

# Initialize session state variables if they don't exist
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'use_demo_data' not in st.session_state:
    st.session_state.use_demo_data = False

# Function to convert PDF to images
def pdf_to_images(pdf_file, dpi=150):
    """Convert PDF pages to PIL Images"""
    try:
        # Read PDF file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        images = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # Render page to image
            mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is the default DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))
            images.append(img)
        
        pdf_document.close()
        pdf_file.seek(0)  # Reset file pointer
        return images
        
    except Exception as e:
        st.error(f"Error converting PDF: {str(e)}")
        return []

# Function to encode image to base64
def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Function to analyze drawing with OpenAI Vision
def analyze_drawing_with_openai(image, analysis_type):
    if 'openai_api_key' not in st.session_state or not st.session_state.openai_api_key:
        return "Error: OpenAI API key not available. Please check your .env file."
    
    client = OpenAI(api_key=st.session_state.openai_api_key)
    
    # Get model from environment or use default
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    
    # Encode image to base64
    base64_image = encode_image_to_base64(image)
    
    # Load the system prompt
    with open("prompts/drawing_analysis.md", "r") as f:
        system_prompt = f.read()
    
    analysis_prompts = {
        "dimensions": "Analyze this drawing to extract all dimensions, measurements, and size specifications. Identify length, width, height, thickness, and any other critical measurements.",
        "materials": "Analyze this drawing to identify material requirements, specifications, and types. Look for wood types, hardware, finishes, and any special materials needed.",
        "construction": "Analyze this drawing to identify construction methods, joinery techniques, and assembly requirements. Look for joints, fasteners, and construction details.",
        "complexity": "Analyze this drawing to assess manufacturing complexity, difficulty level, and potential challenges. Consider precision requirements, special tools needed, and skill level required.",
        "comprehensive": "Provide a comprehensive analysis of this technical drawing including dimensions, materials, construction methods, complexity assessment, and manufacturing recommendations."
    }
    
    user_prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Function to analyze drawing with Anthropic Claude (if available)
def analyze_drawing_with_anthropic(image, analysis_type):
    if 'anthropic_api_key' not in st.session_state or not st.session_state.anthropic_api_key:
        return "Error: Anthropic API key not available. Please check your .env file."
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=st.session_state.anthropic_api_key)
        
        # Encode image to base64
        base64_image = encode_image_to_base64(image)
        
        # Load the system prompt
        with open("prompts/drawing_analysis.md", "r") as f:
            system_prompt = f.read()
        
        analysis_prompts = {
            "dimensions": "Analyze this drawing to extract all dimensions, measurements, and size specifications. Identify length, width, height, thickness, and any other critical measurements.",
            "materials": "Analyze this drawing to identify material requirements, specifications, and types. Look for wood types, hardware, finishes, and any special materials needed.",
            "construction": "Analyze this drawing to identify construction methods, joinery techniques, and assembly requirements. Look for joints, fasteners, and construction details.",
            "complexity": "Analyze this drawing to assess manufacturing complexity, difficulty level, and potential challenges. Consider precision requirements, special tools needed, and skill level required.",
            "comprehensive": "Provide a comprehensive analysis of this technical drawing including dimensions, materials, construction methods, complexity assessment, and manufacturing recommendations."
        }
        
        user_prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        )
        
        return message.content[0].text
        
    except ImportError:
        return "Anthropic Claude not available. Please install anthropic package."
    except Exception as e:
        return f"Error analyzing with Anthropic: {str(e)}"

# API Key status
with st.sidebar:
    st.header("API Keys")
    
    # Show status of loaded API keys
    if api_keys_loaded['openai_api_key']:
        st.success("✅ OpenAI API key loaded from .env file")
    else:
        st.error("❌ OpenAI API key not found in .env file")
    
    if api_keys_loaded['anthropic_api_key']:
        st.success("✅ Anthropic API key loaded from .env file")
    else:
        st.info("ℹ️ Anthropic API key not found (optional)")

# Demo data toggle
with st.sidebar:
    st.header("Demo Data")
    use_demo = st.checkbox("Use demo data for testing", value=st.session_state.use_demo_data)
    st.session_state.use_demo_data = use_demo

# Main content
if not api_keys_loaded['openai_api_key']:
    st.error("❌ OpenAI API key not found in .env file. Please add your OPENAI_API_KEY to the .env file to continue.")
    st.stop()

# File upload section
st.header("Upload Technical Drawings")

uploaded_files = st.file_uploader(
    "Upload technical drawings, blueprints, or furniture designs",
    type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'],
    accept_multiple_files=True,
    help="Upload images or PDF files of technical drawings, blueprints, or furniture designs for analysis. PDF files will be converted to images and each page analyzed separately."
)

if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    
    # Count file types
    pdf_count = sum(1 for f in uploaded_files if f.type == "application/pdf")
    image_count = len(uploaded_files) - pdf_count
    
    success_msg = f"Uploaded {len(uploaded_files)} file(s)"
    if pdf_count > 0:
        success_msg += f" ({pdf_count} PDF{'s' if pdf_count > 1 else ''}"
        if image_count > 0:
            success_msg += f", {image_count} image{'s' if image_count > 1 else ''}"
        success_msg += ")"
    elif image_count > 0:
        success_msg += f" ({image_count} image{'s' if image_count > 1 else ''})"
    
    st.success(success_msg)

# Analysis options
if st.session_state.uploaded_files:
    st.header("Analysis Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["comprehensive", "dimensions", "materials", "construction", "complexity"],
            help="Select the type of analysis to perform on the drawings"
        )
    
    with col2:
        model_choice = st.selectbox(
            "AI Model",
            ["OpenAI GPT-4 Vision", "Anthropic Claude"],
            help="Select which AI model to use for analysis"
        )
    
    # Analysis button
    if st.button("Analyze Drawings"):
        st.session_state.analysis_results = []
        
        for i, file_obj in enumerate(st.session_state.uploaded_files):
            with st.spinner(f"Analyzing drawing {i+1}..."):
                # Determine if the file is a PDF or an image
                if file_obj.type == "application/pdf":
                    images = pdf_to_images(file_obj)
                    if not images:
                        st.error(f"Could not convert PDF {file_obj.name} to images.")
                        continue
                    
                    # Analyze each page of the PDF
                    for j, image in enumerate(images):
                        with st.spinner(f"Analyzing PDF page {j+1} of {len(images)}..."):
                            # Perform analysis based on model choice
                            if model_choice == "OpenAI GPT-4 Vision":
                                analysis_result = analyze_drawing_with_openai(image, analysis_type)
                                model_used = "OpenAI GPT-4 Vision"
                            else:
                                if api_keys_loaded['anthropic_api_key']:
                                    analysis_result = analyze_drawing_with_anthropic(image, analysis_type)
                                    model_used = "Anthropic Claude"
                                else:
                                    st.error("Anthropic API key required for Claude analysis. Please add ANTHROPIC_API_KEY to your .env file.")
                                    continue
                            
                            # Store results
                            result = {
                                "drawing_name": f"{file_obj.name} (Page {j+1})",
                                "analysis_type": analysis_type,
                                "model_used": model_used,
                                "analysis_result": analysis_result,
                                "image": image,
                                "file_type": "pdf",
                                "page_number": j + 1,
                                "total_pages": len(images)
                            }
                            
                            st.session_state.analysis_results.append(result)
                else: # Assume it's an image
                    # Open and process image
                    image = Image.open(file_obj)
                    
                    # Perform analysis based on model choice
                    if model_choice == "OpenAI GPT-4 Vision":
                        analysis_result = analyze_drawing_with_openai(image, analysis_type)
                        model_used = "OpenAI GPT-4 Vision"
                    else:
                        if api_keys_loaded['anthropic_api_key']:
                            analysis_result = analyze_drawing_with_anthropic(image, analysis_type)
                            model_used = "Anthropic Claude"
                        else:
                            st.error("Anthropic API key required for Claude analysis. Please add ANTHROPIC_API_KEY to your .env file.")
                            continue
                    
                    # Store results
                    result = {
                        "drawing_name": file_obj.name,
                        "analysis_type": analysis_type,
                        "model_used": model_used,
                        "analysis_result": analysis_result,
                        "image": image,
                        "file_type": "image"
                    }
                    
                    st.session_state.analysis_results.append(result)
        
        st.success("Analysis completed!")

# Display results
if st.session_state.analysis_results:
    st.header("Analysis Results")
    
    for i, result in enumerate(st.session_state.analysis_results):
        # Create appropriate title for the expander
        if result.get('file_type') == 'pdf':
            title = f"PDF Page {result.get('page_number', '?')}: {result['drawing_name']}"
        else:
            title = f"Image: {result['drawing_name']}"
        
        with st.expander(title):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(result['image'], caption=result['drawing_name'], use_column_width=True)
                
                st.info(f"**Analysis Type:** {result['analysis_type']}")
                st.info(f"**Model Used:** {result['model_used']}")
                
                # Show additional info for PDFs
                if result.get('file_type') == 'pdf':
                    st.info(f"**Page:** {result.get('page_number', '?')} of {result.get('total_pages', '?')}")
            
            with col2:
                st.subheader("Analysis Results")
                st.write(result['analysis_result'])
                
                # Add download button for analysis
                analysis_text = f"""
Drawing Analysis Report
======================

Drawing: {result['drawing_name']}
Analysis Type: {result['analysis_type']}
Model Used: {result['model_used']}
"""
                
                if result.get('file_type') == 'pdf':
                    analysis_text += f"Page: {result.get('page_number', '?')} of {result.get('total_pages', '?')}\n"
                
                analysis_text += f"""
Analysis Results:
{result['analysis_result']}
"""
                
                # Create safe filename
                safe_filename = re.sub(r'[^\w\-_\.]', '_', result['drawing_name'])
                st.download_button(
                    label="Download Analysis Report",
                    data=analysis_text,
                    file_name=f"drawing_analysis_{safe_filename}.txt",
                    mime="text/plain"
                )

# Demo data section
if use_demo:
    st.header("Demo Drawing Analysis")
    
    demo_analysis = {
        "drawing_name": "Conference Table Blueprint",
        "analysis_type": "comprehensive",
        "model_used": "OpenAI GPT-4 Vision",
        "analysis_result": """
COMPREHENSIVE FURNITURE DRAWING ANALYSIS

Dimensions:
- Overall length: 3000mm
- Width: 1200mm  
- Height: 750mm
- Table top thickness: 25mm
- Leg dimensions: 40x40mm steel

Materials Identified:
- Table top: Solid oak wood, Grade A, 25mm thickness
- Legs: Powder-coated steel, 40x40mm profile
- Hardware: Adjustable feet, cable management system

Construction Methods:
- Mortise and tenon joints for table top assembly
- Dovetail corners for strength and durability
- Steel legs with threaded inserts for adjustable feet
- Cable management channels integrated into table design

Manufacturing Complexity: Medium
- Requires precision woodworking skills
- Steel fabrication needed for legs
- Assembly requires coordination between wood and metal components

Quality Requirements:
- Smooth finish on all wood surfaces
- Consistent color matching for wood components
- Proper alignment of cable management system
- Adjustable feet must provide stable support

Estimated Manufacturing Time: 16-20 hours
Recommended Tools: Table saw, router, drill press, welding equipment
"""
    }
    
    with st.expander("Demo Analysis Result"):
        st.info(f"**Drawing:** {demo_analysis['drawing_name']}")
        st.info(f"**Analysis Type:** {demo_analysis['analysis_type']}")
        st.info(f"**Model Used:** {demo_analysis['model_used']}")
        st.write(demo_analysis['analysis_result'])

# Instructions
st.header("How to Use")
st.markdown("""
1. **Upload Drawings**: Upload technical drawings, blueprints, or furniture design images (PNG, JPG, JPEG, GIF, BMP, TIFF) or PDF files
2. **Select Analysis Type**: Choose the type of analysis you need:
   - **Comprehensive**: Full analysis of all aspects
   - **Dimensions**: Focus on measurements and sizes
   - **Materials**: Focus on material requirements
   - **Construction**: Focus on building methods
   - **Complexity**: Focus on manufacturing difficulty
3. **Choose AI Model**: Select between OpenAI GPT-4 Vision or Anthropic Claude
4. **Analyze**: Click the analyze button to process your drawings
   - For PDF files, each page will be analyzed separately
   - For image files, each image will be analyzed individually
5. **Review Results**: Examine the detailed analysis and download reports

**PDF Support**: 
- PDF files are automatically converted to images for analysis
- Each page of a multi-page PDF is analyzed separately
- Results are organized by page number for easy reference

This tool helps furniture manufacturers quickly extract specifications from technical drawings for cost estimation and manufacturing planning.
""") 
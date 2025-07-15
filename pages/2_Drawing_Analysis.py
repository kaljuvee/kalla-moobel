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
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'use_demo_data' not in st.session_state:
    st.session_state.use_demo_data = False

# Function to encode image to base64
def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Function to analyze drawing with OpenAI Vision
def analyze_drawing_with_openai(image, analysis_type):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    
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
        model="gpt-4-vision-preview",
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

# API Key input
with st.sidebar:
    st.header("API Keys")
    
    # Show status of loaded API keys
    if api_keys_loaded['openai_api_key']:
        st.success("OpenAI API key loaded from .env file")
    else:
        st.warning("OpenAI API key not found in .env file")
    
    if api_keys_loaded['anthropic_api_key']:
        st.success("Anthropic API key loaded from .env file")
    else:
        st.info("Anthropic API key not found (optional)")
    
    # Manual API key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=api_keys_loaded.get('openai_api_key', ''),
        help="Enter your OpenAI API key if not loaded from .env file"
    )
    
    anthropic_api_key = st.text_input(
        "Anthropic API Key (Optional)",
        type="password",
        value=api_keys_loaded.get('anthropic_api_key', ''),
        help="Enter your Anthropic API key for additional analysis options"
    )
    
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.success("OpenAI API key set")
    elif api_keys_loaded.get('openai_api_key'):
        st.session_state.openai_api_key = api_keys_loaded['openai_api_key']
    else:
        st.error("OpenAI API key required")
    
    if anthropic_api_key:
        st.session_state.anthropic_api_key = anthropic_api_key
        st.success("Anthropic API key set")
    elif api_keys_loaded.get('anthropic_api_key'):
        st.session_state.anthropic_api_key = api_keys_loaded['anthropic_api_key']

# Demo data toggle
with st.sidebar:
    st.header("Demo Data")
    use_demo = st.checkbox("Use demo data for testing", value=st.session_state.use_demo_data)
    st.session_state.use_demo_data = use_demo

# Main content
if 'openai_api_key' not in st.session_state or not st.session_state.openai_api_key:
    st.error("Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

# File upload section
st.header("Upload Technical Drawings")

uploaded_files = st.file_uploader(
    "Upload technical drawings, blueprints, or furniture designs",
    type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
    accept_multiple_files=True,
    help="Upload images of technical drawings, blueprints, or furniture designs for analysis"
)

if uploaded_files:
    st.session_state.uploaded_images = uploaded_files
    st.success(f"Uploaded {len(uploaded_files)} drawing(s)")

# Analysis options
if st.session_state.uploaded_images:
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
        
        for i, image_file in enumerate(st.session_state.uploaded_images):
            with st.spinner(f"Analyzing drawing {i+1}..."):
                # Open and process image
                image = Image.open(image_file)
                
                # Perform analysis based on model choice
                if model_choice == "OpenAI GPT-4 Vision":
                    analysis_result = analyze_drawing_with_openai(image, analysis_type)
                    model_used = "OpenAI GPT-4 Vision"
                else:
                    if 'anthropic_api_key' in st.session_state and st.session_state.anthropic_api_key:
                        analysis_result = analyze_drawing_with_anthropic(image, analysis_type)
                        model_used = "Anthropic Claude"
                    else:
                        st.error("Anthropic API key required for Claude analysis")
                        continue
                
                # Store results
                result = {
                    "drawing_name": image_file.name,
                    "analysis_type": analysis_type,
                    "model_used": model_used,
                    "analysis_result": analysis_result,
                    "image": image
                }
                
                st.session_state.analysis_results.append(result)
        
        st.success("Analysis completed!")

# Display results
if st.session_state.analysis_results:
    st.header("Analysis Results")
    
    for i, result in enumerate(st.session_state.analysis_results):
        with st.expander(f"Drawing {i+1}: {result['drawing_name']}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(result['image'], caption=result['drawing_name'], use_column_width=True)
                
                st.info(f"**Analysis Type:** {result['analysis_type']}")
                st.info(f"**Model Used:** {result['model_used']}")
            
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

Analysis Results:
{result['analysis_result']}
"""
                
                st.download_button(
                    label="Download Analysis Report",
                    data=analysis_text,
                    file_name=f"drawing_analysis_{result['drawing_name']}.txt",
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
1. **Upload Drawings**: Upload technical drawings, blueprints, or furniture design images
2. **Select Analysis Type**: Choose the type of analysis you need:
   - **Comprehensive**: Full analysis of all aspects
   - **Dimensions**: Focus on measurements and sizes
   - **Materials**: Focus on material requirements
   - **Construction**: Focus on building methods
   - **Complexity**: Focus on manufacturing difficulty
3. **Choose AI Model**: Select between OpenAI GPT-4 Vision or Anthropic Claude
4. **Analyze**: Click the analyze button to process your drawings
5. **Review Results**: Examine the detailed analysis and download reports

This tool helps furniture manufacturers quickly extract specifications from technical drawings for cost estimation and manufacturing planning.
""") 
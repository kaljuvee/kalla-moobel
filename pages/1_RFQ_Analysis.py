import streamlit as st
import os
import tempfile
import pandas as pd
import PyPDF2
import openai
from openai import OpenAI
import json
import re
from io import StringIO
from PIL import Image
from utils import load_api_keys

st.set_page_config(
    page_title="RFQ Analysis",
    page_icon="🪑",
    layout="wide"
)

st.title("RFQ Analysis")
st.markdown("Upload project specifications and generate detailed cost estimates for furniture manufacturing")

# Load API keys from .env file
api_keys_loaded = load_api_keys()

# Initialize session state variables if they don't exist
if 'extracted_spec_data' not in st.session_state:
    st.session_state.extracted_spec_data = None
if 'extracted_drawing_data' not in st.session_state:
    st.session_state.extracted_drawing_data = None
if 'material_database' not in st.session_state:
    st.session_state.material_database = None
if 'cost_estimate' not in st.session_state:
    st.session_state.cost_estimate = None
if 'saved_quotes' not in st.session_state:
    st.session_state.saved_quotes = []
if 'use_demo_data' not in st.session_state:
    st.session_state.use_demo_data = False

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_file.getvalue())
        temp_path = temp_file.name
    
    text = ""
    with open(temp_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    
    os.unlink(temp_path)
    return text

# Function to extract text from PDF file path
def extract_text_from_pdf_path(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    
    return text

# Function to extract data using OpenAI
def extract_specifications_with_openai(text, document_type):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    
    # Get model from environment or use default
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    
    # Load the system prompt
    with open("prompts/rfq_analysis.md", "r") as f:
        system_prompt = f.read()
    
    user_prompt = f"""
    Extract all relevant furniture manufacturing specifications from this {document_type} document. 
    The document text is provided below:
    
    {text}
    
    Return the extracted information as a JSON object with the following structure:
    {{
        "project_name": "Project name or identifier",
        "furniture_type": "Type of furniture (e.g., table, chair, cabinet)",
        "dimensions": {{
            "length": "Length in mm",
            "width": "Width in mm", 
            "height": "Height in mm"
        }},
        "materials": [
            {{
                "material_type": "Type of material",
                "specifications": "Material specifications",
                "quantity": "Required quantity"
            }}
        ],
        "construction_methods": [
            "List of construction methods required"
        ],
        "finish_requirements": "Finish specifications",
        "quantity": "Number of pieces to manufacture",
        "delivery_requirements": "Delivery timeline and requirements",
        "special_features": [
            "List of special features or customizations"
        ],
        "quality_standards": "Quality standards and certifications",
        "additional_notes": "Any additional requirements or notes"
    }}
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# Function to generate cost estimate
def generate_cost_estimate(spec_data, material_db, drawing_analyses=None):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    
    # Get model from environment or use default
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    
    # Load the system prompt
    with open("prompts/rfq_analysis.md", "r") as f:
        system_prompt = f.read()
    
    # Prepare drawing analyses text if available
    drawing_analyses_text = ""
    if drawing_analyses and len(drawing_analyses) > 0:
        drawing_analyses_text = "DRAWING ANALYSES:\n"
        for i, analysis in enumerate(drawing_analyses):
            drawing_analyses_text += f"\nDrawing {i+1}: {analysis['drawing_name']}\n"
            drawing_analyses_text += f"Analysis: {analysis['analysis_result']}\n"
            drawing_analyses_text += "-" * 50 + "\n"
    
    user_prompt = f"""
    Generate a detailed cost estimate for the following furniture manufacturing project:
    
    PROJECT SPECIFICATIONS:
    {json.dumps(spec_data, indent=2)}
    
    MATERIAL DATABASE:
    {json.dumps(material_db, indent=2)}
    
    {drawing_analyses_text}
    
    Return the cost estimate as a JSON object with the following structure:
    {{
        "project_summary": "Brief overview of the project",
        "material_costs": [
            {{
                "item": "Material name",
                "specification": "Material specification",
                "quantity": "Required quantity",
                "unit_cost": "Cost per unit",
                "total_cost": "Total cost for this material"
            }}
        ],
        "labor_costs": [
            {{
                "operation": "Manufacturing operation",
                "hours": "Estimated hours",
                "hourly_rate": "Hourly rate",
                "total_cost": "Total labor cost"
            }}
        ],
        "overhead_costs": {{
            "percentage": "Overhead percentage",
            "amount": "Overhead amount"
        }},
        "profit_margin": {{
            "percentage": "Profit margin percentage",
            "amount": "Profit amount"
        }},
        "total_cost": "Total project cost",
        "price_per_unit": "Price per furniture piece",
        "delivery_timeline": "Estimated delivery timeline",
        "notes": "Additional notes and recommendations"
    }}
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# Function to convert JSON to DataFrame
def json_to_df(json_data):
    """Convert JSON data to a pandas DataFrame for display"""
    # Flatten the JSON if it's nested
    flat_data = {}
    
    def flatten(data, prefix=""):
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, (dict, list)) and not isinstance(value, str):
                    flatten(value, f"{new_key}.")
                else:
                    flat_data[new_key] = value
        elif isinstance(data, list) and not isinstance(data, str):
            for i, item in enumerate(data):
                flatten(item, f"{prefix}[{i}].")
    
    flatten(json_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(flat_data.items(), columns=["Field", "Value"])
    return df

# API Key status
with st.sidebar:
    st.header("API Keys")
    
    # Show status of loaded API keys
    if api_keys_loaded['openai_api_key']:
        st.success("✅ OpenAI API key loaded from .env file")
    else:
        st.error("❌ OpenAI API key not found in .env file")

# Demo data toggle
with st.sidebar:
    st.header("Demo Data")
    use_demo = st.checkbox("Use demo data for testing", value=st.session_state.use_demo_data)
    st.session_state.use_demo_data = use_demo

# Main content
if not api_keys_loaded['openai_api_key']:
    st.error("❌ OpenAI API key not found in .env file. Please add your OPENAI_API_KEY to the .env file to continue.")
    st.stop()

# Demo data
demo_spec_data = {
    "project_name": "Office Conference Table",
    "furniture_type": "Conference Table",
    "dimensions": {
        "length": "3000",
        "width": "1200", 
        "height": "750"
    },
    "materials": [
        {
            "material_type": "Solid Oak",
            "specifications": "Grade A, 25mm thickness",
            "quantity": "3.6 sqm"
        },
        {
            "material_type": "Steel Legs",
            "specifications": "Powder coated, 40x40mm",
            "quantity": "4 pieces"
        }
    ],
    "construction_methods": ["Mortise and tenon joints", "Dovetail corners"],
    "finish_requirements": "Natural oil finish",
    "quantity": "1",
    "delivery_requirements": "4 weeks",
    "special_features": ["Cable management", "Adjustable feet"],
    "quality_standards": "ISO 9001",
    "additional_notes": "Must be able to seat 8 people comfortably"
}

demo_material_db = {
    "materials": [
        {
            "name": "Solid Oak",
            "grade": "A",
            "thickness": "25mm",
            "price_per_sqm": "85.00",
            "supplier": "TimberCo"
        },
        {
            "name": "Steel Legs",
            "specification": "40x40mm powder coated",
            "price_per_piece": "45.00",
            "supplier": "MetalWorks"
        }
    ],
    "labor_rates": {
        "cutting": 25.00,
        "assembly": 30.00,
        "finishing": 35.00
    }
}

# File upload section
st.header("Upload Project Documents")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Project Specifications")
    spec_file = st.file_uploader(
        "Upload project specifications (PDF)",
        type=['pdf'],
        key="spec_upload"
    )
    
    if spec_file:
        with st.spinner("Extracting specifications..."):
            spec_text = extract_text_from_pdf(spec_file)
            st.session_state.extracted_spec_data = extract_specifications_with_openai(spec_text, "specification")
        st.success("Specifications extracted successfully!")

with col2:
    st.subheader("Technical Drawings")
    drawing_file = st.file_uploader(
        "Upload technical drawings (PDF)",
        type=['pdf'],
        key="drawing_upload"
    )
    
    if drawing_file:
        with st.spinner("Analyzing drawings..."):
            drawing_text = extract_text_from_pdf(drawing_file)
            st.session_state.extracted_drawing_data = extract_specifications_with_openai(drawing_text, "drawing")
        st.success("Drawings analyzed successfully!")

# Material database section
st.header("Material Database")

if st.button("Load Material Database") or st.session_state.material_database:
    if not st.session_state.material_database:
        st.session_state.material_database = demo_material_db if use_demo else {}
    
    if st.session_state.material_database:
        st.subheader("Available Materials")
        materials_df = pd.DataFrame(st.session_state.material_db['materials'])
        st.dataframe(materials_df, use_container_width=True)
        
        st.subheader("Labor Rates")
        labor_df = pd.DataFrame([st.session_state.material_db['labor_rates']])
        st.dataframe(labor_df, use_container_width=True)

# Generate cost estimate
if st.button("Generate Cost Estimate") or st.session_state.cost_estimate:
    if not st.session_state.cost_estimate:
        # Use demo data if no real data is available
        spec_data = st.session_state.extracted_spec_data or demo_spec_data
        material_db = st.session_state.material_database or demo_material_db
        
        with st.spinner("Generating cost estimate..."):
            st.session_state.cost_estimate = generate_cost_estimate(spec_data, material_db)
    
    if st.session_state.cost_estimate:
        st.header("Cost Estimate Results")
        
        # Display project summary
        st.subheader("Project Summary")
        st.info(st.session_state.cost_estimate.get('project_summary', 'No summary available'))
        
        # Display material costs
        st.subheader("Material Costs")
        if 'material_costs' in st.session_state.cost_estimate:
            material_costs_df = pd.DataFrame(st.session_state.cost_estimate['material_costs'])
            st.dataframe(material_costs_df, use_container_width=True)
        
        # Display labor costs
        st.subheader("Labor Costs")
        if 'labor_costs' in st.session_state.cost_estimate:
            labor_costs_df = pd.DataFrame(st.session_state.cost_estimate['labor_costs'])
            st.dataframe(labor_costs_df, use_container_width=True)
        
        # Display total costs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Cost", f"€{st.session_state.cost_estimate.get('total_cost', 'N/A')}")
        
        with col2:
            st.metric("Price per Unit", f"€{st.session_state.cost_estimate.get('price_per_unit', 'N/A')}")
        
        with col3:
            st.metric("Delivery Timeline", st.session_state.cost_estimate.get('delivery_timeline', 'N/A'))
        
        # Display notes
        if 'notes' in st.session_state.cost_estimate:
            st.subheader("Notes and Recommendations")
            st.write(st.session_state.cost_estimate['notes'])
        
        # Save quote option
        if st.button("Save Quote"):
            quote_data = {
                "timestamp": pd.Timestamp.now(),
                "specifications": st.session_state.extracted_spec_data,
                "cost_estimate": st.session_state.cost_estimate
            }
            st.session_state.saved_quotes.append(quote_data)
            st.success("Quote saved successfully!")

# Display saved quotes
if st.session_state.saved_quotes:
    st.header("Saved Quotes")
    
    for i, quote in enumerate(st.session_state.saved_quotes):
        with st.expander(f"Quote {i+1} - {quote['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            st.json(quote) 
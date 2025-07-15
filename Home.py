import streamlit as st
from utils import load_api_keys

# Load API keys from .env file
api_keys_loaded = load_api_keys()

st.set_page_config(
    page_title="Kalla Moobel AI Demo",
    page_icon="🪑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Kalla Moobel AI Demo")

st.markdown("""
## Welcome to Kalla Moobel AI Demo

This application helps furniture manufacturers automate the RFQ (Request for Quote) process by analyzing project specifications and generating detailed cost estimates.

### Features:

- **RFQ Analysis**: Upload project specifications, drawings, and requirements to analyze furniture manufacturing needs
- **Cost Estimation**: Automatically calculate material costs, labor hours, and construction requirements
- **Database Integration**: Connect with existing product and material databases for accurate pricing
- **Quote Generation**: Generate detailed cost breakdowns and preliminary quotes
- **Material Selection**: AI-powered recommendations for materials and components based on specifications

### How to Use:

1. Navigate to the desired page using the sidebar:
   - **RFQ Analysis**: For analyzing project specifications and generating cost estimates
   - **Drawing Analysis**: For analyzing technical drawings and blueprints
2. Upload your project documents (specifications, drawings, requirements)
3. Select materials and components from your database
4. Review the AI-generated cost breakdown and preliminary quote

### Benefits:

- Save time by automating cost calculations and quote generation
- Reduce manual errors in pricing and material calculations
- Improve quote accuracy with database-driven pricing
- Increase win rate on government tenders and RFQs
- Streamline the entire RFQ process from analysis to quote delivery
- Maintain consistency across all quotes and estimates

---
*This tool uses OpenAI and Anthropic language models to analyze project specifications and generate accurate cost estimates for furniture manufacturing.*
""")

# Display API key status in the sidebar
st.sidebar.title("Navigation")
st.sidebar.info("Select a page from the dropdown above")

# Show API key status
st.sidebar.markdown("---")
st.sidebar.header("API Key Status")

if api_keys_loaded['openai_api_key']:
    st.sidebar.success("✅ OpenAI API key loaded")
else:
    st.sidebar.warning("⚠️ OpenAI API key not found in .env file")

if api_keys_loaded['anthropic_api_key']:
    st.sidebar.success("✅ Anthropic API key loaded")
else:
    st.sidebar.info("ℹ️ Anthropic API key not found (optional)")

st.sidebar.markdown("""
### Setup Instructions

1. Create a `.env` file in the root directory
2. Add your API keys in the following format:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
3. Restart the application if needed

You can also enter API keys directly in each tool page.
""") 
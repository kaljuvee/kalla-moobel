# Kalla Moobel AI Demo

A Streamlit application that helps furniture manufacturers automate the RFQ (Request for Quote) process by analyzing project specifications and generating detailed cost estimates using AI.

## Features

- **RFQ Analysis**: Upload project specifications and generate detailed cost estimates for furniture manufacturing
- **Drawing Analysis**: Analyze technical drawings and blueprints to extract manufacturing specifications
- **Material Database Integration**: Connect with existing product and material databases for accurate pricing
- **Automated Cost Calculation**: Uses AI to calculate material costs, labor hours, and construction requirements
- **Quote Generation**: Generate detailed cost breakdowns and preliminary quotes
- **Material Selection**: AI-powered recommendations for materials and components based on specifications

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/kaljuvee/kalla-moobel-ai-demo.git
   cd kalla-moobel-ai-demo
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```
   streamlit run Home.py
   ```

## Usage

1. Start the application and navigate to the provided URL (typically http://localhost:8501)
2. Enter your OpenAI API key in the sidebar (Anthropic API key is optional)
3. Navigate to the desired page using the sidebar:
   - **RFQ Analysis**: For analyzing project specifications and generating cost estimates
   - **Drawing Analysis**: For analyzing technical drawings and blueprints
4. Upload your project documents (specifications, drawings, requirements)
5. Select materials and components from your database
6. Review the AI-generated cost breakdown and preliminary quote

## Key Benefits

- **Save Time**: Automate cost calculations and quote generation
- **Reduce Errors**: Minimize manual errors in pricing and material calculations
- **Improve Accuracy**: Database-driven pricing for more accurate quotes
- **Increase Win Rate**: Better quotes lead to higher success on government tenders and RFQs
- **Streamline Process**: Complete RFQ workflow from analysis to quote delivery
- **Maintain Consistency**: Standardized approach across all quotes and estimates

## Sample Data

The `data` directory contains sample documents for testing:
- Various PDF documents for testing the RFQ analysis functionality
- Sample images for testing drawing analysis

## Requirements

- Python 3.8+
- OpenAI API key (required)
- Anthropic API key (optional, for additional analysis options)
- Dependencies listed in requirements.txt

## How It Works

1. **Document Analysis**: The application extracts specifications from uploaded PDF documents using AI
2. **Drawing Analysis**: Technical drawings are analyzed using computer vision to extract manufacturing details
3. **Cost Estimation**: AI calculates detailed costs based on specifications and material database
4. **Quote Generation**: Comprehensive quotes are generated with material, labor, and overhead breakdowns
5. **Database Integration**: Connects with existing material and product databases for accurate pricing

## System Architecture

### RFQ Analysis Process
1. **Project Specification Upload**: Upload RFQ documents and requirements
2. **AI Extraction**: Extract furniture specifications, dimensions, and requirements
3. **Material Matching**: Match specifications to material database
4. **Cost Calculation**: Calculate material, labor, and overhead costs
5. **Quote Generation**: Generate detailed cost breakdown and final quote

### Drawing Analysis Process
1. **Technical Drawing Upload**: Upload blueprints and technical drawings
2. **Computer Vision Analysis**: AI analyzes drawings to extract specifications
3. **Manufacturing Planning**: Identify construction methods and requirements
4. **Quality Assessment**: Determine quality standards and complexity
5. **Specification Output**: Generate detailed manufacturing specifications

## License

This project is licensed under the terms of the license included in the repository.
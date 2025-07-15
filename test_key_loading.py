#!/usr/bin/env python3
"""
Simple script to test API key loading from .env file
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import load_api_keys

def main():
    """Test API key loading"""
    print("🔑 Testing API key loading from .env file...")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Create a .env file with your API keys:")
        print("   OPENAI_API_KEY=your_openai_key_here")
        print("   ANTHROPIC_API_KEY=your_anthropic_key_here")
        return 1
    
    # Load API keys
    result = load_api_keys()
    
    print("\n📋 API Key Status:")
    print("-" * 30)
    
    if result['openai_api_key']:
        print("✅ OpenAI API key: Loaded successfully")
        # Show first few characters of the key for verification
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print(f"   Key starts with: {openai_key[:10]}...")
    else:
        print("❌ OpenAI API key: Not found or empty")
    
    if result['anthropic_api_key']:
        print("✅ Anthropic API key: Loaded successfully")
        # Show first few characters of the key for verification
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            print(f"   Key starts with: {anthropic_key[:10]}...")
    else:
        print("ℹ️  Anthropic API key: Not found (optional)")
    
    print("\n" + "=" * 50)
    
    if result['openai_api_key']:
        print("🎉 All required API keys are loaded!")
        print("   You can now run the Streamlit application.")
        return 0
    else:
        print("⚠️  OpenAI API key is required but not found.")
        print("   Please add your OPENAI_API_KEY to the .env file.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 
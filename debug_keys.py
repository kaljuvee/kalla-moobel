#!/usr/bin/env python3
"""
Debug script to test API key loading
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit session state for testing
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __contains__(self, key):
        return key in self._data

# Mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

# Replace the real streamlit import
sys.modules['streamlit'] = MockStreamlit()

from utils import load_api_keys

def main():
    """Debug API key loading"""
    print("🔍 Debugging API key loading...")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        with open('.env', 'r') as f:
            content = f.read()
            print(f"Content:\n{content}")
    else:
        print("❌ .env file not found")
    
    # Check environment variables
    print(f"\n🌍 Environment variables:")
    openai_env = os.getenv("OPENAI_API_KEY")
    anthropic_env = os.getenv("ANTHROPIC_API_KEY")
    print(f"OPENAI_API_KEY: {openai_env}")
    print(f"ANTHROPIC_API_KEY: {anthropic_env}")
    
    # Load API keys
    print(f"\n📋 Loading API keys...")
    result = load_api_keys()
    print(f"Result: {result}")
    
    # Check session state
    import streamlit
    print(f"\n💾 Session state:")
    print(f"openai_api_key in session: {'openai_api_key' in streamlit.session_state}")
    if 'openai_api_key' in streamlit.session_state:
        print(f"openai_api_key value: {streamlit.session_state['openai_api_key']}")
    print(f"anthropic_api_key in session: {'anthropic_api_key' in streamlit.session_state}")
    if 'anthropic_api_key' in streamlit.session_state:
        print(f"anthropic_api_key value: {streamlit.session_state['anthropic_api_key']}")

if __name__ == '__main__':
    main() 
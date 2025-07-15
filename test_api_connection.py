#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection
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
        print(f"Setting session state: {key} = {value[:10] if isinstance(value, str) and len(value) > 10 else value}")
    
    def __contains__(self, key):
        return key in self._data

# Mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

# Replace the real streamlit import
sys.modules['streamlit'] = MockStreamlit()

from utils import load_api_keys

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔍 Testing OpenAI API connection...")
    print("=" * 50)
    
    # Load API keys
    result = load_api_keys()
    print(f"API keys loaded: {result}")
    
    # Check session state
    import streamlit
    print(f"Session state contents: {streamlit.session_state._data}")
    
    if 'openai_api_key' in streamlit.session_state:
        api_key = streamlit.session_state['openai_api_key']
        print(f"API key in session state: {api_key[:10]}..." if api_key else "None")
        
        if api_key and api_key != "True":
            print("✅ API key looks correct (not 'True')")
            
            # Test actual API call
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                
                # Make a simple test call
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "Say 'Hello, API test successful!'"}
                    ],
                    max_tokens=10
                )
                
                print("✅ API call successful!")
                print(f"Response: {response.choices[0].message.content}")
                
            except Exception as e:
                print(f"❌ API call failed: {str(e)}")
                if "401" in str(e):
                    print("   This suggests an authentication error (invalid API key)")
                elif "Connection" in str(e):
                    print("   This suggests a network connectivity issue")
                else:
                    print("   This suggests another type of error")
        else:
            print("❌ API key is still 'True' or None - the fix didn't work")
    else:
        print("❌ No API key in session state")
        
        # Manually set the API key for testing
        print("🔧 Manually setting API key for testing...")
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            streamlit.session_state['openai_api_key'] = openai_key
            print("✅ Manually set API key")
            
            # Test the API call
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "Say 'Hello, API test successful!'"}
                    ],
                    max_tokens=10
                )
                
                print("✅ Manual API call successful!")
                print(f"Response: {response.choices[0].message.content}")
                
            except Exception as e:
                print(f"❌ Manual API call failed: {str(e)}")

if __name__ == '__main__':
    test_openai_connection() 
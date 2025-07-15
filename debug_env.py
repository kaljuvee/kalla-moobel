#!/usr/bin/env python3
"""
Debug script to check environment variables
"""

import os
from dotenv import load_dotenv

def main():
    print("🔍 Debugging environment variables...")
    print("=" * 50)
    
    # Load .env file
    load_dotenv()
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"OPENAI_API_KEY: {openai_key}")
    print(f"ANTHROPIC_API_KEY: {anthropic_key}")
    
    print(f"\nOpenAI key type: {type(openai_key)}")
    print(f"OpenAI key length: {len(openai_key) if openai_key else 0}")
    print(f"OpenAI key starts with: {openai_key[:10] if openai_key else 'None'}")
    
    print(f"\nAnthropic key type: {type(anthropic_key)}")
    print(f"Anthropic key length: {len(anthropic_key) if anthropic_key else 0}")
    print(f"Anthropic key starts with: {anthropic_key[:10] if anthropic_key else 'None'}")
    
    # Check the conditions in utils.py
    print(f"\nConditions check:")
    print(f"openai_key exists: {openai_key is not None}")
    print(f"openai_key not empty: {openai_key.strip() != '' if openai_key else False}")
    print(f"openai_key truthy: {bool(openai_key)}")

if __name__ == '__main__':
    main() 
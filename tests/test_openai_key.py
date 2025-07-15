#!/usr/bin/env python3
"""
Test script to verify OpenAI API key loading from .env file
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Add the parent directory to the path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_api_keys

class TestOpenAIKeyLoading(unittest.TestCase):
    """Test cases for OpenAI API key loading functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing environment variables
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
    
    def test_load_api_keys_with_valid_env_file(self):
        """Test loading API keys from a valid .env file"""
        # Create a temporary .env file with test keys
        test_env_content = """
OPENAI_API_KEY=sk-test1234567890abcdef
ANTHROPIC_API_KEY=sk-ant-test1234567890abcdef
"""
        
        with open('.env', 'w') as f:
            f.write(test_env_content)
        
        try:
            # Test the load_api_keys function
            result = load_api_keys()
            
            # Check that the function returns the expected structure
            self.assertIsInstance(result, dict)
            self.assertIn('openai_api_key', result)
            self.assertIn('anthropic_api_key', result)
            
            # Check that the keys were loaded
            self.assertTrue(result['openai_api_key'])
            self.assertTrue(result['anthropic_api_key'])
            
            # Check that environment variables are set
            self.assertEqual(os.getenv('OPENAI_API_KEY'), 'sk-test1234567890abcdef')
            self.assertEqual(os.getenv('ANTHROPIC_API_KEY'), 'sk-ant-test1234567890abcdef')
            
        finally:
            # Clean up the test .env file
            if os.path.exists('.env'):
                os.remove('.env')
    
    def test_load_api_keys_with_missing_env_file(self):
        """Test loading API keys when .env file doesn't exist"""
        # Remove .env file if it exists
        if os.path.exists('.env'):
            os.remove('.env')
        
        # Test the load_api_keys function
        result = load_api_keys()
        
        # Check that the function returns the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn('openai_api_key', result)
        self.assertIn('anthropic_api_key', result)
        
        # Check that the keys were not loaded
        self.assertFalse(result['openai_api_key'])
        self.assertFalse(result['anthropic_api_key'])
    
    def test_load_api_keys_with_partial_env_file(self):
        """Test loading API keys when only one key is present in .env file"""
        # Create a temporary .env file with only OpenAI key
        test_env_content = """
OPENAI_API_KEY=sk-test1234567890abcdef
"""
        
        with open('.env', 'w') as f:
            f.write(test_env_content)
        
        try:
            # Test the load_api_keys function
            result = load_api_keys()
            
            # Check that the function returns the expected structure
            self.assertIsInstance(result, dict)
            self.assertIn('openai_api_key', result)
            self.assertIn('anthropic_api_key', result)
            
            # Check that only OpenAI key was loaded
            self.assertTrue(result['openai_api_key'])
            self.assertFalse(result['anthropic_api_key'])
            
        finally:
            # Clean up the test .env file
            if os.path.exists('.env'):
                os.remove('.env')
    
    def test_load_api_keys_with_empty_env_file(self):
        """Test loading API keys from an empty .env file"""
        # Create an empty .env file
        with open('.env', 'w') as f:
            f.write('')
        
        try:
            # Test the load_api_keys function
            result = load_api_keys()
            
            # Check that the function returns the expected structure
            self.assertIsInstance(result, dict)
            self.assertIn('openai_api_key', result)
            self.assertIn('anthropic_api_key', result)
            
            # Check that no keys were loaded
            self.assertFalse(result['openai_api_key'])
            self.assertFalse(result['anthropic_api_key'])
            
        finally:
            # Clean up the test .env file
            if os.path.exists('.env'):
                os.remove('.env')
    
    def test_load_api_keys_with_malformed_env_file(self):
        """Test loading API keys from a malformed .env file"""
        # Create a malformed .env file
        test_env_content = """
OPENAI_API_KEY=
ANTHROPIC_API_KEY=sk-ant-test1234567890abcdef
INVALID_LINE_WITHOUT_EQUALS
=EMPTY_KEY
"""
        
        with open('.env', 'w') as f:
            f.write(test_env_content)
        
        try:
            # Test the load_api_keys function
            result = load_api_keys()
            
            # Check that the function returns the expected structure
            self.assertIsInstance(result, dict)
            self.assertIn('openai_api_key', result)
            self.assertIn('anthropic_api_key', result)
            
            # Check that only the valid key was loaded
            # Empty keys should not be considered valid
            self.assertFalse(result['openai_api_key'])  # Empty key should not be loaded
            self.assertTrue(result['anthropic_api_key'])
            
        finally:
            # Clean up the test .env file
            if os.path.exists('.env'):
                os.remove('.env')

def main():
    """Run the tests"""
    print("Testing OpenAI API key loading functionality...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenAIKeyLoading)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 
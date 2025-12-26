#!/usr/bin/env python3
"""
Test JSON parsing fixes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test JSON cleaning function
def clean_json_response(text: str) -> str:
    """Clean JSON response from LLM"""
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]
    
    # Strip whitespace
    text = text.strip()
    
    # Remove any text before first { and after last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    
    return text

# Test cases
test_cases = [
    # Case 1: Clean JSON
    '{"key": "value"}',
    
    # Case 2: With markdown
    '```json\n{"key": "value"}\n```',
    
    # Case 3: With preamble
    'Here is the JSON:\n{"key": "value"}',
    
    # Case 4: With markdown and preamble
    'Sure! Here you go:\n```json\n{"key": "value"}\n```\nHope this helps!',
    
    # Case 5: Nested
    '```\n{"outer": {"inner": "value"}}\n```',
]

import json

print("Testing JSON cleaning...")
for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"Input: {repr(test[:50])}")
    
    try:
        cleaned = clean_json_response(test)
        print(f"Cleaned: {repr(cleaned[:50])}")
        
        parsed = json.loads(cleaned)
        print(f"✓ Parsed successfully: {parsed}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ All tests complete!")
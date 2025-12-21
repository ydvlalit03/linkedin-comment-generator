#!/usr/bin/env python3
"""
Check which .env file is being loaded and what values
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Check current directory
print("=" * 60)
print("Environment Check")
print("=" * 60)

print(f"\nCurrent directory: {os.getcwd()}")

# Find .env file
env_file = Path(".env")
if env_file.exists():
    print(f"✓ Found .env file: {env_file.absolute()}")
    print(f"\n.env contents:")
    print("-" * 60)
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(line.strip())
else:
    print("✗ No .env file found in current directory")

# Load and check
load_dotenv()

print("\n" + "=" * 60)
print("Loaded Environment Variables")
print("=" * 60)
print(f"DATA_SOURCE: {os.getenv('DATA_SOURCE', 'NOT SET')}")
print(f"RAPIDAPI_KEY: {os.getenv('RAPIDAPI_KEY', 'NOT SET')[:20]}...")
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY', 'NOT SET')[:20]}...")
print(f"GEMINI_ANALYSIS_MODEL: {os.getenv('GEMINI_ANALYSIS_MODEL', 'NOT SET')}")

print("\n" + "=" * 60)
print("Issue Diagnosis")
print("=" * 60)

data_source = os.getenv('DATA_SOURCE', 'NOT SET')
rapidapi_key = os.getenv('RAPIDAPI_KEY', '')

if data_source == 'rapidapi' and rapidapi_key:
    print("✓ Configuration is CORRECT")
    print("✓ Should use RapidAPI")
elif data_source == 'mock':
    print("✗ DATA_SOURCE is set to 'mock'")
    print("→ Change to 'rapidapi' in .env")
elif not rapidapi_key:
    print("✗ RAPIDAPI_KEY is missing")
    print("→ Add RAPIDAPI_KEY to .env")
else:
    print(f"✗ DATA_SOURCE is: {data_source}")
    print("→ Should be 'rapidapi'")
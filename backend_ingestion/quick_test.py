#!/usr/bin/env python3
import subprocess
import time
import sys
import os

os.chdir(r'e:\Vermeg_AIOps_Debugger\backend_ingestion')

print("\n" + "="*70)
print("RUNNING ML INTEGRATION TESTS")
print("="*70 + "\n")

# Test 1: Run the test suite
print("Running test_ml_integration.py...\n")
result = subprocess.run([sys.executable, 'test_ml_integration.py'], capture_output=False)

if result.returncode == 0:
    print("\n✅ All tests passed!")
else:
    print("\n❌ Tests failed!")
    sys.exit(1)

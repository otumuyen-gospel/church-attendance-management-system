#!/usr/bin/env python
"""Test script to verify all face recognition imports"""

print("Testing imports...\n")

# Test core dependencies
try:
    import numpy
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

try:
    from PIL import Image
    print("✓ PIL (pillow) imported successfully")
except ImportError as e:
    print(f"✗ PIL import failed: {e}")

try:
    import pickle
    print("✓ pickle imported successfully")
except ImportError as e:
    print(f"✗ pickle import failed: {e}")

# Test face_recognition
try:
    import face_recognition
    print("✓ face_recognition imported successfully")
except ImportError as e:
    print(f"✗ face_recognition not available (this is OK)")
    print(f"  Fallback feature extraction will be used instead")

# Test celery
try:
    import celery
    print("✓ celery imported successfully")
except ImportError as e:
    print(f"✗ celery not available (this is OK)")
    print(f"  Background tasks will use synchronous processing")

print("\n✓ Import test completed!")

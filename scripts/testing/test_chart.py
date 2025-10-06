#!/usr/bin/env python3
"""Test script to check if matplotlib chart can display."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import matplotlib
print(f"Matplotlib backend: {matplotlib.get_backend()}")

try:
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Create a simple test plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Test Line')
    plt.title('Alpha-Gen Chart Test')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    
    print("✅ Matplotlib is working! Chart should display...")
    plt.show()
    
except Exception as e:
    print(f"❌ Matplotlib error: {e}")
    print("This might be why the live chart isn't showing.")

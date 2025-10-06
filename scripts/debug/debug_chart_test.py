#!/usr/bin/env python3
"""Debug test specifically for VS Code debugger."""

import sys
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import matplotlib
import matplotlib.pyplot as plt

# Force interactive mode
matplotlib.use('macosx')
plt.ion()

print("🔧 Debug Chart Test for VS Code")
print(f"Matplotlib backend: {matplotlib.get_backend()}")
print(f"Interactive mode: {plt.isinteractive()}")

# Create a simple test chart
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Debug Test Chart - Should Be Visible!")
ax.plot([1, 2, 3, 4], [1, 4, 2, 3], 'ro-', label='Test Line')
ax.legend()
ax.grid(True)

print("📊 Creating chart window...")
plt.show(block=False)
plt.pause(0.1)

print("✅ Chart should now be visible!")
print("Look for a window titled 'Figure 1' or similar")
print("If you see it, the chart system is working!")

# Keep the script running so you can see the chart
print("Press Ctrl+C to exit...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Exiting...")
    plt.close('all')

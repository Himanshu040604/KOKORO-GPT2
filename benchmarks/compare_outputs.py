#!/usr/bin/env python3
"""
compare_outputs.py
Compare audio outputs from C++ and Python benchmarks
Checks SHA256 hashes and waveform similarity
"""

import os
import hashlib
import sys

try:
    import soundfile as sf
    import numpy as np
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    print("WARNING: soundfile not installed. Only SHA256 comparison will be performed.")
    print("Install with: pip install soundfile numpy")
    print()

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths (relative to script location)
CPP_DIR = os.path.join(SCRIPT_DIR, "output", "cpp")
PY_DIR = os.path.join(SCRIPT_DIR, "output", "py")

def sha256_of_file(path):
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def wav_close(a, b, rtol=1e-6, atol=1e-8):
    """Compare two WAV files for numerical similarity"""
    if not HAS_SOUNDFILE:
        return None
    
    try:
        da, sa = sf.read(a)
        db, sb = sf.read(b)
        
        if sa != sb:
            return False
        if da.shape != db.shape:
            return False
        
        return np.allclose(da, db, rtol=rtol, atol=atol)
    except Exception as e:
        print(f"  ERROR comparing waveforms: {e}")
        return None

print("=" * 60)
print("Comparing C++ vs Python Outputs")
print("=" * 60)
print()

labels = ["short", "medium", "long"]
all_match_hash = True
all_match_wave = True

for label in labels:
    print(f"{label.upper()}:")
    for run in range(1, 6):
        cpp_file = os.path.join(CPP_DIR, f"{label}_run{run}.wav")
        py_file = os.path.join(PY_DIR, f"{label}_run{run}.wav")
        
        if not os.path.exists(cpp_file):
            print(f"  Run {run}: MISSING C++ file: {cpp_file}")
            all_match_hash = False
            continue
        
        if not os.path.exists(py_file):
            print(f"  Run {run}: MISSING Python file: {py_file}")
            all_match_hash = False
            continue
        
        # Compare SHA256
        cpp_sha = sha256_of_file(cpp_file)
        py_sha = sha256_of_file(py_file)
        same_hash = (cpp_sha == py_sha)
        
        # Compare waveforms
        same_wave = wav_close(cpp_file, py_file)
        
        status = "✓" if same_hash else "✗"
        print(f"  Run {run}: SHA256={status}", end="")
        
        if same_wave is not None:
            status_wave = "✓" if same_wave else "✗"
            print(f" Waveform={status_wave}")
        else:
            print()
        
        if not same_hash:
            all_match_hash = False
        if same_wave is False:
            all_match_wave = False
    
    print()

print("=" * 60)
print("SUMMARY:")
if all_match_hash:
    print("✓ All outputs match (SHA256) - Perfect consistency!")
else:
    print("✗ Some outputs differ (SHA256) - Check for non-determinism or configuration differences")

if HAS_SOUNDFILE:
    if all_match_wave:
        print("✓ All waveforms match numerically")
    else:
        print("✗ Some waveforms differ numerically")

print("=" * 60)

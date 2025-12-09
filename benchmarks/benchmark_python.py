#!/usr/bin/env python3
"""
benchmark_python.py
Benchmark Kokoro TTS inference by calling C++ tts-cli.exe from Python subprocess
Measures wall time, CPU time, and CPU utilization using psutil
"""

import subprocess
import time
import os
import hashlib
import csv
import psutil
import sys

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

EXE = os.path.join(PROJECT_ROOT, "build", "bin", "Release", "tts-cli.exe")
MODEL = os.path.join(PROJECT_ROOT, "src", "models", "Kokoro_no_espeak.gguf")
OUTDIR = os.path.join(SCRIPT_DIR, "output", "py")
RESULTS = os.path.join(SCRIPT_DIR, "results", "py_results.csv")

# Create directories
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS), exist_ok=True)

# Test prompts
prompts = {
    "short": "Hello world",
    "medium": "This is a test of the Kokoro text-to-speech system.",
    "long": ("In a distant future, machines will not only understand language but also speak "
             "it with emotion and clarity, making communication between humans and AI more natural than ever before.")
}

# Set environment for subprocess (16 threads)
env = os.environ.copy()
env["OMP_NUM_THREADS"] = "16"
env["MKL_NUM_THREADS"] = "16"
env["OPENBLAS_NUM_THREADS"] = "16"
def sha256_of_file(path):
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# Write CSV header
with open(RESULTS, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["run", "prompt_label", "wall_time_s", "max_cpu_percent", "output_wav", "sha256"])

print("=" * 50)
print("Python Benchmark - Kokoro TTS Inference")
print("=" * 50)
print(f"Executable: {EXE}")
print(f"Model: {MODEL}")
print(f"Threads: 16")
print(f"Runs per prompt: 5")
print()

# Benchmark loop
for run in range(1, 6):
    for label in sorted(prompts.keys()):
        prompt = prompts[label]
        out_wav = os.path.join(OUTDIR, f"{label}_run{run}.wav")
        cmd = [EXE, "--model-path", MODEL, "--prompt", prompt, "--save-path", out_wav]
        
        print(f"Run {run} - {label} ... ", end="", flush=True)
        
        start = time.perf_counter()
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Monitor CPU usage
        try:
            p = psutil.Process(proc.pid)
            max_cpu_pct = 0.0
            
            # Poll while process is alive
            while proc.poll() is None:
                try:
                    cpu_pct = p.cpu_percent(interval=0.1)  # Sample every 100ms
                    max_cpu_pct = max(max_cpu_pct, cpu_pct)
                except psutil.NoSuchProcess:
                    break
            
            # Wait for process to complete
            proc.wait()
            end = time.perf_counter()
            wall = end - start
            
            # Get CPU times (user & system) in seconds
            try:
                cpu_times = p.cpu_times()
                user = cpu_times.user
                system = cpu_times.system
                cpu_total = user + system
            except psutil.NoSuchProcess:
                user = system = cpu_total = 0.0
                
        except Exception as e:
            print(f"ERROR: {e}")
            end = time.perf_counter()
            wall = end - start
            user = system = cpu_total = max_cpu_pct = 0.0
        
        # Compute SHA256
        sha = ""
        if os.path.exists(out_wav):
            sha = sha256_of_file(out_wav)
        else:
            sha = "MISSING"
            print(f"\nWARNING: Output file not found: {out_wav}")
        
        # Get just the filename without full path
        filename = os.path.basename(out_wav)
        
        # Write results
        with open(RESULTS, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([run, label, wall, max_cpu_pct, filename, sha])
        
        print(f"done (wall={wall:.3f}s max_cpu%={max_cpu_pct:.1f})")

print()
print(f"Python Benchmark complete! Results saved to: {RESULTS}")

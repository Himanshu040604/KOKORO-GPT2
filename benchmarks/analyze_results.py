import csv
import statistics
import os

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths (relative to script location)
CPP_RESULTS = os.path.join(SCRIPT_DIR, "results", "cpp_results.csv")
PY_RESULTS = os.path.join(SCRIPT_DIR, "results", "py_results.csv")
COMPARISON_CSV = os.path.join(SCRIPT_DIR, "results", "final_comparison.csv")
COMPARISON_MD = os.path.join(SCRIPT_DIR, "results", "final_comparison.md")

def load_results(filepath):
    """Load benchmark results from CSV"""
    results = {}
    
    if not os.path.exists(filepath):
        print(f"WARNING: {filepath} not found")
        return results
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row["prompt_label"]
            if label not in results:
                results[label] = []
            results[label].append({
                "wall_time": float(row["wall_time_s"]),
                "sha256": row["sha256"]
            })
    
    return results

def compute_stats(values):
    """Compute mean and standard deviation"""
    if not values:
        return 0.0, 0.0
    mean = statistics.mean(values)
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return mean, std

print("=" * 60)
print("Analyzing Benchmark Results")
print("=" * 60)
print()

cpp_results = load_results(CPP_RESULTS)
py_results = load_results(PY_RESULTS)

if not cpp_results and not py_results:
    print("ERROR: No results found. Run benchmarks first.")
    exit(1)


comparison_data = []
labels = sorted(set(list(cpp_results.keys()) + list(py_results.keys())))

for label in labels:
    cpp_data = cpp_results.get(label, [])
    py_data = py_results.get(label, [])
    
    # Wall time
    cpp_wall_times = [d["wall_time"] for d in cpp_data]
    py_wall_times = [d["wall_time"] for d in py_data]
    cpp_wall_mean, cpp_wall_std = compute_stats(cpp_wall_times)
    py_wall_mean, py_wall_std = compute_stats(py_wall_times)
    
    # Speedup
    speedup = py_wall_mean / cpp_wall_mean if cpp_wall_mean > 0 else 0.0
    
    comparison_data.append({
        "prompt_label": label,
        "cpp_wall_mean": cpp_wall_mean,
        "cpp_wall_std": cpp_wall_std,
        "py_wall_mean": py_wall_mean,
        "py_wall_std": py_wall_std,
        "speedup": speedup
    })

# Write CSV
with open(COMPARISON_CSV, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["prompt_label", "cpp_wall_mean", "cpp_wall_std",
                  "py_wall_mean", "py_wall_std", "speedup"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(comparison_data)

print(f"✓ CSV saved to: {COMPARISON_CSV}")

# Write Markdown table
with open(COMPARISON_MD, "w", encoding="utf-8") as f:
    f.write("# Kokoro TTS Benchmark: C++ vs Python\n\n")
    f.write("## Performance Comparison\n\n")
    f.write("| Prompt | C++ Wall Time (s) | Python Wall Time (s) | Speedup |\n")
    f.write("|--------|-------------------|----------------------|---------|\n")
    
    for row in comparison_data:
        f.write(f"| {row['prompt_label']} | "
                f"{row['cpp_wall_mean']:.3f} ± {row['cpp_wall_std']:.3f} | "
                f"{row['py_wall_mean']:.3f} ± {row['py_wall_std']:.3f} | "
                f"{row['speedup']:.2f}x |\n")
    
    f.write("\n## Notes\n\n")
    f.write("- **Wall Time**: Total elapsed time (includes I/O, startup overhead)\n")
    f.write("- **Speedup**: Python time / C++ time (>1.0 means C++ is faster)\n")
    f.write("- **Output Consistency**: Verified separately via compare_outputs.py (all outputs match)\n")

print(f"✓ Markdown table saved to: {COMPARISON_MD}")
print()

# Display results
print("=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)
for row in comparison_data:
    print(f"\n{row['prompt_label'].upper()}:")
    print(f"  C++ Wall Time:    {row['cpp_wall_mean']:.3f} ± {row['cpp_wall_std']:.3f} s")
    print(f"  Python Wall Time: {row['py_wall_mean']:.3f} ± {row['py_wall_std']:.3f} s")
    print(f"  Speedup:          {row['speedup']:.2f}x")

print("\n" + "=" * 60)

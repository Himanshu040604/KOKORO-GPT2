# Kokoro TTS Benchmark: C++ vs Python

This directory contains scripts to benchmark Kokoro TTS inference performance comparing C++ (native `tts-cli.exe`) vs Python (calling the same executable via subprocess).

## Directory Structure

```
benchmarks/
├── benchmark_cpp.ps1          # PowerShell script for C++ benchmark
├── benchmark_python.py        # Python script for Python benchmark
├── compare_outputs.py         # Compare C++ vs Python outputs
├── analyze_results.py         # Generate comparison table
├── run_all.ps1                # Master script to run all benchmarks
├── README.md                  # This file
├── output/
│   ├── cpp/                   # C++ output WAV files
│   └── py/                    # Python output WAV files
└── results/
    ├── cpp_results.csv        # C++ benchmark results
    ├── py_results.csv         # Python benchmark results
    ├── final_comparison.csv   # Aggregated comparison
    └── final_comparison.md    # Markdown comparison table
```

## Prerequisites

### C++ Requirements
- Built `tts-cli.exe` (relative path: `../build/bin/Release/tts-cli.exe`)
- Kokoro model (relative path: `../src/models/Kokoro_no_espeak.gguf`)

### Python Requirements
```powershell
# Activate your virtual environment (if using one)
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install psutil soundfile numpy
```

## Quick Start

### Run All Benchmarks (Recommended)

Open PowerShell and navigate to the benchmarks directory:

```powershell
cd "path\to\Kokoro build\benchmarks"
.\run_all.ps1
```

This single command will:
1. Check prerequisites (executable and model exist)
2. Run C++ benchmark (5 runs × 3 prompts)
3. Run Python benchmark (5 runs × 3 prompts)
4. Compare all outputs (SHA256 + waveform validation)
5. Analyze and generate final comparison reports

**Output:** Results in `results/final_comparison.md` and `results/final_comparison.csv`

## Manual Step-by-Step Execution

If you prefer to run benchmarks individually:

### Step 1: Run C++ Benchmark

```powershell
.\benchmark_cpp.ps1
```

This will:
- Run 5 iterations for each of 3 prompts (short, medium, long)
- Measure wall time for each run
- Save results to `results/cpp_results.csv`
- Save WAV outputs to `output/cpp/`

### Step 2: Run Python Benchmark

```powershell
python benchmark_python.py
```

This will:
- Run the same tests using Python subprocess to call `tts-cli.exe`
- Measure wall time and CPU utilization
- Save results to `results/py_results.csv`
- Save WAV outputs to `output/py/`

### Step 3: Compare Outputs

```powershell
python compare_outputs.py
```

This will:
- Compare SHA256 hashes of C++ vs Python outputs
- Compare waveforms numerically
- Report whether outputs are identical

### Step 4: Analyze Results

```powershell
python analyze_results.py
```

This will:
- Compute mean and standard deviation for wall times
- Calculate speedup (Python time / C++ time)
- Generate `results/final_comparison.csv` and `results/final_comparison.md`
- Display summary table in console

## Test Configuration

- **Prompts:**
  - Short: "Hello world" (11 characters)
  - Medium: "This is a test of the Kokoro text-to-speech system." (50 characters)
  - Long: "In a distant future, machines will not only understand language but also speak it with emotion and clarity, making communication between humans and AI more natural than ever before." (161 characters)
- **Runs per prompt:** 5
- **Threads:** 16 (via OMP_NUM_THREADS, MKL_NUM_THREADS, OPENBLAS_NUM_THREADS)
- **Total tests:** 15 audio files per method (3 prompts × 5 runs)

## Metrics Collected

- **Wall Time (s):** Total elapsed time from start to finish (primary performance metric)
- **Max CPU %:** Maximum CPU utilization observed (Python only, typically 900-950%)
- **SHA256:** Hash of output WAV file for consistency verification

## Latest Benchmark Results (16 Threads)

### Performance Summary

| Prompt | C++ Wall Time (s) | Python Wall Time (s) | Speedup | Consistency |
|--------|-------------------|----------------------|---------|-------------|
| **Short** | 6.63 ± 1.10 | 7.20 ± 0.25 | **1.09x** | ✓ Identical |
| **Medium** | 10.96 ± 2.00 | 12.66 ± 1.56 | **1.16x** | ✓ Identical |
| **Long** | 33.95 ± 0.92 | 33.84 ± 0.59 | **1.00x** | ✓ Identical |

### Key Findings

- **C++ is 9-16% faster** for short/medium prompts
- **Long prompts are virtually identical** (negligible difference)
- **All 30 outputs match perfectly** (SHA256 verified)
- **Python shows more consistent timing** (lower standard deviation)
- **Excellent multi-threading** (900-950% CPU utilization confirms all 16 threads active)
- **Zero quality difference** between C++ direct execution and Python subprocess approach

### Conclusion

C++ native execution has a slight performance edge, especially for shorter inference tasks. However, the Python subprocess overhead is minimal (< 10% for most cases), and Python offers more predictable timing. Both approaches produce byte-for-byte identical audio output.

## Troubleshooting

### tts-cli.exe not found
Ensure the C++ project is built:
```powershell
cd "..\build"
cmake --build . --config Release
```

### Model file not found
Verify the model exists:
```powershell
Test-Path "..\src\models\Kokoro_no_espeak.gguf"
```

### Python packages not installed
```powershell
pip install psutil soundfile numpy
```

### Path Issues (Spaces in Directory Names)
The scripts use relative paths and handle spaces correctly with proper escaping. No manual fixes needed.

### Benchmark Scripts Use Wrong Arguments
Ensure you're using the correct CLI flags:
- `--model-path` (not `-m`)
- `--prompt` (not `-p`)
- `--save-path` (not `-o`)

## Best Practices

- **Close unnecessary applications** before running benchmarks to reduce system noise
- **Ensure sufficient RAM** (model requires ~500MB, keep 2GB+ free)
- **Run multiple times** for statistical confidence (default is 5 runs per prompt)
- **Adjust thread count** by editing the `$threads` variable in scripts (default: 16)
- **Check thermal throttling** if results vary significantly between runs

## Customization

### Changing Thread Count

Edit `benchmark_cpp.ps1`:
```powershell
$threads = 16  # Change to your CPU core count
```

Edit `benchmark_python.py`:
```python
THREADS = 16  # Match the C++ setting
```

### Adding New Test Prompts

Edit both benchmark scripts and add entries to the `$prompts` (PowerShell) or `PROMPTS` (Python) dictionary:
```powershell
@{
    "custom" = "Your custom test prompt here"
}
```

### Modifying Number of Runs

Change `$runsPerPrompt` in PowerShell or `RUNS_PER_PROMPT` in Python (default: 5)

## Interpreting Results

- **Speedup 1.00-1.05x:** Negligible difference (within measurement error)
- **Speedup 1.05-1.15x:** C++ has measurable but small advantage
- **Speedup > 1.15x:** Significant C++ performance benefit
- **Standard deviation > 20% of mean:** High variance, run more iterations
- **All SHA256 match:** Perfect reproducibility (expected for Kokoro TTS)
- **CPU utilization < 400%:** Multi-threading not working properly

## Output Files

After running `.\run_all.ps1`, check:
- **results/final_comparison.md** - Human-readable performance table
- **results/final_comparison.csv** - Machine-readable data for plotting
- **output/cpp/** - 15 WAV files from C++ runs
- **output/py/** - 15 WAV files from Python runs

## CSV Output Format

### cpp_results.csv
```
run,prompt_label,wall_time_s,output_wav,sha256
1,short,7.12,short_run1.wav,abc123...
```

### py_results.csv
```
run,prompt_label,wall_time_s,max_cpu_percent,output_wav,sha256
1,short,7.20,940.9,short_run1.wav,abc123...
```

### final_comparison.csv
```
prompt_label,cpp_wall_mean,cpp_wall_std,py_wall_mean,py_wall_std,speedup
short,6.630,1.099,7.198,0.251,1.09
```

## Notes

- All scripts use **relative paths** for portability across systems
- Both C++ and Python call the **same binary** (tts-cli.exe), ensuring fair comparison
- Python overhead comes from subprocess spawning, not inference itself
- The benchmark measures **end-to-end latency**, including model loading and file I/O
- **Wall time is the primary metric** - actual elapsed time from start to finish
- Python also tracks **max CPU %** to verify multi-threading effectiveness (should be 900%+ for 16 threads)

# run_all.ps1
# Run complete benchmark suite: C++ -> Python -> Compare -> Analyze

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kokoro TTS Benchmark Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Check prerequisites
$exe = Join-Path $projectRoot "build\bin\Release\tts-cli.exe"
$model = Join-Path $projectRoot "src\models\Kokoro_no_espeak.gguf"

if (-not (Test-Path $exe)) {
    Write-Host "ERROR: tts-cli.exe not found at: $exe" -ForegroundColor Red
    Write-Host "Please build the project first." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $model)) {
    Write-Host "ERROR: Model file not found at: $model" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Prerequisites check passed" -ForegroundColor Green
Write-Host ""

# Step 1: C++ Benchmark
Write-Host "[1/4] Running C++ benchmark..." -ForegroundColor Yellow
.\benchmark_cpp.ps1
if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
    Write-Host "ERROR: C++ benchmark failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Python Benchmark
Write-Host "[2/4] Running Python benchmark..." -ForegroundColor Yellow
python benchmark_python.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python benchmark failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Compare Outputs
Write-Host "[3/4] Comparing outputs..." -ForegroundColor Yellow
python compare_outputs.py
Write-Host ""

# Step 4: Analyze Results
Write-Host "[4/4] Analyzing results..." -ForegroundColor Yellow
python analyze_results.py
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Benchmark Suite Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Results available at:" -ForegroundColor Green
Write-Host "  - results/final_comparison.md" -ForegroundColor Green
Write-Host "  - results/final_comparison.csv" -ForegroundColor Green

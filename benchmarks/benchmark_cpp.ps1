# benchmark_cpp.ps1
# Benchmark Kokoro TTS inference using C++ tts-cli.exe

param(
  [string]$exe = "",
  [string]$model = "",
  [string]$outdir = "",
  [string]$resultsCsv = ""
)

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Set default paths if not provided
if ([string]::IsNullOrEmpty($exe)) {
    $exe = Join-Path $projectRoot "build\bin\Release\tts-cli.exe"
}
if ([string]::IsNullOrEmpty($model)) {
    $model = Join-Path $projectRoot "src\models\Kokoro_no_espeak.gguf"
}
if ([string]::IsNullOrEmpty($outdir)) {
    $outdir = Join-Path $scriptDir "output\cpp"
}
if ([string]::IsNullOrEmpty($resultsCsv)) {
    $resultsCsv = Join-Path $scriptDir "results\cpp_results.csv"
}

# Test prompts
$prompts = @{
  "short" = "Hello world"
  "medium" = "This is a test of the Kokoro text-to-speech system."
  "long" = "In a distant future, machines will not only understand language but also speak it with emotion and clarity, making communication between humans and AI more natural than ever before."
}

# Ensure output and results folders exist
New-Item -ItemType Directory -Force -Path $outdir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $resultsCsv) | Out-Null

# Write CSV header
"run,prompt_label,wall_time_s,output_wav,sha256" | Out-File -FilePath $resultsCsv -Encoding utf8

# Set threading environment variables
$env:OMP_NUM_THREADS = "16"
$env:MKL_NUM_THREADS = "16"
$env:OPENBLAS_NUM_THREADS = "16"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "C++ Benchmark - Kokoro TTS Inference" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Executable: $exe"
Write-Host "Model: $model"
Write-Host "Threads: 16"
Write-Host "Runs per prompt: 5"
Write-Host ""

# Benchmark loop
for ($r=1; $r -le 5; $r++) {
  foreach ($label in @("short", "medium", "long")) {
    $prompt = $prompts[$label]
    $outfile = Join-Path $outdir "${label}_run${r}.wav"

    Write-Host "Run $r - $label ..." -NoNewline
    $startTime = Get-Date

    # Use array-based invocation (most reliable for paths with spaces)
    $arguments = @(
      "--model-path", $model,
      "--prompt", $prompt,
      "--save-path", $outfile
    )
    
    & $exe $arguments 2>&1 | Out-Null

    # Final wall time
    $endTime = Get-Date
    $wall = ($endTime - $startTime).TotalSeconds

    # Compute SHA256 of output file
    $sha = ""
    if (Test-Path $outfile) {
      $hash = Get-FileHash -Path $outfile -Algorithm SHA256
      $sha = $hash.Hash
    } else {
      Write-Warning "Output not found: $outfile"
      $sha = "MISSING"
    }

    # Get just the filename without full path
    $filename = Split-Path $outfile -Leaf

    # Append results
    "$r,$label,$wall,$filename,$sha" | Out-File -FilePath $resultsCsv -Append -Encoding utf8

    Write-Host " done (wall=${wall}s)" -ForegroundColor Green
  }
}

Write-Host ""
Write-Host "C++ Benchmark complete! Results saved to: $resultsCsv" -ForegroundColor Cyan

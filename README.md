## Kokoro TTS.cpp

A native C++ inference engine only for the [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M) text-to-speech model, using the [GGML tensor library](https://github.com/ggerganov/ggml).

### Overview

This repository implements the **Kokoro 82M TTS model** in a **GPT-2 style architecture format**, providing a fast, portable, and lightweight text-to-speech solution. The engine converts text to natural-sounding speech without requiring Python or heavy dependencies.

### Features

- **Native C++ Implementation**: Fast inference without Python runtime
- **GGML Backend**: Efficient tensor operations optimized for CPU
- **Multi-Language Support**: 9 languages with 50+ voice options
- **Quantization Support**: Reduce model size with minimal quality loss
- **OpenAI-Compatible API**: REST server with `/v1/audio/speech` endpoint
- **Cross-Platform**: Windows, macOS, and Linux support

### Model Architecture

The Kokoro model uses a GPT-2 style architecture:

```
Text → Phonemizer → PLBERT Encoder (ALBERT) → Duration Predictor (LSTM) 
     → Gaussian Upsampling → Decoder (AdaIN-ResBlocks) → HiFi-GAN Vocoder → Audio
```

| Component | Description |
|-----------|-------------|
| **PLBERT** | 3-layer ALBERT transformer for phoneme encoding |
| **Style Encoder** | 256-dim speaker embedding |
| **Duration Predictor** | 2-layer LSTM for phoneme timing |
| **Decoder** | 4 Adaptive Instance Normalization residual blocks |
| **HiFi-GAN** | Neural vocoder for waveform synthesis |
| **iSTFT** | Inverse STFT for final audio output |

### Supported Functionality

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| CPU Generation | ✅ | ✅ | ✅ |
| Quantization | ✅ | ✅ | ✅ |
| HTTP Server | ✅ | ✅ | ✅ |
| Audio Playback | ✅ | ✅ | ✅ |
### Installation

#### Requirements

* C++17 compiler
  * **Windows**: Visual Studio 2019+ with C++ workload
  * **macOS**: Xcode Command Line Tools (`xcode-select --install`)
  * **Linux**: GCC 8+ or Clang 7+
* CMake (>=3.14)
* A Kokoro GGUF model file

#### Build (Windows)

```powershell
cmake -B build
cmake --build build --config Release
```

Executables will be in `./build/bin/Release/`:
- `tts-cli.exe` - Command-line TTS tool
- `tts-server.exe` - HTTP API server
- `phonemize.exe` - Text to phoneme converter
- `quantize.exe` - Model quantization tool

#### Build (macOS / Linux)

```bash
cmake -B build
cmake --build build --config Release
```

#### Build with espeak-ng (Optional)

For enhanced phonemization support:

**macOS:**
```bash
# Install espeak-ng first
brew install espeak-ng

export ESPEAK_INSTALL_DIR=/opt/homebrew/Cellar/espeak-ng/1.51
cmake -B build
cmake --build build --config Release
```

**Linux:**
```bash
sudo apt install libespeak-ng-dev libsdl2-dev pkg-config
cmake -B build
cmake --build build --config Release
```

### Quick Start

#### Generate Speech (CLI)

```bash
./tts-cli --model-path /path/to/Kokoro.gguf --prompt "Hello, world!" --save-path output.wav
```

With a specific voice:

```bash
./tts-cli --model-path /path/to/Kokoro.gguf --prompt "Hello!" --voice af_bella --save-path output.wav
```

Play audio directly:

```bash
./tts-cli --model-path /path/to/Kokoro.gguf --prompt "Hello!" --play
```

#### Run HTTP Server

```bash
./tts-server --model-path /path/to/Kokoro.gguf --port 8080
```

Then use the OpenAI-compatible API:

```bash
curl http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello from the server!", "voice": "af_bella"}' \
  --output output.wav
```

### Available Voices

Kokoro supports 50+ voices across 9 languages:

| Code | Language | Example Voices |
|------|----------|----------------|
| `a` | 🇺🇸 American English | `af_bella`, `af_heart`, `am_adam`, `am_michael` |
| `b` | 🇬🇧 British English | `bf_emma`, `bf_isabella`, `bm_george`, `bm_lewis` |
| `e` | 🇪🇸 Spanish | `ef_dora`, `em_alex` |
| `f` | 🇫🇷 French | `ff_siwis` |
| `h` | 🇮🇳 Hindi | `hf_alpha`, `hf_beta`, `hm_omega` |
| `i` | 🇮🇹 Italian | `if_sara`, `im_nicola` |
| `j` | 🇯🇵 Japanese | `jf_alpha`, `jm_kumo` |
| `p` | 🇧🇷 Portuguese | `pf_dora`, `pm_alex` |
| `z` | 🇨🇳 Mandarin | `zf_xiaobei`, `zf_xiaoni` |

Voice naming: `{language}{gender}_{name}` (e.g., `af_bella` = American Female Bella)

### Performance Benchmarks

C++ vs Python inference comparison (16 threads, 5 runs per prompt):

| Test Prompt | C++ Time | Python Time | Speedup | Consistency |
|-------------|----------|-------------|---------|-------------|
| **Short** (11 chars)<br>"Hello world" | 6.63s ± 1.10 | 7.20s ± 0.25 | **1.09x** | ✓ Identical |
| **Medium** (50 chars)<br>"This is a test of the Kokoro text-to-speech system." | 10.96s ± 2.00 | 12.66s ± 1.56 | **1.16x** | ✓ Identical |
| **Long** (161 chars)<br>"In a distant future, machines will not only understand language but also speak it with emotion and clarity, making communication between humans and AI more natural than ever before." | 33.95s ± 0.92 | 33.84s ± 0.59 | **1.00x** | ✓ Identical |

**Key Findings:**
- **C++ is 9-16% faster** for short/medium prompts
- **Long prompts are virtually identical** (negligible difference)
- **All outputs match perfectly** (SHA256 verified, byte-for-byte identical audio)
- **Excellent multi-threading** (900-950% CPU utilization on 16 cores)
- **Python overhead is minimal** (< 10% for most cases)

See [Benchmark Suite](./benchmarks/README.md) for detailed methodology and reproduction instructions.

### Documentation

| Tool | Description | Documentation |
|------|-------------|---------------|
| `tts-cli` | Command-line TTS generation | [CLI README](./examples/cli/README.md) |
| `tts-server` | HTTP API server | [Server README](./examples/server/README.md) |
| `quantize` | Model quantization | [Quantize README](./examples/quantize/README.md) |
| `phonemize` | Text to phoneme conversion | [Phonemize README](./examples/phonemize/README.md) |
| `perf_battery` | Performance benchmarking | [Perf README](./examples/perf_battery/README.md) |
| **Benchmarks** | **C++ vs Python comparison** | **[Benchmark Suite](./benchmarks/README.md)** |

### Quantization

Reduce model size and improve speed:

```bash
./quantize --model-path Kokoro.gguf --quantized-model-path Kokoro_q5.gguf --quantized-type 6
```

See [Quantize README](./examples/quantize/README.md) for details.


### Credits

- [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M) - Original model by hexgrad
- [GGML](https://github.com/ggerganov/ggml) - Tensor library by Georgi Gerganov
- [TTS.cpp](https://github.com/mmwillet/TTS.cpp) - Original multi-model TTS implementation

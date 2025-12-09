### Overview

This tool runs a series of benchmarks to test the generative throughput of the Kokoro TTS inference engine. Over 30 sentences, it measures:

- **Generation Time**: End-to-end mean generation time in milliseconds
- **Real Time Factor (RTF)**: Generation time divided by audio output duration (RTF < 1.0 means faster than real-time)

### Requirements

* `perf_battery` and the TTS library must be built
* A Kokoro GGUF model file (e.g., `Kokoro_no_espeak.gguf`)

### Usage

To see all available options:

```bash
./perf_battery --help

--n-threads (-nt):
    The number of CPU threads to run generation with. Defaults to 10.
--use-metal (-m):
    (OPTIONAL) Whether to use Metal acceleration (macOS only).
--model-path (-mp):
    (REQUIRED) The local path to the Kokoro GGUF model file.
```

### Example

Run the benchmark:

```bash
./perf_battery --model-path /path/to/Kokoro.gguf
```

With Metal acceleration (macOS):

```bash
./perf_battery --model-path /path/to/Kokoro.gguf --use-metal
```

### Sample Output

```
Mean Stats for arch Kokoro:

  Generation Time (ms):             9108.24
  Generation Real Time Factor:      2.17

```

### Interpreting Results

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Generation Time (ms)** | Average time to generate audio | Lower is better |
| **Real Time Factor** | How fast vs real-time playback | < 1.0 = faster than real-time |

A Real Time Factor of 0.5 means audio is generated 2x faster than it takes to play.

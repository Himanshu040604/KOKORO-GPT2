### Overview

This runs a RESTful HTTP server for the Kokoro TTS inference engine, providing an OpenAI-compatible `/v1/audio/speech` endpoint for generating speech. It supports model parallelism and request queuing.


### Requirements

* `tts-server` and the TTS library must be built
* A Kokoro GGUF model file

### Configuration

To see all available options:

```bash
./tts-server --help

--temperature (-t):
    (OPTIONAL) The temperature for generation. Defaults to 1.0.
--repetition-penalty (-r):
    (OPTIONAL) The repetition penalty for sampled output. Defaults to 1.0.
--top-p (-tp):
    (OPTIONAL) The sum of probabilities to sample over (0.0-1.0). Defaults to 1.0.
--topk (-tk):
    (OPTIONAL) Nucleus sampling size. Defaults to 50.
--n-threads (-nt):
    (OPTIONAL) Number of CPU threads for generation. Defaults to hardware concurrency.
--port (-p):
    (OPTIONAL) Server port. Defaults to 8080.
--n-http-threads (-ht):
    (OPTIONAL) Number of HTTP threads. Defaults to hardware concurrency minus 1.
--timeout (-to):
    (OPTIONAL) HTTP call timeout in seconds. Defaults to 300.
--n-parallelism (-np):
    (OPTIONAL) Number of parallel models for async processing. Defaults to 1.
--use-metal (-m):
    (OPTIONAL) Whether to use Metal acceleration (macOS only).
--model-path (-mp):
    (REQUIRED) Path to the Kokoro GGUF model file.
--ssl-file-cert (-sfc):
    (OPTIONAL) Path to PEM-encoded SSL certificate.
--ssl-file-key (-sfk):
    (OPTIONAL) Path to PEM-encoded SSL private key.
--host (-h):
    (OPTIONAL) Server hostname. Defaults to '127.0.0.1'.
--voice (-v):
    (OPTIONAL) Default voice for generation. See CLI README for available voices.
--espeak-voice-id (-eid):
    (OPTIONAL) espeak voice ID for phonemization (when auto-detection doesn't work).
```

### Quick Start

Start the server:

```bash
./tts-server --model-path /path/to/Kokoro.gguf
```

This runs the server on `http://127.0.0.1:8080`.

With a specific voice:

```bash
./tts-server --model-path /path/to/Kokoro.gguf --voice af_bella
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/audio/speech` | POST | Generate speech from text |
| `/v1/audio/voices` | GET | List available voices |

### Generate Speech

**POST** `/v1/audio/speech`

```bash
curl http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test of the Kokoro TTS server.",
    "voice": "af_bella",
    "response_format": "wav"
  }' \
  --output output.wav
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✅ Yes | The text to convert to speech |
| `voice` | string | No | Voice ID (e.g., `af_bella`, `am_adam`) |
| `temperature` | float | No | Sampling temperature (default: 1.0) |
| `top_k` | int | No | Nucleus sampling size (default: 50) |
| `repetition_penalty` | float | No | Repetition penalty (default: 1.0) |
| `response_format` | string | No | Output format: `wav` or `aiff` (default: `wav`) |

### List Voices

**GET** `/v1/audio/voices`

```bash
curl http://127.0.0.1:8080/v1/audio/voices
```

Returns a JSON list of all available Kokoro voices.

### Example with Python

```python
import requests

response = requests.post(
    "http://127.0.0.1:8080/v1/audio/speech",
    json={
        "input": "Hello from Python!",
        "voice": "af_heart",
        "response_format": "wav"
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### Future Work

* Token authentication and permissions
* Streaming audio for long-form generation
* WebSocket support for real-time synthesis

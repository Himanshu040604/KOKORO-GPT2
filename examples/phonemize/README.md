### Overview

This CLI tool converts text to phonemes (IPA format) for use with the Kokoro TTS model. Phonemization is the process of converting written text into phonetic representations that the TTS model uses to generate speech.

### Requirements

* `phonemize` tool and library must be built
* Either:
  - A Kokoro GGUF model with embedded phonemization rules, OR
  - espeak-ng installed on your system (for espeak-based phonemization)

### Usage

To see all available options:

```bash
./phonemize --help

--use-espeak (-ue):
    (OPTIONAL) Whether to use espeak-ng to generate phonemes.
--phonemizer-path (-mp):
    (OPTIONAL) The local path to a GGUF file containing phonemization rules. Required if not using espeak.
--prompt (-p):
    (REQUIRED) The text prompt to phonemize.
--espeak-voice-id (-eid):
    (OPTIONAL) The voice ID to use for espeak phonemization. Defaults to 'gmw/en-US'.
```

### Examples

#### Using Built-in Phonemizer

```bash
./phonemize --phonemizer-path "/path/to/phonemizer.gguf" --prompt "Hello, how are you?"
```

#### Using espeak-ng

If you built with espeak support:

```bash
./phonemize --prompt "Hello, how are you?" --use-espeak
```

With a specific language/voice:

```bash
./phonemize --prompt "Bonjour le monde" --use-espeak --espeak-voice-id "fr"
```

### Sample Output

```
Input:  "Hello, how are you?"
Output: "həˈloʊ, haʊ ɑːɹ juː?"
```

### Supported Languages

When using espeak-ng, you can phonemize text in multiple languages. Use `--espeak-voice-id` to specify the language:

| Voice ID | Language |
|----------|----------|
| `gmw/en-US` | American English (default) |
| `gmw/en` | British English |
| `fr` | French |
| `de` | German |
| `es` | Spanish |
| `it` | Italian |
| `ja` | Japanese |
| `zh` | Mandarin Chinese |

To see all available espeak voices:

```bash
espeak-ng --voices
```

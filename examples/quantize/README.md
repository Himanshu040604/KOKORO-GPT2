### Overview

This tool converts a 32-bit floating point Kokoro TTS GGUF model to a quantized format. [Quantization](https://huggingface.co/docs/optimum/en/concept_guides/quantization) reduces the precision of model weights to decrease memory usage and improve inference speed, with minimal impact on audio quality.

**WARNING**: Quantization to formats smaller than Q4_0 is not recommended. Importance matrices are not currently supported.
 
### Requirements

* `quantize` tool and the TTS library must be built 
* A Kokoro GGUF model file

### Usage

To see all available options:

```bash
./quantize --help

--quantized-type (-qt):
    (OPTIONAL) The GGML quantization type. Defaults to Q4_0 (value: 2). See table below.
--n-threads (-nt):
    (OPTIONAL) The number of CPU threads to use. Defaults to hardware concurrency.
--convert-non-quantized-to-f16 (-nqf):
    (OPTIONAL) Whether to convert non-quantizable tensors to 16-bit precision. Defaults to false.
--quantize-output-heads (-qh):
    (OPTIONAL) Whether to quantize the output heads. Defaults to false.
--model-path (-mp):
    (REQUIRED) The path to the input Kokoro GGUF model file.
--quantized-model-path (-qp):
    (REQUIRED) The path to save the quantized model.
```

### Example

Quantize a model using Q5_0 (recommended for best quality/speed balance):

```bash
./quantize --model-path /path/to/Kokoro.gguf --quantized-model-path /path/to/Kokoro_q5.gguf --quantized-type 6
```

Convert to F16 (half precision, smaller but no quality loss):

```bash
./quantize --model-path /path/to/Kokoro.gguf --quantized-model-path /path/to/Kokoro_f16.gguf --quantized-type 1
```

### Quantization Types

The `--quantized-type` parameter accepts these values:

| Value | Type | Description | Recommended |
|-------|------|-------------|-------------|
| 1 | F16 | 16-bit float (no quality loss) | Good |
| 2 | Q4_0 | 4-bit quantization | Faster but lower quality |
| 6 | Q5_0 | 5-bit quantization | Best balance |
| 7 | Q5_1 | 5-bit quantization (variant) | Good |
| 8 | Q8_0 | 8-bit quantization | High quality |
| 10 | Q2_K | 2-bit K-quant | Not recommended |
| 11 | Q3_K | 3-bit K-quant | Use with caution |
| 12 | Q4_K | 4-bit K-quant | Good |
| 13 | Q5_K | 5-bit K-quant | Recommended |
| 14 | Q6_K | 6-bit K-quant | High quality |

### Recommendations for Kokoro

For Kokoro TTS models:

| Use Case | Recommended Type | Command |
|----------|------------------|---------|
| **Best Quality** | Q8_0 or F16 | `--quantized-type 8` |
| **Balanced** | Q5_0 or Q5_K | `--quantized-type 6` |
| **Smallest Size** | Q4_0 or Q4_K | `--quantized-type 2` |

### Performance Benefits

Quantization improves inference speed and reduces memory usage:

| Format | Model Size | Speed | Quality |
|--------|------------|-------|---------|
| F32 (original) | 100% | Baseline | Best |
| F16 | ~50% | ~1.2x faster | Excellent |
| Q8_0 | ~25% | ~1.5x faster | Very Good |
| Q5_0 | ~18% | ~1.8x faster | Good |
| Q4_0 | ~15% | ~2x faster | Acceptable |

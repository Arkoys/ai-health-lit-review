# Local Installation Guide (Ollama)

This guide explains how to run the AI Health Literature Review system entirely locally using Ollama, avoiding API costs and rate limits.

## Requirements

- **Linux/macOS/Windows** with Python 3.10+
- **NVIDIA GPU** (recommended) with at least 8GB VRAM for 7B-8B models
  - RTX 3060 Ti (8GB) can run `llama3:8b`, `mistral:7b`, `phi3:mini`
- **Or CPU-only** (slower, but works with smaller models like `phi3:mini`)

## 1. Install Ollama

### Ubuntu/Debian
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### macOS
```bash
brew install ollama
```

### Windows
Download from https://ollama.com/download/windows

After installation, start the Ollama service:
```bash
# Linux (systemd)
systemctl --user start ollama
systemctl --user enable ollama

# Or run manually
ollama serve
```

## 2. Download a Model

Choose a model that fits your VRAM:

| Model | Size | Quality | Recommended VRAM |
|-------|------|---------|------------------|
| `llama3:8b` | 8B | Excellent | 8GB (4-bit) |
| `mistral:7b` | 7B | Very Good | 6GB (4-bit) |
| `phi3:mini` | 3.8B | Good | 4GB (4-bit) |
| `gemma:7b` | 7B | Good | 6GB (4-bit) |

Download the model:
```bash
ollama pull llama3:8b
```

Wait for download to complete (4-8GB depending on model).

## 3. Configure the Project

Edit `config.yaml`:

```yaml
providers:
  ollama:
    enabled: true        # <-- Enable Ollama
    model: llama3:8b     # <-- Your downloaded model
  # Disable other providers or set enabled: false
  openai:
    enabled: false
  gemini:
    enabled: false
  openrouter:
    enabled: false
  huggingface:
    enabled: false
```

## 4. Test Ollama Connection

First, make sure Ollama is running and the model is available:

```bash
# Check running models
curl http://localhost:11434/api/tags

# Expected output: {"models":[{"name":"llama3:8b",...}]}
```

Then test with Python:

```bash
python3 -c "
import requests
r = requests.post('http://localhost:11434/v1/chat/completions', json={
    'model': 'llama3:8b',
    'messages': [{'role': 'user', 'content': 'Say OK'}],
    'max_tokens': 5
})
print(r.json()['choices'][0]['message']['content'])
"
```

Should print `OK` or similar.

## 5. Run the System

```bash
# Activate virtual environment if you created one
source venv/bin/activate

# Test summarization only
python run_daily.py --test-summarize

# Run full pipeline (collect, summarize, report)
python run_daily.py
```

## 6. Performance Expectations

- **llama3:8b**: ~20-40 tokens/sec on RTX 3060 Ti (4-bit quantized)
- **mistral:7b**: ~25-50 tokens/sec on RTX 3060 Ti
- **phi3:mini**: ~50-100 tokens/sec (fast, but lower quality)

For 10 papers/day × ~300 words each, expect:
- Total inference time: ~5-15 minutes depending on model
- No external API calls, everything stays on your machine

## 7. Troubleshooting

### "Ollama not running" error
Make sure the Ollama service is started:
```bash
ollama serve  # in a terminal
# Or as a service
systemctl --user status ollama
```

### Out of memory
If you get CUDA out-of-memory errors:
- Use a smaller model (`phi3:mini` instead of `llama3:8b`)
- Or use 4-bit quantization (Ollama does this automatically)
- Reduce `max_words` in config (ex: 150 instead of 300)

### Slow inference
- Ensure you're using GPU (check `nvidia-smi` while running)
- Use a quantized model (Ollama defaults to Q4_K_M)
- Close other GPU-intensive applications

### Connection refused
Ollama binds to `localhost:11434`. Make sure firewall isn't blocking:
```bash
curl http://localhost:11434/api/tags
```
Should return JSON, not connection error.

## 8. Multi-provider Setup (Fallback)

You can combine Ollama with cloud providers as fallback:

```yaml
providers:
  ollama:
    enabled: true
    model: llama3:8b
  gemini:
    enabled: true  # Fallback if Ollama down
    model: gemini-2.0-flash
```

The system will try Ollama first, then Gemini if Ollama fails.

## Notes

- Ollama stores downloaded models in `~/.ollama/models/`
- To list models: `ollama list`
- To remove a model: `ollama rm llama3:8b`
- To update a model: `ollama pull llama3:8b` (re-downloads if newer version)

---

**Enjoy your fully local, private, and unlimited AI literature review!** 🚀
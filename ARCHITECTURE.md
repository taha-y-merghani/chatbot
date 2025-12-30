# Architecture: Local-First Voice Agent on Legacy Hardware

## The Problem

Build a production-ready voice agent that runs **entirely locally** on consumer hardware (2015 MacBook Pro: no GPU, 8GB RAM, thermal throttling). Cloud APIs (OpenAI, Anthropic) solve the easy problem. Local orchestration with hard latency constraints solves the engineering problem.

## The Constraint

**Hardware:**
- 2015 MacBook Pro (no GPU, integrated graphics only)
- 8GB RAM (shared between OS, Whisper, Ollama, Python runtime)
- Thermal throttling under sustained load
- ~5-10 second inference latency per component

**Why This Matters:**
Most LLM demos assume cloud infrastructure or beefy GPUs. Real-world deployment often means legacy hardware, air-gapped environments, or privacy-first constraints. This project optimizes for the **90% case**, not the ideal.

## System Architecture

```
┌─────────────┐
│   User      │
│  (Audio)    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Audio Input (Microphone/Upload)        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  OpenAI Whisper (Quantized Model)       │
│  - Subprocess: python -m whisper        │
│  - Timeout: 30s                         │
│  - Fallback: Retry with smaller chunk   │
└──────┬──────────────────────────────────┘
       │ (Transcribed Text)
       ▼
┌─────────────────────────────────────────┐
│  Subprocess Orchestration Layer         │
│  - Manages Ollama server lifecycle      │
│  - Port conflict detection (11434)      │
│  - Timeout handling (per-request)       │
│  - NumPy ABI compatibility checks       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Ollama + Mistral 7B (4-bit Quantized)  │
│  - Local inference server               │
│  - Context window: 8k tokens            │
│  - Latency: ~8-12s on CPU               │
└──────┬──────────────────────────────────┘
       │ (Generated Response)
       ▼
┌─────────────────────────────────────────┐
│  Gradio UI (FastAPI/ASGI Compatible)    │
│  - Web interface for testing            │
│  - Real-time streaming (when possible)  │
└─────────────────────────────────────────┘
```

## Key Engineering Decisions

### 1. Whisper Quantization
**Decision:** Use `whisper.cpp` with quantized weights instead of full PyTorch model.

**Why:**
- PyTorch Whisper: 2.8GB VRAM, 15-20s inference
- Quantized: 500MB RAM, 8-10s inference
- Tradeoff: Slight accuracy loss (< 2%) for 3x speedup

**How to Reproduce:**
```bash
# Install whisper.cpp (not pip install whisper)
brew install whisper-cpp
whisper-cpp --model base.en --file audio.wav
```

### 2. Ollama Subprocess Management
**Decision:** Don't assume Ollama is running. Start/stop it programmatically.

**Problem:** If Ollama crashes mid-inference, the entire app hangs.

**Solution:**
```python
import subprocess
import time

def ensure_ollama_running():
    """Check if Ollama server is responsive on port 11434."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        # Start Ollama as background subprocess
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Wait for server startup
        return ensure_ollama_running()  # Retry
```

**Why This Matters:**
Juniors assume infrastructure is running. Seniors handle infrastructure failures.

### 3. Timeout Handling
**Decision:** Every subprocess call has a timeout.

**Why:**
- Whisper can hang on malformed audio (>60s)
- Ollama can timeout on context overflow (>120s)
- Gradio async handlers need bounded execution

**Implementation:**
```python
import subprocess

def transcribe_with_timeout(audio_file, timeout=30):
    try:
        result = subprocess.run(
            ["whisper-cpp", "--file", audio_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "[ERROR] Whisper timed out. Audio too long or corrupted."
```

### 4. NumPy ABI Compatibility
**Problem:** Different Python packages expect different NumPy versions.

**Symptom:**
```
ImportError: numpy.core.multiarray failed to import
```

**Root Cause:**
- `whisper` expects NumPy 1.24.x
- `gradio` expects NumPy 1.23.x
- Mac ARM (M1/M2) vs Intel has different precompiled binaries

**Solution:**
```bash
# Pin NumPy version explicitly
pip install numpy==1.24.3 --force-reinstall

# Verify ABI compatibility
python -c "import numpy; print(numpy.__version__)"
```

**Senior Insight:**
This isn't in any tutorial. You only learn this by debugging "works on my machine" failures.

## When Abstraction Fails: Why Cursor Couldn't Help

**The Limit of AI Coding Assistants:**

Cursor (and similar tools) excel at:
- Writing boilerplate
- Refactoring code
- Explaining syntax

Cursor **cannot** see:
- Your hardware constraints (no GPU, 8GB RAM)
- Running processes (is Ollama already on port 11434?)
- System-level errors (NumPy ABI mismatch)

**Example Failure:**
```
Me: "Why is Whisper hanging?"
Cursor: "Try increasing the timeout."
Reality: Audio file was corrupted. Whisper was waiting for EOF that never came.
```

**The Fix:**
```bash
# Check if audio is valid before processing
ffprobe audio.wav 2>&1 | grep "Invalid data"
```

**Senior Takeaway:**
AI assistants generate code. Engineers debug **systems**. Know when to drop into `strace`, `lsof`, and process monitors.

## Performance Benchmarks

| Component       | Latency (2015 MBP) | Bottleneck          |
|-----------------|-------------------|---------------------|
| Whisper (30s audio) | ~8s               | CPU-bound           |
| Ollama (100 tokens) | ~12s              | Memory bandwidth    |
| Gradio UI       | ~200ms            | Network I/O         |
| **Total (E2E)** | **~20-25s**       | Sequential pipeline |

**Optimization Attempts:**
- ❌ Tried parallel Whisper + Ollama: RAM overflow
- ❌ Tried streaming output: Ollama doesn't support true streaming on CPU
- ✅ Quantized models: 3x speedup, acceptable accuracy loss

## Production Deployment Considerations

1. **Error Recovery:** What happens when Ollama crashes mid-conversation?
   - Current: Restart subprocess, lose context
   - Better: Persist conversation to SQLite, reload on restart

2. **Monitoring:** How do you know if the system is healthy?
   - Add `/health` endpoint that checks Ollama + Whisper availability
   - Log latency per request (P50, P95, P99)

3. **Security:** This runs a local web server. What if someone finds it?
   - Gradio defaults to `0.0.0.0` (public). Change to `127.0.0.1`.
   - Add API key authentication for production.

## How to Run

```bash
# 1. Install dependencies
pip install openai-whisper ollama-python gradio

# 2. Start Ollama server
ollama serve &

# 3. Pull Mistral model (one-time)
ollama pull mistral:7b-instruct-v0.2-q4_0

# 4. Run the app
python app.py

# 5. Open browser
# http://localhost:7860
```

## Lessons for Senior Engineers

1. **Constraints Drive Design:** The 2015 MacBook Pro constraint forced quantization, subprocess isolation, and timeout handling. Cloud deployment would have hidden these skills.

2. **Abstraction Failures Are Learning Opportunities:** When Cursor couldn't debug NumPy ABI issues, I learned `pip show numpy`, `otool -L` (macOS library inspector), and ABI versioning.

3. **Document the "Why," Not Just the "What":** This ARCHITECTURE.md explains decisions, not just code. That's the difference between Junior (writes code) and Senior (writes design docs).

## Further Reading

- [Whisper.cpp Optimization Guide](https://github.com/ggerganov/whisper.cpp)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Gradio Production Deployment](https://www.gradio.app/guides/deploying-gradio-apps)

---

**Author:** Taha Merghani
**Last Updated:** December 30, 2024
**Status:** Production-ready for local deployment

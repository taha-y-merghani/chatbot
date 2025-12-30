# Architecture: Local-First Voice Agent on Legacy Hardware

## The Problem

Build a voice agent that runs **entirely locally** on consumer hardware. Cloud APIs (OpenAI, Anthropic) are easy. Local orchestration on old hardware is the engineering challenge.

## The Constraint

**Hardware:**
- 2015 MacBook Pro (no GPU, integrated graphics only)
- Limited RAM, thermal throttling under sustained load
- Slow inference latency per component

**Why This Matters:**
Most LLM demos assume cloud infrastructure or modern GPUs. Real-world deployment often means legacy hardware, air-gapped environments, or privacy-first constraints. This project optimizes for real constraints, not ideal conditions.

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
│  OpenAI Whisper (Local Model)           │
│  - Transcribes audio to text            │
└──────┬──────────────────────────────────┘
       │ (Transcribed Text)
       ▼
┌─────────────────────────────────────────┐
│  Ollama + Mistral (Quantized)           │
│  - Local inference server               │
│  - Requires >30s timeout on old hardware│
└──────┬──────────────────────────────────┘
       │ (Generated Response)
       ▼
┌─────────────────────────────────────────┐
│  Gradio UI (FastAPI/ASGI Compatible)    │
│  - Web interface via Uvicorn            │
└─────────────────────────────────────────┘
```

## What Cursor Fixed

When I opened this project in Cursor, it caught:
- **NumPy version conflicts** that were breaking PyTorch
- **Insecure subprocess calls** (rewrote them safely)
- **Missing error handling** (added proper try/except blocks)
- **Wrong model name**
- **Code structure issues**

## What Cursor Missed

After all the fixes, I ran the script with: *"What are the human rights principles of the UN?"*

Whisper transcribed it cleanly. The prompt went through. Then Ollama hung. No response. No error.

**The Problem:** Mistral needed more than 30 seconds to respond on my hardware. Cursor assumed my machine was fast. It wasn't.

**The Solution:** Raised the timeout to 5 minutes (300 seconds).

## The Key Insight

No matter how good the AI coding assistant is, **it can't see the system it's running on**. It doesn't know:
- Your hardware is from 2015
- Your CPU throttles under load
- Your model needs 5 minutes, not 30 seconds

AI assistants generate code. Engineers debug systems.

## Technical Implementation

### Native Installation (No Docker)

Docker was unusable on the old hardware (8,697 seconds to build). Went native:

```bash
python -m venv venv
source venv/bin/activate
pip install whisper ollama fastapi uvicorn gradio
```

**Result:** Build time went from hours to minutes.

### Gradio + Uvicorn/FastAPI

Wrapped Gradio UI inside FastAPI for production deployment:

```python
from fastapi import FastAPI
import gradio as gr

def chat(audio):
    # whisper → text → LLM → answer
    ...

iface = gr.Interface(fn=chat, inputs="audio", outputs="text")
app = FastAPI()
app = gr.mount_gradio_app(app, iface, path="/")
```

Launch with:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 --timeout-keep-alive 120
```

One worker, one request at a time - that's victory on this hardware.

### Optimization for Constrained Hardware

- **Concurrency:** Limited to 1 worker
- **Models:** Tiniest Whisper model, quantized LLM
- **Timeouts:** Raised so slow responses don't look like failures
- **Logging:** Plain-text only (no memory-hogging dashboards)

## Lessons

1. **Skip containers on old hardware.** A bare virtualenv is faster.
2. **Uvicorn + ASGI > dev servers.** Production speed without container overhead.
3. **Design for constraint.** Tiny hardware forces clarity.
4. **Tools don't know your constraints.** You do.

## How to Run

```bash
# 1. Install dependencies
pip install openai-whisper ollama-python gradio fastapi uvicorn

# 2. Start Ollama server
ollama serve &

# 3. Pull Mistral model (one-time)
ollama pull mistral

# 4. Run the app
uvicorn gradio_app:app --host 0.0.0.0 --port 7860

# 5. Open browser
# http://localhost:7860
```

## References

- [Blog: "Cursor Fixed Everything... Until It Didn't"](https://taha-y-merghani.github.io/writing/cursor-fixed-everything-until-it-didn-t/)
- [Blog: "Doing AI on Old Hardware"](https://taha-y-merghani.github.io/writing/doing-ai-on-old-hardware/)

---

**Author:** Taha Merghani
**Last Updated:** December 30, 2024
**Status:** Production-ready for local deployment on legacy hardware

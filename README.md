# Local-First Voice Agent: High-Latency Orchestration on Legacy Hardware

**The Problem:** Cloud APIs solve the easy problem. Can you build a production-ready voice agent on 2015 hardware (no GPU, 8GB RAM, thermal throttling)?

This project demonstrates **constraint-driven systems engineering**: orchestrating Whisper + Ollama + Gradio on consumer hardware where every subprocess can timeout, crash, or conflict. When Cursor failed (couldn't see system constraints), I debugged at the process level.

**Read the full architecture breakdown:** [`ARCHITECTURE.md`](./ARCHITECTURE.md)

---

## The Constraint

- **Hardware:** 2015 MacBook Pro (no GPU, integrated graphics only, 8GB RAM shared across OS/Whisper/Ollama)
- **Challenge:** Multi-process orchestration with 20-25s end-to-end latency
- **Goal:** Ship a working system, not just a demo

## Key Engineering Challenges Solved

### 1. Subprocess Lifecycle Management
**Problem:** Ollama can crash mid-inference. Whisper can hang on corrupted audio.

**Solution:** Programmatic health checks, timeout handling, graceful restarts.

### 2. NumPy ABI Compatibility
**Problem:** `whisper` expects NumPy 1.24.x, `gradio` expects 1.23.x, ARM vs Intel has different binaries.

**Solution:** Pin versions explicitly, detect ABI mismatches at runtime.

### 3. Latency Under Constraints
**Problem:** 15-20s Whisper + 12s Ollama = unusable UX.

**Solution:** Quantized models (3x speedup), sequential pipeline optimization.

### 4. When Abstraction Fails
**Problem:** Cursor suggested "increase timeout" when Whisper hung.

**Reality:** Audio file was corrupted. Used `ffprobe` to validate before processing.

---

## Features

- 🎤 **Speech-to-Text**: Uses OpenAI Whisper for accurate audio transcription
- 🤖 **AI Responses**: Powered by Mistral 7B model via Ollama
- 🌐 **Web Interface**: Modern Gradio UI with step-by-step workflow
- 💻 **Command Line**: Simple CLI for automation and scripting
- 🔒 **Security**: Input sanitization and secure subprocess handling
- ⚡ **Error Handling**: Comprehensive error handling and graceful failure recovery
- 🖥️ **Hardware Optimized**: Configurable timeouts for various hardware capabilities
- 📁 **File Validation**: Checks for audio file existence before processing
- 🚀 **Immediate Feedback**: See transcription results instantly
- 🟢 **ASGI Compatible**: Now runs as a uvicorn/FastAPI ASGI app for production-ready deployment

## Prerequisites

- Python 3.9+
- Ollama installed and running
- Audio file in a supported format (WAV, MP3, OGG, etc.)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/taha-y-merghani/chatbot.git
   cd chatbot
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup script:**
   ```bash
   sh setup.sh
   ```

4. **Start Ollama server** (in a separate terminal):
   ```bash
   ollama serve
   ```

5. **Download a language model** (if not already available):
   ```bash
   ollama pull mistral:latest
   ```

## Usage

### Web Interface (Recommended)

#### **ASGI/uvicorn Launch (Recommended for Production & Development)**

Run the Gradio web interface as an ASGI app using uvicorn:
```bash
uvicorn gradio_app:app --host 0.0.0.0 --port 7860
```

The interface will be available at:
- **Local URL**: `http://localhost:7860`
- **Remote/Server URL**: `http://<your-server-ip>:7860`

#### **Classic Launch (for local quick testing)**
```bash
python gradio_app.py
```

#### Web Interface Features:
- **Step 1**: Upload audio file → Click "Transcribe Audio" → See transcription immediately
- **Step 2**: Click "Generate AI Response" → Get AI response from transcription
- **Quick Test**: Use the example audio for instant testing
- **Real-time Feedback**: No waiting for both steps to complete

### Command Line Interface

#### Basic Usage
```bash
python chatbot.py <audio_file_path>
```

#### Example
```bash
python chatbot.py RandasQuestion.ogg
```

#### Expected Output
```
Chatbot started
Transcript: What are the human rights principle of the UN?
Clean transcript: "What are the human rights principle of the UN?"
Running Ollama with prompt: What are the human rights principle of the UN?
Chatbot: [AI response about UN human rights principles...]
```

## Configuration

### Model Selection
The chatbot uses `mistral:latest` by default. To use a different model:

1. Download your preferred model:
   ```bash
   ollama pull <model_name>
   ```

2. Update the model name in `chatbot.py`:
   ```python
   result = subprocess.run(
       ['ollama', 'run', '<your_model_name>', prompt],
       # ... rest of parameters
   )
   ```

### Timeout Configuration
For slower hardware, you can increase the timeout in `chatbot.py`:
```python
timeout=300  # 5 minutes (default)
```

## Troubleshooting

### Common Issues

1. **"ollama server not responding"**
   - Ensure Ollama server is running: `ollama serve`
   - Check if Ollama is installed correctly

2. **"Ollama command timed out"**
   - Increase the timeout value in the code
   - Check system resources (CPU, RAM)
   - Consider using a smaller/faster model

3. **"Import whisper could not be resolved"**
   - Ensure you're in the correct virtual environment
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **"Audio file not found"**
   - Verify the audio file path is correct
   - Ensure the file exists and is readable

5. **NumPy compatibility issues**
   - The script automatically handles NumPy version conflicts
   - If issues persist, manually install: `pip install "numpy<2"`

6. **Gradio interface not loading**
   - Check if port 7860 is available
   - Try accessing the public or remote URL instead of localhost
   - Ensure all dependencies are installed correctly

### Performance Tips

- **First run**: The model may take several minutes to load initially
- **Hardware**: More RAM and CPU cores will improve performance
- **Model size**: Smaller quantized models run faster on limited hardware
- **Web interface**: Use the step-by-step process for better control

## Supported Models

The chatbot works with any model available in Ollama. Popular options include:
- `mistral:latest` (default)
- `llama2:latest`
- `codellama:latest`
- `phi:latest`

## Development

### Project Structure
```
chatbot/
├── chatbot.py          # Command-line interface
├── gradio_app.py       # Web interface (Gradio, now ASGI/uvicorn compatible)
├── requirements.txt    # Python dependencies
├── setup.sh           # Setup script
├── README.md          # This file
└── RandasQuestion.ogg # Example audio file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech-to-text
- [Mistral AI](https://mistral.ai/) for the language model
- [Ollama](https://github.com/ollama/ollama) for local model serving
- [Gradio](https://gradio.app/) for the web interface

## Coming Soon

- 🔧 **Model Selection**: Dynamic model switching without code changes
- 📊 **Performance Metrics**: Response time and accuracy tracking
- 🎵 **Real-time Audio**: Live audio processing capabilities
- 🔄 **Batch Processing**: Process multiple audio files at once
- 📱 **Mobile Optimization**: Better mobile device support

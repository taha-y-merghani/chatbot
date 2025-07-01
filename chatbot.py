import os
import whisper
import sys
import subprocess
import shlex

def speech2text(audio_path):
    """
    Function to transcribe an audio file to text using OpenAI Whisper locally
    """
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def prompt2answer(prompt):
    """
    Function to answer question by autocompletion using Ollama
    """
    try:
        # Sanitize the prompt to prevent shell injection
        sanitized_prompt = shlex.quote(prompt)
        print(f"Running Ollama with prompt: {prompt}")
        result = subprocess.run(
            ['ollama', 'run', 'mistral:latest', prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minutes
        )
        
        if result.returncode != 0:
            print(f"Error running Ollama: {result.stderr}")
            return None
            
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Ollama command timed out")
        return None
    except Exception as e:
        print(f"Error running Ollama: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python chatbot.py <audio_file_path>")
        sys.exit(1)

    print("Chatbot started")
    audio_path = sys.argv[1]
    
    # Check if audio file exists
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found")
        sys.exit(1)
    
    transcript = speech2text(audio_path)
    if transcript is None:
        print("Failed to transcribe audio")
        sys.exit(1)
        
    print(f'Transcript: {transcript}')
    
    # Ensure transcript is a string and strip whitespace
    if isinstance(transcript, str):
        clean_transcript = transcript.strip()
    else:
        clean_transcript = str(transcript).strip()
    
    print(f'Clean transcript: "{clean_transcript}"')
    
    response = prompt2answer(clean_transcript)
    if response is None:
        print("Failed to get response from Ollama")
        sys.exit(1)
        
    print(f"Chatbot: {response}")

if __name__ == '__main__':
    main()
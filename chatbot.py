import os
import whisper
import sys
import subprocess

def speech2text(audio_path):
  '''
  Function to transcribe an audio file to text using OpenAI Speech API or locally 
  '''
  return whisper.load_model("base").transcribe(audio_path)["text"]
def prompt2answer(prompt):
  """ 
  Function to answer question by autocompletion 
  """
  result = subprocess.run([f"""
  ollama run mistral "{prompt}" """], shell=True,  stdout=subprocess.PIPE, text=True)
  return result.stdout

def main():
    if len(sys.argv) < 2:
        print("Usage: script.py <audio_file_path>")
        sys.exit(1)

    print("Chatbot started")
    audio_path = sys.argv[1]
    transcript = speech2text(audio_path)
    print(f'Transcript: {transcript}')
    prompt = transcript
    response = prompt2answer(prompt)
    print(f"Chatbot: {response}")

if __name__ == '__main__':
  main()
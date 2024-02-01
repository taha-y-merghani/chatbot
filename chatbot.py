import openai
import os
import whisper
import sys
import subprocess
def get_api_key():
    return os.environ["OPENAI_API_KEY"]
def speech2text(audio_path, model="whisper-1", api_key=get_api_key(), locally=False):
  '''
  Function to transcribe an audio file to text using OpenAI Speech API or locally 
  '''
  if locally:
    print('locally ...')
    return whisper.load_model("base").transcribe(audio_path)["text"]
  client = openai.OpenAI(api_key=api_key)
  audio_file = open(audio_path, "rb")
  transcript = client.audio.transcriptions.create( 
    model=model,
    file=audio_file
  )
  return transcript.text
def prompt2answer(prompt, model="gpt-4", api_key=get_api_key(), locally=False):
  """ 
  Function to answer question by autocompletion 
  """
  if locally:
    print('locally ...')
    result = subprocess.run([f"""
    llama.cpp/main 2>/dev/null -e -p "{prompt}" -m "../models/mistral-7b-instruct-v0.1.Q6_K.gguf" -ngl 30000"""], shell=True,  stdout=subprocess.PIPE, text=True)
    return result.stdout
  client = openai.OpenAI(api_key=api_key)
  completion = client.chat.completions.create(
    model=model,messages=
    [ {"role": "system", "content": prompt} ]
  )
  return completion.choices[0].message.content


def main():
    if len(sys.argv) < 2:
        print("Usage: script.py <audio_file_path>")
        sys.exit(1)

    print("Chatbot started")
    audio_path = sys.argv[1]
    transcript = speech2text(audio_path, locally=True)
    print(f'Transcript: {transcript}')
    prompt = transcript
    response = prompt2answer(prompt, locally=True)
    print(f"Chatbot: {response}")

if __name__ == '__main__':
  main()
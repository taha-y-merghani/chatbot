import openai
import os
def speech2text(audio_path, model="whisper-1", api_key=os.environ["OPENAI_API_KEY"]):
  '''
  Function to transcribe an audio file to text using OpenAI Speech API
  '''
  client = openai.OpenAI(api_key=api_key)
  audio_file = open(audio_path, "rb")
  transcript = client.audio.transcriptions.create( 
    model=model,
    file=audio_file
  )
  return transcript.text
def prompt2answer(prompt, model="gpt-4", api_key=os.environ["OPENAI_API_KEY"]):
  client = openai.OpenAI(api_key=api_key)
  completion = client.chat.completions.create(
    model=model,messages=
    [ {"role": "system", "content": prompt} ]
  )
  return completion.choices[0].message.content


  
def main():
  print("Chatbot started")
  audio_path = "recordings/CapitalOfSudan.m4a"
  transcript = speech2text(audio_path)
  print(f'Transcript: {transcript}')
  prompt = transcript
  response = prompt2answer(prompt)
  print(f"Chatbot: {response}")

if __name__ == '__main__':
  main()
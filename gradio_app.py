import gradio as gr
from chatbot import speech2text, prompt2answer

# Add FastAPI import for ASGI compatibility
from fastapi import FastAPI

def transcribe_audio(audio_file):
    """
    Transcribe audio file only
    """
    if audio_file is None:
        return "No audio file uploaded"
    
    transcribed_text = speech2text(audio_file)
    if transcribed_text is None:
        return "Error: Could not transcribe the audio file."
    
    return transcribed_text

def generate_ai_response(transcribed_text):
    """
    Generate AI response from transcribed text
    """
    if not transcribed_text or transcribed_text == "No audio file uploaded" or transcribed_text.startswith("Error:"):
        return "Please transcribe an audio file first."
    
    answer = prompt2answer(transcribed_text)
    if answer is None:
        return "Error: Could not generate AI response."
    
    return answer

# Create a Gradio interface with separate steps
with gr.Blocks(title="Audio-to-AI Chatbot") as demo:
    gr.Markdown("# 🎤 Audio-to-AI Chatbot")
    gr.Markdown("Step 1: Upload audio and transcribe. Step 2: Generate AI response from transcription.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Step 1: Upload & Transcribe")
            audio_input = gr.Audio(type="filepath", label="Upload Audio File")
            transcribe_btn = gr.Button("🎵 Transcribe Audio", variant="primary")
            transcription_output = gr.Textbox(label="Transcription", lines=4, placeholder="Transcribed text will appear here...")
        
        with gr.Column():
            gr.Markdown("### Step 2: Generate AI Response")
            ai_btn = gr.Button("🤖 Generate AI Response", variant="secondary")
            answer_output = gr.Textbox(label="AI Response", lines=10, placeholder="AI response will appear here...")
    
    # Event handlers
    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=audio_input,
        outputs=transcription_output
    )
    
    ai_btn.click(
        fn=generate_ai_response,
        inputs=transcription_output,
        outputs=answer_output
    )
    
    # Example section
    gr.Markdown("---")
    gr.Markdown("### 🚀 Quick Test")
    example_audio = gr.Audio(value="./RandasQuestion.ogg", type="filepath", label="Example Audio")
    example_transcribe_btn = gr.Button("Transcribe Example", variant="primary")
    example_ai_btn = gr.Button("Generate AI Response", variant="secondary")
    example_transcription = gr.Textbox(label="Example Transcription", lines=3)
    example_answer = gr.Textbox(label="Example AI Response", lines=8)
    
    example_transcribe_btn.click(
        fn=transcribe_audio,
        inputs=example_audio,
        outputs=example_transcription
    )
    
    example_ai_btn.click(
        fn=generate_ai_response,
        inputs=example_transcription,
        outputs=example_answer
    )

# Mount Gradio app as ASGI app for uvicorn compatibility
app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

# Launch the app if run directly
if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
# What is this?

This is just a mini chatbot run locally with a speech2text interface with [openai's whisper](https://github.com/openai/whisper), and it answers using [mistral 7b](https://mistral.ai/news/announcing-mistral-7b/).

This app was tested primarily on Google Colab Pro's NVIDIA V100 GPU, but I would be curious to see your experience!

## Usage:
`pip install -r requirements.txt`

`sh setup.sh`

In a seperate terminal run:
`ollama serve`

Return to the first terminal and run on the example audio file provided.
 `python chatbot.py RandasQuestion.ogg`

 Coming soon:
- UI with gradio
- full control for LLMs other than mistral that are supported by [ollama](https://github.com/ollama/ollama)

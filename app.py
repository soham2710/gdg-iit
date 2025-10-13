import os
from flask import Flask, render_template, request, jsonify, redirect
from google import genai
from google.genai import types

app = Flask(__name__)

PROJECT_ID = "gdg-iit"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="us-central1",
)

@app.route('/')
def index():
    return render_template('index.html')

def generate(youtube_link, model, additional_prompt):
    youtube_video = types.Part.from_uri(
        file_uri=youtube_link,
        mime_type="video/*",
    )

    if not additional_prompt:
        additional_prompt = " "

    contents = [
        youtube_video,
        types.Part.from_text(text="Provide a summary of the video."),
        additional_prompt,
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
    )

    return client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    ).text

@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_link = request.form.get('youtube_link')
    model = request.form.get('model')
    additional_prompt = request.form.get('additional_prompt')

    try:
        summary = generate(youtube_link, model, additional_prompt)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)

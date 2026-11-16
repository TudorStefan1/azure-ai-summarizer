import os
from flask import Flask, request, render_template_string
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

app = Flask(__name__)

ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

client = None
if ENDPOINT and DEPLOYMENT:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )

PAGE = """
<!doctype html>
<title>AI Summarizer</title>
<h1>Text Summarizer</h1>
<form method="post">
  <textarea name="text" rows="10" cols="70"
    placeholder="Paste text here...">{{ text }}</textarea><br>
  <button type="submit">Summarize</button>
</form>
{% if summary %}<h2>Summary</h2><p>{{ summary }}</p>{% endif %}
"""


def summarize(text: str) -> str:
    if client is None:
        # Local fallback when no Azure AI is configured
        return ".".join(text.split(".")[:2]).strip() + "."
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system",
                 "content": "Summarize the user's text in 2-3 concise sentences, "
                            "in the same language as the text."},
                {"role": "user", "content": text[:8000]},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content
    except Exception as exc:
        app.logger.error("AI call failed: %s", exc)
        return "Summary unavailable right now."


@app.route("/", methods=["GET", "POST"])
def index():
    text = summary = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        if text.strip():
            summary = summarize(text)
    return render_template_string(PAGE, text=text, summary=summary)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
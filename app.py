from flask import Flask, request, render_template_string

app = Flask(__name__)

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
    # Placeholder: replaced with an Azure AI call later
    sentences = text.split(".")
    return ".".join(sentences[:2]).strip() + "."

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
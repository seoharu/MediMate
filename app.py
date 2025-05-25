from flask import Flask, request, render_template
from gpt_summarize import gpt_simplify_and_summarize

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    raw_text = request.form.get("text")
    summary = gpt_simplify_and_summarize(raw_text)
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)

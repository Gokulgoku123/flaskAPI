from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    urls = data.get("urls", [])

    if not urls:
        return jsonify({"summary": "No URLs provided."}), 400

    combined_text = ""
    for url in urls:
        try:
            print(f"🔗 Fetching: {url}")
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join([p.get_text() for p in paragraphs])
            combined_text += text[:30000] + "\n"
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")

    if not combined_text:
        return jsonify({"summary": "No valid content found."}), 200

    print("📄 Summarizing...")
    summary = summarizer(combined_text, max_length=3000, min_length=1000, do_sample=False)[0]['summary_text']
    return jsonify({"summary": summary}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

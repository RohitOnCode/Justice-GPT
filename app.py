import dotenv
from flask import Flask, render_template, request, jsonify
from src.agents.rag_graph import rag_pipeline

dotenv.load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"answer": "Please ask a legal question."})
    result = rag_pipeline.invoke({"query": user_msg})
    answer = result.get("final", "Sorry, I couldn't generate an answer.")
    print("/n",answer)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=7070)

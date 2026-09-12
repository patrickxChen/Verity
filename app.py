"""
Verity — a search engine that makes disagreement visible.

Run with: .venv\\Scripts\\python.exe app.py
Then open: http://localhost:5001
"""

import json
import os

from flask import Flask, Response, render_template, request

from pipeline import run_verity

app = Flask(__name__, static_folder='static', static_url_path='/static')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    """Streams the run as server-sent events. EventSource can only issue GET requests, so the
    question arrives as a query param rather than a JSON body."""
    question = request.args.get("q", "")

    # "error" is reserved by EventSource for transport failures, so pipeline errors go out
    # under a distinct name the client listens for explicitly.
    event_names = {"status": "status", "result": "result", "error": "error_msg"}

    def stream():
        try:
            for kind, payload in run_verity(question):
                yield f"event: {event_names.get(kind, kind)}\ndata: {json.dumps(payload)}\n\n"
        except Exception as e:  # never leave the browser hanging on an open stream
            yield f"event: error_msg\ndata: {json.dumps(str(e))}\n\n"
        yield "event: done\ndata: {}\n\n"

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # threaded so the streaming request doesn't block the page from loading assets
    app.run(debug=False, port=5001, threaded=True)

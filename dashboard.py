"""Lightweight Flask dashboard to monitor the pipeline and approve posts before they go live."""

import json
import logging

from flask import Flask, redirect, render_template_string, request, url_for

from config import (
    SCRAPED_FILE,
    ANALYSIS_FILE,
    GENERATED_FILE,
    POSTED_LOG_FILE,
    DASHBOARD_PORT,
)

app = Flask(__name__)
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


TEMPLATE = """
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>🌱 Garten-Content Dashboard</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f4f7f2; }
    h1 { color: #2d6e3c; }
    .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .stats { display: flex; gap: 16px; flex-wrap: wrap; }
    .stat { flex: 1; min-width: 140px; text-align: center; }
    .stat .num { font-size: 28px; font-weight: bold; color: #2d6e3c; }
    .stat .label { color: #666; font-size: 13px; }
    .caption-box { white-space: pre-wrap; background: #f0f4ee; padding: 14px; border-radius: 8px; font-size: 14px; margin: 10px 0; }
    .btn { display: inline-block; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; margin-right: 8px; }
    .btn-approve { background: #2d6e3c; color: white; }
    .btn-reject { background: #c0392b; color: white; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; background: #eee; }
    .badge-pending { background: #fff3cd; color: #856404; }
    .badge-posted { background: #d4edda; color: #155724; }
  </style>
</head>
<body>
  <h1>🌱 Garten-Content Dashboard</h1>

  <div class="card stats">
    <div class="stat"><div class="num">{{ scraped_count }}</div><div class="label">Gescrapte Posts</div></div>
    <div class="stat"><div class="num">{{ qualified_count }}</div><div class="label">Viral qualifiziert</div></div>
    <div class="stat"><div class="num">{{ unposted_count }}</div><div class="label">Wartende Captions</div></div>
    <div class="stat"><div class="num">{{ posted_count }}</div><div class="label">Insgesamt gepostet</div></div>
  </div>

  {% if top_hashtags %}
  <div class="card">
    <h3>🔥 Top-Hashtags heute</h3>
    <p>{% for h in top_hashtags %}#{{ h }} {% endfor %}</p>
  </div>
  {% endif %}

  <div class="card">
    <h3>📝 Generierte Captions zur Freigabe</h3>
    {% if not pending %}
      <p>Keine Captions wartend. Führe <code>python workflow.py generate</code> aus.</p>
    {% endif %}
    {% for post in pending %}
      <div class="caption-box">{{ post.caption }}</div>
      <span class="badge badge-pending">wartet auf Freigabe</span>
      <form method="post" action="{{ url_for('approve', post_id=post.id) }}" style="display:inline">
        <button class="btn btn-approve" type="submit">✅ Posten</button>
      </form>
      <form method="post" action="{{ url_for('reject', post_id=post.id) }}" style="display:inline">
        <button class="btn btn-reject" type="submit">🗑️ Verwerfen</button>
      </form>
      <hr>
    {% endfor %}
  </div>

  <div class="card">
    <h3>✅ Zuletzt gepostet</h3>
    {% if not posted_log %}
      <p>Noch nichts gepostet.</p>
    {% endif %}
    {% for entry in posted_log[-5:] | reverse %}
      <p><span class="badge badge-posted">{{ entry.posted_at[:19] }}</span> Post-ID: {{ entry.post_id }}</p>
    {% endfor %}
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    scraped = _load(SCRAPED_FILE) or []
    analysis = _load(ANALYSIS_FILE) or {}
    generated = _load(GENERATED_FILE) or []
    posted_log = _load(POSTED_LOG_FILE) or []

    pending = [p for p in generated if not p.get("posted")]

    return render_template_string(
        TEMPLATE,
        scraped_count=len(scraped),
        qualified_count=analysis.get("qualified_posts", 0),
        unposted_count=len(pending),
        posted_count=len(posted_log),
        top_hashtags=analysis.get("top_hashtags", [])[:15],
        pending=pending,
        posted_log=posted_log,
    )


@app.route("/approve/<post_id>", methods=["POST"])
def approve(post_id):
    import poster

    generated = _load(GENERATED_FILE) or []
    # Move the approved post to the front of the queue, then post it.
    generated.sort(key=lambda p: 0 if p["id"] == post_id else 1)
    with open(GENERATED_FILE, "w", encoding="utf-8") as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)

    poster.run()
    return redirect(url_for("index"))


@app.route("/reject/<post_id>", methods=["POST"])
def reject(post_id):
    generated = _load(GENERATED_FILE) or []
    generated = [p for p in generated if p["id"] != post_id]
    with open(GENERATED_FILE, "w", encoding="utf-8") as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)
    return redirect(url_for("index"))


def run():
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)


if __name__ == "__main__":
    run()

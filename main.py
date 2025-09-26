from flask import Flask, request, render_template_string, session, redirect, url_for
import pandas as pd
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CSV Row Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .row-box { border: 1px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .nav-buttons { margin-top: 20px; }
        button { padding: 10px 20px; margin-right: 10px; }
    </style>
</head>
<body>
    <h1>Upload CSV</h1>
    {% if not session.get("file_id") %}
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv" required>
        <button type="submit">Upload</button>
    </form>
    {% else %}
        <h2>Row {{ index + 1 }} of {{ total }}</h2>
        <div class="row-box">
            {% for col, val in row.items() %}
                <p><b>{{ col }}</b>: {{ val }}</p>
            {% endfor %}
        </div>
        <div class="nav-buttons">
            {% if index > 0 %}
                <a href="{{ url_for('navigate', direction='prev') }}"><button>Previous</button></a>
            {% endif %}
            {% if index < total - 1 %}
                <a href="{{ url_for('navigate', direction='next') }}"><button>Next</button></a>
            {% endif %}
        </div>
    {% endif %}
</body>
</html>
"""

def load_dataframe():
    """Helper: load dataframe from uploaded file"""
    file_id = session.get("file_id")
    if not file_id:
        return None
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.csv")
    return pd.read_csv(file_path)

@app.route("/", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".csv"):
            # Save file with a unique ID
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.csv")
            file.save(file_path)

            # Reset session
            session["file_id"] = file_id
            session["index"] = 0
            return redirect(url_for("upload_csv"))

    if "file_id" in session:
        df = load_dataframe()
        index = session.get("index", 0)
        row = df.iloc[index].to_dict()
        return render_template_string(
            TEMPLATE,
            row=row,
            index=index,
            total=len(df),
            session=session
        )

    return render_template_string(TEMPLATE)

@app.route("/navigate/<direction>")
def navigate(direction):
    if "file_id" in session:
        df = load_dataframe()
        index = session.get("index", 0)
        if direction == "next" and index < len(df) - 1:
            session["index"] = index + 1
        elif direction == "prev" and index > 0:
            session["index"] = index - 1
    return redirect(url_for("upload_csv"))

if __name__ == "__main__":
    app.run(debug=True)

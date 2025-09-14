from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "ok"

@app.route("/api/request/<string:data>")
def requests(data):
    # Place holder for download logic

    return f"Files Downloaded: {len(os.listdir("./temp_files"))}", 200

@app.route("/api/download/<string:name>")
def download(name):
    if (not os.path.exists(os.path.join("temp_files", name))):
        return "file not found", 404
    
    return send_file(os.path.join("temp_files", name))

@app.route("/api/clean")
def clean():
    files = os.listdir("./temp_files")

    if len(files) == 0:
        return "no files to delete", 404

    for file in files:
        os.remove(os.path.join("temp_files", file))
    
    return "all_files_cleared", 200

@app.route("/api/check")
def check():
    files = os.listdir("./temp_files")

    return jsonify(files)

if __name__ == "__main__":
    os.makedirs("./temp_files", exist_ok=True)
    app.run(debug=True, port=8000)

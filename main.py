from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import subprocess, uuid, os, threading, time

app = FastAPI()

TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Serve frontend
@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()

def delete_later(path):
    time.sleep(1800)  # 30 minutes
    if os.path.exists(path):
        os.remove(path)

@app.get("/formats")
def formats(url: str):
    try:
        output = subprocess.check_output(["yt-dlp", "-F", url], stderr=subprocess.STDOUT)
        return {"formats": output.decode()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/download")
def download(url: str, vcode: str, acode: str):
    file_id = f"{uuid.uuid4()}.mp4"
    file_path = os.path.join(TEMP_DIR, file_id)

    try:
        cmd = ["yt-dlp", "-f", f"{vcode}+{acode}", "-o", file_path, url]
        subprocess.run(cmd, timeout=150)

        if not os.path.exists(file_path):
            return {"error": "Download failed."}

        threading.Thread(target=delete_later, args=(file_path,), daemon=True).start()

        return FileResponse(file_path, filename=file_id)

    except Exception as e:
        return {"error": str(e)}

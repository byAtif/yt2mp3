# main.py
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp, tempfile, os, subprocess

app = FastAPI()

def mp3_stream(video_url: str):
    # download to a temporary folder
    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            mp3_path = os.path.join(tmp, f"{info['id']}.mp3")
            if not os.path.exists(mp3_path):
                raise FileNotFoundError("MP3 was not created")
            filename = info["title"].replace('"', "") + ".mp3"
            def iterfile():
                with open(mp3_path, "rb") as f:
                    while chunk := f.read(1024 * 1024):
                        yield chunk
            headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
            return StreamingResponse(iterfile(), media_type="audio/mpeg", headers=headers)
        except Exception as e:
            raise HTTPException(500, str(e))

@app.post("/download/")
async def download(url: str = Form(...)):
    return mp3_stream(url)

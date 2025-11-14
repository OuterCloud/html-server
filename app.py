"""
pip install fastapi uvicorn python-multipart aiofiles
"""

import os
import socket

import aiofiles
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/html", StaticFiles(directory="html_files", html=True), name="html")
os.makedirs("can_be_downloaded", exist_ok=True)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


@app.get("/")
async def index():
    return HTMLResponse(content=open("html_files/index.html").read())


@app.get("/download")
async def download_page():
    files = os.listdir("can_be_downloaded")
    html = "<html><head><title>Download Files</title></head><body><h1>Download Files</h1><ul>"
    for file in files:
        html += f'<li><a href="/download/file/{file}">{file}</a></li>'
    html += "</ul></body></html>"
    return HTMLResponse(content=html)


@app.get("/download/file/{filename}")
async def download_file(filename: str):
    file_path = f"can_be_downloaded/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            file_path, media_type="application/octet-stream", filename=filename
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        async with aiofiles.open(file.filename, "wb") as f:
            await f.write(contents)
    except Exception as e:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        await file.close()
    return {"message": f"Successfully uploaded {file.filename}"}


if __name__ == "__main__":
    local_ip = get_local_ip()
    print("Starting server at http://{}:8000".format(local_ip))
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

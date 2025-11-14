"""
pip install fastapi uvicorn python-multipart aiofiles
"""

import socket
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
import uvicorn

app = FastAPI()
app.mount("/html", StaticFiles(directory="html_files", html=True), name="html")


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

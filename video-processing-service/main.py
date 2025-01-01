import uvicorn
from multiprocessing import Process
from app.worker import process_videos

def start_worker():
    process_videos()

if __name__ == "__main__":
    worker_process = Process(target=start_worker)
    worker_process.start()

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    worker_process.join()

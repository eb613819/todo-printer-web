import json
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DATA_FILE = Path(os.environ.get("TASKS_FILE", "tasks.json"))
PRINTER_IP = os.environ.get("PRINTER_IP", "192.168.1.87")
PRINTER_PORT = int(os.environ.get("PRINTER_PORT", "9100"))
STATIC_DIR = Path(__file__).parent / "ui" / "dist" / "ui" / "browser"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WIDE = 24
BORDER = "*" * WIDE
THIN = "-" * WIDE
THICK = "=" * WIDE

def load_tasks() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_tasks(tasks: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

class NewGroup(BaseModel):
    name: str
    tasks: list[str] = []

class AddTasks(BaseModel):
    tasks: list[str]

class PrintRequest(BaseModel):
    groups: list[str]

@app.get("/api/tasks")
def get_tasks():
    return load_tasks()

@app.post("/api/groups")
def create_group(body: NewGroup):
    tasks = load_tasks()
    name = body.name.strip().lower()
    if name in tasks:
        raise HTTPException(status_code=400, detail="Group already exists")
    tasks[name] = body.tasks
    save_tasks(tasks)
    return tasks

@app.post("/api/groups/{group}/tasks")
def add_tasks(group: str, body: AddTasks):
    tasks = load_tasks()
    name = group.strip().lower()
    if name not in tasks:
        raise HTTPException(status_code=404, detail="Group not found")
    tasks[name].extend(body.tasks)
    save_tasks(tasks)
    return tasks

@app.delete("/api/groups/{group}/tasks/{index}")
def remove_task(group: str, index: int):
    tasks = load_tasks()
    name = group.strip().lower()
    if name not in tasks:
        raise HTTPException(status_code=404, detail="Group not found")
    if index < 0 or index >= len(tasks[name]):
        raise HTTPException(status_code=400, detail="Task index out of range")
    tasks[name].pop(index)
    if not tasks[name]:
        del tasks[name]
    save_tasks(tasks)
    return tasks

@app.delete("/api/groups/{group}")
def remove_group(group: str):
    tasks = load_tasks()
    name = group.strip().lower()
    if name not in tasks:
        raise HTTPException(status_code=404, detail="Group not found")
    del tasks[name]
    save_tasks(tasks)
    return tasks

@app.post("/api/print")
def print_groups(body: PrintRequest):
    tasks = load_tasks()
    try:
        from escpos.printer import Network
        p = Network(PRINTER_IP, PRINTER_PORT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Printer connection failed: {e}")

    now = datetime.now().strftime("%b %d, %Y  %I:%M %p")
    valid_groups = [g.strip().lower() for g in body.groups if g.strip().lower() in tasks]

    if not valid_groups:
        raise HTTPException(status_code=400, detail="No valid groups to print")

    if len(valid_groups) == 1:
        group = valid_groups[0]
        p.set(align="center", bold=True)
        p.text(BORDER + "\n")
        p.text("*" + " " * (WIDE - 2) + "*\n")
        p.set(align="center", bold=True, double_height=True, double_width=True)
        p.text(f" {group.upper()} \n")
        p.set(align="center", bold=False, double_height=False, double_width=False)
        p.text("*" + " " * (WIDE - 2) + "*\n")
        p.text(BORDER + "\n")
        p.set(align="center", bold=False)
        p.text(f"{now}\n")
        p.text(THICK + "\n")
        p.set(align="left", bold=False, double_height=False, double_width=False, font='b')
        p.text(THIN + "\n")
        for idx, task in enumerate(tasks[group], 1):
            p.text(f"[ ] {idx}. {task}\n\n")
    else:
        p.set(align="center", bold=False)
        p.text(BORDER + "\n")
        p.text(f"{now}\n")
        p.text(THICK + "\n")
        for i, group in enumerate(valid_groups):
            if i > 0:
                p.text(THICK + "\n")
            p.set(align="center", bold=True)
            p.text(f"{group.upper()}\n")
            p.set(align="left", bold=False, double_height=False, double_width=False, font='b')
            p.text(THIN + "\n")
            for idx, task in enumerate(tasks[group], 1):
                p.text(f"[ ] {idx}. {task}\n\n")

    p.set(align="center", bold=True, double_height=True, double_width=True)
    p.text(THICK + "\n")
    p.text("\n\n")
    p.cut()

    return {"ok": True}

if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

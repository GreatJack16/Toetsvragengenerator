from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_file(file):
    if not file or file.filename == "":
        return None

    path = UPLOAD_DIR / file.filename
    file.save(path)
    return str(path)
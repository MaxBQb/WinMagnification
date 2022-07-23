import os.path
import shutil


for path in [
    r'.\source\generated',
    r'.\build',
]:
    try:
        path = os.path.abspath(path)
        shutil.rmtree(path)
        print("Removed", path)
    except FileNotFoundError:
        print("Skipped", path)
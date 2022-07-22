import shutil

try:
    shutil.rmtree(r'.\source\_autosummary')
    shutil.rmtree(r'.\build')
except FileNotFoundError:
    pass

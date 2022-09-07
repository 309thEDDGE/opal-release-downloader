from pathlib import Path
import subprocess

def validate():
    fp = Path(__file__)
    print(f"fp = {str(fp)}")
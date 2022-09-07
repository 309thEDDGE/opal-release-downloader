import sys
from pathlib import Path
import subprocess

def run_subproc_in_current_shell(command: list) -> int:

    print(f"\n===> Executing subprocess: \"{' '.join(command)}\"")
    proc = subprocess.run(command, 
        stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    print(f"\n===> End subprocess output")
    return proc.returncode


def validate():
    script_path = Path(__file__).parent / 'bin' / 'validate_opal_artifacts.sh'
    command = ['bash', str(script_path)]
    retcode = run_subproc_in_current_shell(command)

    if retcode != 0:
        print(f"Error in previous process: return code is {retcode}.")
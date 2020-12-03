import os
import subprocess
import tempfile
import venv
from pathlib import Path


repo_dir = Path(__file__).parent.parent
os.chdir(repo_dir)

with tempfile.TemporaryDirectory() as tmp:
    work_dir = Path(tmp)
    env_dir = work_dir / 'env'
    env = venv.EnvBuilder(with_pip=True)
    # EnvBuilder.create() doesn't return context
    ctx = env.ensure_directories(env_dir)
    env.create(env_dir)
    pyexe = ctx.env_exe
    subprocess.check_call([
        pyexe, '-m', 'pip', 'install', 'pyinstaller', 'stdlib-list'])
    subprocess.check_call([
        pyexe, '-m', 'PyInstaller',
        '--clean',
        '--distpath', 'dist',
        '--workpath', str(work_dir),
        'dl-plus.spec',
    ])

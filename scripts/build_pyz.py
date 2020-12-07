import os
import zipapp
from pathlib import Path


repo_dir = Path(__file__).parent.parent
os.chdir(repo_dir)

dest_dir = Path('dist')
os.makedirs(dest_dir, exist_ok=True)
zipapp.create_archive(
    source='src',
    target=dest_dir / 'dl-plus',
    interpreter='/usr/bin/env python3',
    main='dl_plus.cli:main',
    compressed=True,
)

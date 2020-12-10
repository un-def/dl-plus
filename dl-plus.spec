from stdlib_list import stdlib_list


hiddenimports = [
    m for m in stdlib_list()
    if not m.startswith('ensurepip')
    and not m.startswith('idlelib')
    and not m.startswith('lib2to3')
    and not m.startswith('test')
    and not m.startswith('tkinter')
    and not m.startswith('turtle')
    and not m.startswith('venv')
]


a = Analysis(   # noqa: F821
    ['src\\dl_plus\\__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(   # noqa: F821
    a.pure,
    a.zipped_data,
    cipher=None,
)
exe = EXE(   # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dl-plus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

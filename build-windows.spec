# -*- mode: python -*-

block_cipher = None

added_files = [
    ('.\\ain\\assets', 'assets'),
    ('.\\ain\\frontend\\dist', 'frontend/dist')
]

a = Analysis(['.\\ain\\main.py'],
             pathex=['.\\dist'],
             binaries=None,
             datas=added_files,
             hiddenimports=['clr'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=False,
          name='ain',
          debug=False,
          strip=True,
          icon='.\\ain\\assets\\favicon.ico',
          upx=True,
          console=False ) # set this to see error output of the executable
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='ain')
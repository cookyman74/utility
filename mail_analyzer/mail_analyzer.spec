# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['mail_analyzer.py'],
             pathex=['C:\\Users\\cooky\\PycharmProjects\\develop\\utility\\mail_analyzer'],
             binaries=[],
             datas=[('src/stopwords','wordcloud'),('C:/Users/cooky/Documents/PythonVirtualenv/mailanalyzer37/Lib/site-packages/konlpy','konlpy')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='mail_analyzer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

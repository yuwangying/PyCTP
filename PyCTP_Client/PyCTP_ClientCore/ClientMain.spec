# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path

added_files = [('D:\\Python34\\DLLs\\python3.dll', '.'),('*.dll', '.'),('img', 'img'),('image', 'image'),('config', 'config'),('log', 'log')]

a = Analysis(['ClientMain.py'],
             pathex=['.', 'D:\\CTP\\PyCTP\\PyCTP_Client\\PyCTP_ClientCore'],
             binaries=[('PyCTP.pyd',''),
             ('thostmduserapi.dll',''),
             ('thosttraderapi.dll','')],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ClientMain',
          debug=False,
          strip=False,
          upx=False,
          console=True , icon='img\\rocket.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='bee')

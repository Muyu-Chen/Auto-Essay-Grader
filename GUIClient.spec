# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['GUIClient.py'],
    pathex=[],
     binaries=[
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\libtkdnd2.9.4.dll', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\pkgIndex.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd2.9.3.lib', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd2.9.4.lib', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_compat.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_generic.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_macosx.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_unix.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_utils.tcl', '.'),
        ('c:\\program files (x86)\\microsoft visual studio\\shared\\python39_64\\lib\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\tkdnd_windows.tcl', '.'),
        
        ],
    datas=[],
    hiddenimports=['tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GUIClient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)

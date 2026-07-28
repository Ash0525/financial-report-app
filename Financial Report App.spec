# -*- mode: python ; coding: utf-8 -*-
from backend.version import APP_VERSION

a = Analysis(
    ['backend/desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('frontend', 'frontend')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Financial Report App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Financial Report App',
)
app = BUNDLE(
    coll,
    name="Financial Report App.app",
    icon="assets/app-icon.icns",
    bundle_identifier="com.alexash.financialreportapp",
    info_plist={
        "CFBundleDisplayName": "Financial Report App",
        "CFBundleName": "Financial Report App",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_VERSION,
        "NSHighResolutionCapable": True,
    },
)

# Usage / 使い方

## 必要な環境

- Geo3D開発者 Alex Moncks氏の [openMSX fork](https://github.com/alexmoncks/openMSX)。検証コミットは `de29fb854885a38251c03e24596ad4ff95770ef2` です。一般配布版openMSXやV9968対応だけのビルドではなく、**Geo3D拡張を含むビルド**が必要です。
- 同じ版に含まれる `Panasonic_FS-A1ST_V9968` machine と `geo3d` extension。
- FS-A1STの起動に必要なシステムROMは各自で適法に用意してください。本リポジトリはBIOSを含みません。
- 今回は内蔵VDP側98h–9Ch、Geo3D 9Dh/9Fhの構成です。外付け88h側への自動対応はありません。

Use the Geo3D developer's openMSX build, including its machine and extension definitions from the same revision. Standard openMSX or a V9968-only build is insufficient. Supply your own legally obtained FS-A1ST system ROMs. We do not redistribute the emulator or firmware.

## ROMを起動する / Run a ROM

[Release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.1.1) から `V9968_Geo3D_SampleDemo-v0.1.1-ROMs.zip` をダウンロードし展開します。PowerShell例:

```powershell
& 'C:\path\to\geo3d-openmsx\openmsx.exe' `
  -machine Panasonic_FS-A1ST_V9968 -ext geo3d `
  -cart '.\roms\VECTOR_RUSH.ROM' -romtype ASCII16
```

フライトは `SKYBOUND.ROM`、地球・月は `ORBITAL.ROM` に差し替えます。起動後は自動でループ再生します。ゲーム操作・音楽はありません。終了はエミュレータの通常の終了操作で行います。

The demos start and loop automatically. There are no gameplay controls or music. Replace the filename to select another demo; exit through the emulator UI.

## ソースからビルド / Build

検証ホストはWindows、Python 3.13、NumPy 2.4.6、Pillow 12.2.0。SDCC付属の `sdasz80.exe` と `sdldz80.exe` が必要です。使用したassemblerの表示は `V05.50.4+NoICE+SDCCmods-WIP-R14`。ツール自体は同梱していません。

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN = 'C:\path\to\sdcc\bin'
python demos/vector-rush/build.py
python demos/skybound/build.py
python demos/orbital/build.py
python tools/verify.py
```

生成先は各 `demos/<name>/out/`。公開版ROMと同一ハッシュになることを検査します。依存バージョンが異なる場合、画像変換の差により一致しない可能性があります。その場合は原因を確認し、検証記録を上書きして合格扱いにしないでください。

Build outputs are under each demo's `out/`. Verification compares them with the release hashes. Dependency differences may affect image conversion; do not silently replace the reference hashes.

## 任意: キャプチャ・動画生成 / Optional media reproduction

```powershell
$env:GEO3D_RUNTIME = 'C:\path\to\geo3d-openmsx'
# A directory containing openmsx.exe and its matching share/ directory.
# Configure BIOS paths normally, or set your own OPENMSX_USER_DATA / OPENMSX_HOME.
python demos/orbital/capture.py
python -m pip install -r requirements-media.txt
$env:FFMPEG = 'C:\path\to\ffmpeg.exe'
$env:CAPTION_FONT = 'C:\Windows\Fonts\bahnschrift.ttf'
python demos/orbital/encode.py
```

`vector-rush` / `skybound` も同様です。キャプチャは独立したエミュレータプロセスを起動し、設定の自動保存を無効にします。`throttle off` は収録の実時間を短縮するためで、映像のタイムスタンプはエミュレート時間を使います。エンコード時の速度変更はありません。キャプチャは起動と終了のタイムアウトを持ちます。

Media generation also needs OpenCV (tested 5.0.0) and ffmpeg (tested 7.1). The caption font is rendered into the video, not bundled. Set `CAPTION_FONT` to another locally available licensed font if necessary. MP4 is silent; GIF export checks the 15,000,000-byte limit.


## NIGHT RAVEN (v0.2.0)

See [NIGHT RAVEN usage, technical details, validation and license review](NIGHT_RAVEN.md). The existing three demos and v0.1.0 assets are unchanged.

## OBSIDIAN / TITAN PASS (v0.2.0)

[起動・ビルド・技術・検証・素材の来歴](OBSIDIAN.md)。256KiB / ASCII16、無音の自動再生デモです。

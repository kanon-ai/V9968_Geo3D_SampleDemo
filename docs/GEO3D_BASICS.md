# Geo3D BASIC FUNCTIONS

## English

A small automatic, silent parameter demo. No story or scenic assets are required to see the changes.

| Scene | Changes | Remains fixed |
|---|---|---|
| FOCAL | Focal length F, 115–225 | Cube pose, center, texture origin |
| CENTER | Projection center X/Y | Cube pose, F=170, texture origin |
| TEX ORIGIN | TEXY, 768–799 | Plane geometry, UVs and camera |
| COMBINED | All three parameters | Plane geometry and UVs |

The upper line shows the actual F/X/Y/T values written to Geo3D; T is the absolute texture Y origin in VRAM. The cross and frame are fixed screen references, not wireframe rendering. Each scene uses 32 parameter steps, each held for three display updates. With a fixed viewpoint, varying focal length appears as scaling; it is not a camera dolly experiment.

### Run

Download GEO3D-BASICS.ROM from the [release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-basics-v0.1.0). ROM size is **1 MiB; explicitly select ASCII16**. A compatible V9968 + Geo3D emulator configuration is required. Verified configuration: developer Geo3D openMSX, Panasonic_FS-A1ST_V9968 machine, geo3d extension:

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart GEO3D-BASICS.ROM -romtype ASCII16
```

No input is needed. Video and GIF are silent, about 12.8 seconds, with no playback acceleration or motion interpolation.

### Build

Install Python, NumPy, Pillow and SDCC (sdasz80/sdldz80). Add SDCC bin to PATH or set SDCC_BIN. Set ROM_FONT to a locally licensed TrueType monospace font; the verified Windows build used Consolas. Font files are not included.

```text
python demos/geo3d-basics/build.py
```

The output is demos/geo3d-basics/out/GEO3D-BASICS.ROM. Using a different font changes the label bitmap and ROM hash.

### Implementation and validation

Geo3D performs the runtime transformation, projection and textured rasterization. The CPU sends fixed geometry/matrices and parameter tables. F/CX/CY and TEXY registers change directly; texture movement is not simulated by changing plane vertices or UVs. V9968 is configured in a 256-entry EPAL display mode, although the test pattern uses only a few colors.

The dedicated Geo3D openMSX build based on de29fb854885a38251c03e24596ad4ff95770ef2 was used. All 1,536 parameter records were checked to keep unrelated parameters fixed in isolated scenes. Representative screenshots from every scene were inspected, and the complete GIF/MP4 decoded successfully. Palette revision changed 19 bytes only; geometry, animation, labels and texture indices were identical. The packaged source was rebuilt and compared against the tested ROM.

**BlueMSX Plus and physical FPGA/cartridge operation are unverified for this demo. Emulator timing is not a physical hardware performance claim.**

### License and disclaimer

MIT, with the repository LICENSE and retained Geo3D/V9968 notices in THIRD_PARTY_NOTICES.md and LICENSES. No BIOS, emulator, tool executable, font file or music is bundled. Supplied as an experimental sample, without warranty; compatibility with future experimental hardware/emulator versions is not guaranteed. Hardware and author names identify dependencies and do not imply endorsement.

## 日本語

黒背景で焦点距離・投影中心・テクスチャ原点を順に動かし、最後に組み合わせます。画面上端のF/X/Y/Tは実際の設定値です。立方体・平面の姿勢は固定しています。

ROMは1 MiB、マッパーはASCII16を明示してください。上記の専用Geo3D openMSX構成で自動再生します。通常のMSX用エミュレータだけでは動作しません。無音・約12.8秒、動画の早回しや補間はありません。

公開ソースからの再ビルド一致、各機能の単独変更、全シーンの画像、GIF/MP4のデコードを確認しました。実機・BlueMSX Plusは本デモ未検証です。エミュレータでの動作は実機性能の保証ではありません。

MITライセンスおよび既存のGeo3D/V9968の権利表示を継承します。実験用サンプルとして無保証で提供し、将来の仕様との互換性は保証しません。詳細は上記英語説明およびリポジトリのライセンス文書を参照してください。

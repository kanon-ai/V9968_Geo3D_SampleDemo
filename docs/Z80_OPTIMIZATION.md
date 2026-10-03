# Z80 optimization update / Z80最適化更新 — 2026-10-03

[Download ROMs and source / ROM・ソース](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0)

## English

Nine existing demos receive a measured Z80 optimization. Geometry, textures, animation records and object counts are unchanged. The bulk Geo3D data-port loop uses groups of 16 OUTI instructions on Z80, removing repeated-loop overhead. R800 selects the original bulk loop at startup; VDP transfers and short Geo3D tails retain their existing code. SKYBOUND additionally reuses byte-identical face/UV buffers across terrain meshes, with cache IDs generated from the full face and UV data.

These are **developer-openMSX measurements, not physical-hardware results**. Z80 uses an isolated C-BIOS MSX2+ profile; R800 uses the V9968 TurboR profile. Emulator source: `de29fb854885a38251c03e24596ad4ff95770ef2`. The external-cartridge bus timing and physical performance are not established by these results. **This update is not yet verified on physical hardware or BlueMSX+.** Older BlueMSX+ checks in individual guides refer to earlier ROMs.

| Demo | Before / 旧版 | After / 最適化版 | Gain / 改善 |
|---|---:|---:|---:|
| BULLRUSH | 5.54 fps | 6.25 fps | +12.9% |
| BULLRUSH CROWD (5 robots) | 4.70 fps | 5.20 fps | +10.7% |
| NIGHT RAVEN | 9.95 fps | 10.75 fps | +8.0% |
| NIGHT RAVEN FLIGHT | 9.64 fps | 10.45 fps | +8.4% |
| OBSIDIAN | 5.13 fps | 5.99 fps | +16.8% |
| ORBITAL | 9.73 fps | 11.27 fps | +15.8% |
| ORBITAL TYPE REAL | 9.73 fps | 11.27 fps | +15.8% |
| SKYBOUND | 9.69 fps | 12.91 fps | +33.3% |
| VECTOR RUSH | 8.99 fps | 10.34 fps | +15.1% |

Rates use 511 intervals between 512 completed display pages in emulated time. NIGHT RAVEN FLIGHT uses a scripted start/movement/fire/missile input sequence; the other table rows use automatic playback with no input. The JSON also includes the flight edition's no-input result and BULLRUSH texture-toggle checks.

All nine updated demos matched 512 old/new display pages on both CPUs. Additional 512-page comparisons exercise texture toggling in both BULLRUSH editions and keyboard input in NIGHT RAVEN FLIGHT, on both CPUs. Published-source rebuilds match the tested ROMs. All asset/animation banks after bank 0 are unchanged. R800 rates remain approximately at previous levels (small display-frame quantization differences remain).

**Unchanged:** Geo3D BASIC FUNCTIONS remains approximately 29.96 fps, so its optimization experiment is not published. FOUR SEASONS was already optimized in v0.2.0 and is not modified again. Existing GIF/MP4 previews remain earlier-version recordings; this release contains ROM/source updates, not new or accelerated videos. Old releases remain available.

## 日本語

Z80で実測効果のあった9本のみ更新しました。Geo3Dへの大量転送を16個のOUTI単位に展開し、繰り返し処理の負担を削減しています。R800では起動時に従来の転送ループを選択します。VDP転送は変更していません。SKYBOUNDは地形間で完全一致する面・UV情報の再転送も省きます。機体・地形・惑星の数、形状、テクスチャ、アニメーション記録は変更していません。

表は専用openMSXのエミュレーション時間による更新頻度です。NIGHT RAVEN FLIGHTのみ操作付き比較、他は入力なしの自動再生です。各9本×両CPU×512画面に加え、BULLRUSH 2版のTキー切替とNIGHT RAVEN FLIGHTの操作付き比較も各CPUで512画面ずつ実施し、表示ページのバイト単位の一致を確認しました。実機・BlueMSX+は本更新について未検証であり、表は実機性能の保証ではありません。

基本機能デモは約29.96 fpsのままで効果がないため更新しません。花びら FOUR SEASONS は更新済みv0.2.0を維持します。既存GIF・MP4は旧版の記録として残します。旧リリースも保存します。

## Run / 実行

All ROMs use **ASCII16**. OBSIDIAN is **256 KiB**; the other eight ROMs are **1 MiB**. Use a V9968 + Geo3D-capable configuration. Plain MSX2+ without these extensions cannot run these demos. The Z80 optimization does not remove the hardware requirements.

全ROMともASCII16です。OBSIDIANは256 KiB、ほか8本は1 MiB。V9968 + Geo3D対応環境が必要です。通常のMSX2+本体だけでは動作しません。R800自動選択は維持しています。各デモ固有の操作・音声仕様は従来どおりです。

Example (dedicated emulator / 専用エミュレータ):

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart SKYBOUND.ROM -romtype ASCII16
```

For MSX2+, select your correctly configured Z80 machine profile with V9968 and Geo3D; the TurboR command above is not a Z80 benchmark configuration. Supply legally obtained BIOS files yourself.

## Build / ビルド

Use the existing Python / NumPy / Pillow / SDCC setup and each demo's `build.py`. SKYBOUND generates `src/topology.inc` during its build. OBSIDIAN also requires `ROM_FONT`; the verified build used the locally installed `C:/Windows/Fonts/consola.ttf`, not bundled here.

The published five-robot CROWD edition requires `python demos/bullrush-crowd/variants.py` after `build.py`, with `CROWD_EXTRAS` unset. Distribute `out/BULLRUSH-5robots.ROM` as `BULLRUSH-CROWD.ROM`. The default builder's intermediate `BULLRUSH.ROM` is not the five-robot release asset.

公開CROWDは5機版です。既定のビルド後に `variants.py` を実行し、`BULLRUSH-5robots.ROM` を配布名 `BULLRUSH-CROWD.ROM` として使用してください。

## Evidence, license and disclaimer / 検証・ライセンス・免責

[Detailed measurements and hashes / 測定・ハッシュ](validation/z80-optimization.json)

MIT license and existing upstream notices are retained; see [LICENSE](../LICENSE) and [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md). No BIOS, emulator, FPGA bitstream, tool executable or font file is distributed. This experimental software is supplied as-is, without warranty, hardware certification, or a promise of performance/compatibility. Each demo's existing license and disclaimer continue to apply.

MITライセンスと既存の第三者表記を維持しています。BIOS・エミュレータ・FPGAビットストリーム・ツール本体・フォントファイルは同梱しません。技術実験用の現状有姿・無保証の配布であり、実機動作や性能・互換性の保証、公式認証を意味しません。各デモの既存免責事項も引き続き適用します。

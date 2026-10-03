# NIGHT RAVEN — silent sample / 無音サンプル

**2026-10-03 Z80 update / Z80最適化版:** [ROM](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) · [測定・検証範囲 / Measurements and verification scope](Z80_OPTIMIZATION.md). Existing previews and earlier validation below describe previous releases. 以下の既存映像・過去検証は旧版の記録です。

## v0.3.2 — NIGHT RAVEN 高速版

画面外へ完全に出た壁区画のモデル転送とGeo3D RUNを省略しました。画面・敵・弾・演出は保持し、無音仕様も継続します。ROMは1MiB / ASCII16です。

開発者版openMSX (de29fb854885a38251c03e24596ad4ff95770ef2) で、元版と一周512画面の表示VRAMが完全一致、237イベントも不変でした。最初と最後の表示完了間の時間は25.800335秒から24.749319秒へ約4.07%短縮。1,536進行レコードの壁RUN候補7,680回中843回を省略します（描画は3レコード刻み）。実機性能を示す値ではありません。

[検証記録](validation/night-raven-optimization-v0.3.2.json)。blueMSXのローカル検証パッチは含みません。blueMSXでの同条件の最適化前後比較・実機検証は未実施です。従来の使用方法、ライセンス、無保証の条件を引き継ぎます。

Download: [v0.3.2](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.2)

Software-only off-screen hull culling. Identical display VRAM across all 512 rendered frames; unchanged events. About 4.07% less elapsed emulated time in the stated openMSX comparison. No emulator patches included; physical hardware unverified.

## v0.2.0 documentation / 旧版の記録


TurboR + V9968 + Geo3Dで、巨大艦の壁沿いを黒烏が突破する非操作型の宇宙戦デモです。墨黒の機体、橙色の誘導ミサイル、5種類の船体区画、雲のない惑星を組み合わせています。ゲーム操作はできません。

**今回は効果音・BGMともにありません。カッコいいBGMを付けたいのですが、まだ決まらず悩み中です。今後BGMを追加する予定です。それまでは、それぞれの「心のBGM」を重ねてお楽しみください。** 追加時期は未定です。

A non-interactive space-combat demo: the black Raven breaks through an interception line beside a massive ship. **This edition has no sound effects or BGM. We would love a great soundtrack, but have not settled on one yet; BGM is planned for a future update. Until then, enjoy it with the soundtrack in your imagination!** No delivery date is promised.

![NIGHT RAVEN](media/night-raven.gif)

## Download / ダウンロード

[v0.2.0 — NIGHT RAVEN ROM and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.2.0)

The release adds NIGHT RAVEN; the three previous demos remain available in [v0.1.0](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.1.0).

## Run / 起動

**まずGeo3D開発者 Alex Moncks氏のopenMSXで確認しています。**
検証版: [alexmoncks/openMSX](https://github.com/alexmoncks/openMSX), commit `de29fb854885a38251c03e24596ad4ff95770ef2`.
通常のopenMSXやV9968のみ対応するビルドではなく、Geo3D拡張を含む版が必要です。

```powershell
& 'C:\path\to\geo3d-openmsx\openmsx.exe' `
  -machine Panasonic_FS-A1ST_V9968 -ext geo3d `
  -cart '.\NIGHT_RAVEN_GEO3D.ROM' -romtype ASCII16
```

- ROM: **1 MiB / ASCII16**. Auto-start, automatic looping; no gameplay controls.
- Internal VDP ports 98h–9Ch and Geo3D ports 9Dh/9Fh. External 88h configuration is not tested or automatically selected.
- Use the matching machine/extension definitions supplied by the developer's emulator and legally obtained system ROMs. Emulator, BIOS and FPGA bitstreams are **not included**.
- Exit using the emulator's normal controls. A reset restarts the demo.

## Build / ビルド

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN = 'C:\path\to\sdcc\bin'
python demos/night-raven/build.py
python demos/night-raven/verify_combat.py
python demos/night-raven/verify_hull.py
```

Output: `demos/night-raven/out/NIGHT_RAVEN_GEO3D.ROM`.
Uses Python, NumPy, Pillow and SDCC's `sdasz80.exe` / `sdldz80.exe`; no external game artwork or font file is needed for the ROM. The 5×7 HUD font is defined in source.

For capture, follow the environment setup in [USAGE.md](USAGE.md), then use `demos/night-raven/capture.py` and `encode.py`. The latter uses `FFMPEG` and `CAPTION_FONT` and checks GIF size against 15,000,000 bytes. Source AVI is temporary and excluded from Git.

## How it works / 技術説明

- **Geo3D:** model vertices and faces are transformed/projected/shaded at runtime. Solid faces are decomposed into horizontal LINE commands for the V9968. Each RUN accepts up to 255 vertices/faces; the scene uses multiple RUNs. The five hull districts are streamed separately, then the aircraft vertex pool is restored.
- **V9968:** VRAM and actual pixel drawing; LRMM rotates/scales the starfield/planet atlas, LINE draws weapons/shields, HMMM copies the HUD, and display pages alternate. Hull/aircraft detail uses polygons, not mapped textures; this sample does not exercise Geo3D's texture mode.
- **TurboR R800:** configures hardware, streams model/pose data, schedules drawing and page flips. **Movement, combat events and camera records are precomputed at build time.** This is real-time polygon rendering, not a prerecorded raster movie, but it is also not a runtime AI/gameplay benchmark.
- No separate Geo3D framebuffer is used; final pixels live in V9968 VRAM. Painter ordering has limitations, with no Z-buffer or complete near-plane polygon clipping.
- Three simulation ticks advance per rendered frame. Media uses emulator timestamps; no playback acceleration is applied.

投入面数は1フレーム419～531面、平均約493面（画面外・裏面を含む）。全てが実際に塗りつぶされる面ではありません。再生映像のfpsと実際の描画更新回数も区別してください。

## Validation / 検証範囲

Silent release tested on 2026-09-29 with the above developer emulator:

- ROM build and model/index/camera-record checks; deterministic battle events remain unchanged.
- One complete approximately 25.83-second loop captured, including scene wrap.
- About **19.81 rendered updates/s** in this evaluation; the video container is about 59.92 fps and contains repeated frames.
- Recorded emulator PCM has zero peak amplitude; published MP4 has no audio stream. GIF is 14,035,096 bytes, 432×351, about 25.85 seconds.
- Validation manifests and logs: [validation/](validation/), files prefixed `night-raven-`.

**実機・FPGAでの動作や速度は未検証です。** このエミュレータではGeo3D計算の時間再現に限界があり、上記は実機性能・最大ポリゴン性能を示しません。本家V9968の全仕様との互換性、他のエミュレータ、異なるGeo3D版も保証しません。

Physical hardware, other emulators and other revisions are unverified. Emulator geometry-computation timing is not a hardware performance measurement. This sample is not an official endorsement or certification from either hardware author.

## License, credits and disclaimer

Original source and procedural geometry/background assets are supplied under this repository's [MIT License](../LICENSE), to the extent the contributors hold rights. No commercial game images, models, music or logos are included. Inspiration references do not imply affiliation.

Geo3D protocol/reference material: **Alex Moncks** (MIT). V9968: **HRA!**. The existing upstream MIT notices are retained in [LICENSES](../LICENSES); see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). No emulator, FPGA source/bitstream, BIOS, tool executable or font file is redistributed. Video captions use a locally licensed font, rendered into the video.

**試作中・無保証・現状有姿です。** 動作、速度、機器への適合、保守やバグ修正を保証しません。利用は各自の判断と責任で行ってください。責任制限は適用法で許される範囲に限ります。商用ゲームやハードウェアメーカーの公式作品ではありません。

Experimental software, provided **AS IS, without warranty**, including no guarantee of compatibility, performance, maintenance or fixes. Liability limitations apply only to the extent permitted by applicable law. See the MIT License for the complete terms.

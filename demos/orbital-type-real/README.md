# ORBITAL — TYPE REAL

猛烈に回る地球を楽しむ、ORBITALの別バージョンです。従来版はそのまま残しています。
地球は月の1公転につき約27.3回、月と同方向に自転します。月は常に同じ面を地球に向けます。
専用Geo3D openMSXで月の1周は約18.42秒、地球の1回転は約0.67秒です。
TYPE REALは自転方向と周期比を意識した名称で、実時間・実寸の天文シミュレーションではありません。軌道・距離・大きさ・傾きは演出用です。

A separate fast-spinning edition of ORBITAL. Earth turns approximately 27.3 times per lunar orbit, in the same rotational sense as the Moon. The Moon remains tidally locked. Timing, scale and orbit are deliberately illustrative, not a scientific simulation.

## Download and run

[TYPE REAL v0.3.1 release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.1): 1 MiB ASCII16 ROM, silent MP4 and GIF. Automatic playback; no controls. Existing ORBITAL remains available unchanged.

Use the Geo3D developer's openMSX with `Panasonic_FS-A1ST_V9968` and `-ext geo3d`. Build with the same dependencies as [Usage](../../docs/USAGE.md), setting `SDCC_BIN`, then run `python demos/orbital-type-real/build.py`. Output: `out/ORBITAL-TYPE-REAL.ROM`. Capture uses `GEO3D_RUNTIME`; encoding uses `FFMPEG`.

## Implementation and validation

Geo3D transforms/projects textured sphere polygons; V9968 draws the texture spans via LRMM. Movement matrices are precomputed; ROM contains no prerecorded raster movie. Earth: 222 vertices / 240 faces; Moon: 146 / 160; occasional distant UFO: 96 / 78. Faster rotation does not increase polygon count and is not a hardware throughput benchmark.

Validated using Geo3D openMSX commit `de29fb854885a38251c03e24596ad4ff95770ef2`. Physical hardware and other emulators remain unverified. Rendering/capture runs at original emulated speed without video acceleration. Quantized Moon-facing error stays below 0.16 degrees. At the end of each lunar cycle the scripted scene restarts; 27.3 Earth turns do not form a seamless Earth-texture loop.

MIT license and existing AI-generated texture provenance apply; see [license review](../../docs/LICENSE_REVIEW.md) and [validation limits](../../docs/VALIDATION.md). Supplied AS IS, without warranty.

## v0.3.1 — Earth texture orientation fix

地球のテクスチャが左右反転していた問題を修正しました。両版の自転速度・月の動きは維持しています。
Corrected mirrored Earth UV mapping. Rotation speeds and lunar motion are unchanged.

[Updated ROM, GIF and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.1)

## v0.3.4 — Moon rabbit / 月の餅つきウサギ

月の上に小さなウサギ・杵・臼を追加。16姿勢のポリゴンモデルで餅つきします。ROMは1 MiBのままです。地球と月の運動データは維持していますが、描画負荷が増え、専用openMSXでの1周は約25.63秒になりました。TYPE REALの自転周期比27.3は維持しています。従来の18.42秒という計測値はウサギ追加前の値です。

Added a small polygon rabbit pounding mochi on the Moon. Sixteen animation poses reuse free ROM banks. One extra Geo3D object raises rendering load: a cycle now takes about 25.63 seconds in the evaluated emulator, not the earlier 18.42 seconds. This is not a physical hardware speed measurement.

[Updated ROM, GIF and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.5)

### v0.3.5

ウサギと餅つき道具を月の姿勢に連動させ、常に地球側を向くよう調整しました。サイズ・餅つき動作・天体の動きは維持しています。
Rabbit and mochi tools now follow the lunar orientation, facing Earth. Size, animation and planetary motion are unchanged.

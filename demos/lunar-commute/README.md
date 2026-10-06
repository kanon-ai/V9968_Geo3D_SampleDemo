# LUNAR COMMUTE — 通勤が疲れたデモ

> My commute felt like 380,000 km today.
> 通勤が38万キロくらいに感じた。

A quiet Earthrise turns into a cat and rabbit's journey home. They walk to their rocket, board it and leave for Earth; the final camera follows them toward Earth. A silent, automatic **TurboR + V9968 + Geo3D** animation in **SCREEN 8 / EPAL 256 colours**.

美しい地球の出を眺めていたら、猫とうさぎが帰宅するだけのデモでした。月面を歩いてロケットへ乗り込み、最後は地球へ向かいます。無音・操作不要・自動ループです。

## Download and run / 実行方法

[ROM, MP4 and GIF](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/lunar-commute-v0.1.1)

- ROM: **1,048,576 bytes (1 MiB), ASCII16 mapper**.
- Use a V9968 + Geo3D capable openMSX build and its matching machine/extension definitions. A stock openMSX installation is insufficient. TurboR/R800 is the tested CPU configuration.
- Example with the author's evaluation setup: `openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart EARTHRISE-HOME.ROM -romtype ASCII16`.
- Machine names vary by distribution. BIOS, emulator, machine definitions and FPGA bitstreams are not bundled.

V9968とGeo3Dの両方に対応したエミュレータ・機種設定を使用し、ASCII16でROMを挿入してください。通常版openMSXだけでは実行できません。検証はTurboR/R800構成です。

## v0.1.1 — Z80 optimization / Z80最適化

Invisible back-facing polygons are conservatively removed when building each animation frame, reducing CPU-to-Geo3D transfers. Geometry, textures, visible detail and choreography are preserved; existing Z80 unrolled transfers remain in use. No video speed-up.

Dedicated openMSX measurements: **Z80 12.21 → 13.42 fps (+9.9%)**, **R800 21.39 → 21.91 fps (+2.4%)**. All **602 display-page samples per CPU** match v0.1.0 byte-for-byte. Public-source rebuild matches the release ROM. [Measurements](../../docs/validation/lunar-commute-z80.json).

BlueMSX+ experimental-2 also passed full-route and loop checks for the optimized ROM in R800 and forced-Z80 configurations. This is functional validation, not a claim of pixel-exact agreement between emulators or physical hardware speed. Slower CPUs still play the frame-driven animation more slowly.

見えない裏面の転送をROM生成時に省くことでZ80で約9.9%改善。形状・テクスチャ・見えるディテール・演出内容を維持し、両CPUで各602枚の描画ページ一致を確認しました。BlueMSX+でもR800・Z80固定の進行とループを確認。実機未検証で、遅いCPUでは演出の実時間も長くなります。

## Technology and verification / 技術と検証

Geo3D renders textured polygons for Earth, lunar terrain, characters and rocket in real time. V9968 copies the star background and switches display pages. Camera/model matrices and animation are precomputed ROM data, not prerecorded video. Earth lighting is baked into its texture. Conservative off-screen polygon removal reduces transfers. The final zoom is a camera approach, not a change to the video playback rate.

Validated on 2026-10-06 with the author's dedicated integrated openMSX evaluation build (including the previously used concert collision patch, which this demo does not use). Executable SHA256: `7ea5b46eefa1d5333d20497db46da50ffc89437301e5a0131dfb3097f5097b5f`.

A complete 600-frame cycle and restart were captured. Representative frames include Earthrise, walking, boarding and departure. Exported MP4 is approximately 28 seconds, silent, with no speed-up or interpolated frames; GIF reduces temporal resolution to 15 fps. **Physical hardware remains unverified. Z80 evaluation uses a TurboR profile forced to Z80; native MSX2/2+ hardware is untested.** Emulator timing is not a hardware benchmark or a compatibility guarantee for other builds.

600フレームの全編とループ再開を専用openMSXで確認。MP4は約28秒、速度加工・フレーム補間なしです。GIFは15fpsに間引いています。実機は未検証です。Z80評価はTurboRプロファイルをZ80固定にしたもので、MSX2/2+実機の検証ではありません。

### BlueMSX Plus follow-up / 追加検証

The same public ROM also passed a run in **BlueMSX+ V9968-geo3d-experimental-2 (2090cd2, x64)**, with V9968/256kB VRAM, TurboR/R800, explicit ASCII16, CPU speed 100 and VDP command speed 100. Read-only frame-counter sampling covered the full 0–599 route and loop restarts. Representative visual checks showed Earth/terrain, walking characters and the final Earth/rocket close-up. No ROM change was needed for v0.1.0. This is not a pixel-exact cross-emulator comparison or a hardware timing claim. [Validation record](../../docs/validation/lunar-commute-bluemsx.json).

同一公開ROMをBlueMSX+のGeo3D実験版でも追加検証しました。ASCII16を明示し、全600フレームの進行・ループ再開と代表場面の描画を確認。ROM修正は不要でした。画素単位の完全一致試験や実機の速度保証ではありません。

## Artistic astronomy / 天文表現について

This is a visual joke, not an ephemeris or flight simulator. Earth remains fixed in scene space; the reveal uses camera movement and an animated lunar horizon. For a stationary observer on the near side of the real Moon, Earth does not rise daily like the Sun. Lunar geometry, stellar brightness, distances, scale and travel time are staged for readability. The Earth texture is not mirrored.

天体暦や実際の帰還軌道を再現したものではありません。地球はシーン内で固定し、視点と月面の傾きで出現を演出しています。実際の月の表側では、静止した観測者に地球が毎日昇るわけではありません。月面形状・星空の明るさ・距離・縮尺・所要時間は演出です。

## Build / ビルド

Install Python, NumPy, Pillow and SDCC's assembler/linker separately. Set `SDCC_BIN` to the SDCC bin directory, then run `python demos/lunar-commute/build.py` from the repository root. Output: `demos/lunar-commute/out/EARTHRISE-HOME.ROM`. No emulator or BIOS is needed for the build. Generated intermediate files are not release sources.

## License and credits / ライセンス・出典

Original code and contributed assets: repository [MIT license](../../LICENSE), to the extent contributors hold rights. Preserve [Geo3D / V9968 notices](../../THIRD_PARTY_NOTICES.md). AI-generated lunar material, sky and character faces are documented in [asset provenance](assets/PROVENANCE.md); no exclusive rights or absence of all third-party claims are asserted for AI outputs.

**NASA's Earth image is a separate third-party asset, not relicensed under MIT.** Credit: NASA / Reto Stockli, NASA Goddard Space Flight Center. Use is subject to [NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/). NASA does not endorse this demo. See the asset notice for source links.

コード・提供素材は権利を有する範囲でMITを適用します。NASA地球画像はMITへの再許諾対象ではなく、NASAの利用指針に従う別素材です。Geo3D・V9968の上流表示を保持し、AI生成素材の独占的権利は主張しません。

## Disclaimer / 免責事項

Experimental software supplied **as is**, without warranty of compatibility, performance, astronomical accuracy or fitness for a particular purpose. Use at your own risk; liability is limited to the extent permitted by applicable law and the MIT license. Hardware/tool names identify technologies, not endorsement or certification by their creators.

実験的なデモを無保証で提供します。互換性・性能・天文的正確性・特定用途への適合性を保証せず、適用法およびMITライセンスで認められる範囲で責任を負いません。各技術・ツール名の記載は、開発者による公認や動作保証を意味しません。

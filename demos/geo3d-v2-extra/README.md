# Geo3D V2.0 Extra Demos v0.1.0 / V2専用・別バージョン

Eight existing public demos now use **Geo3D V2.0 resident geometry**, extended face indices and VFIRST/FFIRST to reduce repeated CPU uploads. These are separate experimental editions. Original downloads and PAWS & BEATS are unchanged.

公開済み8デモを、**Geo3D V2.0のモデルRAM常駐・拡張面インデックス・VFIRST/FFIRST**を使う別バージョンにしました。従来版、演奏会は変更していません。

[Download eight ROMs and source](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0)

## Run / 実行

- Requires V9968 + **Geo3D V2.0**, ID 20h and 1024-entry RAM configuration (XCTRL high nibble Ah). **Not compatible with Geo3D V1.** An unsupported version stops with a red border; all eight were tested for this rejection.
- Use the author's [openMSX geo3d-v2.0 branch](https://github.com/alexmoncks/openMSX/tree/67811936bee936c15e3fbdbdffe01755fd349876). Tested local build: unmodified source at `67811936bee936c15e3fbdbdffe01755fd349876`, MSVC Release x64. Machine `Panasonic_FS-A1ST_V9968`, extension `geo3d`, **ASCII16** ROM mapper. Use your own legally obtained system ROMs.
- OBSIDIAN is **256 KiB**; the other seven are **1 MiB**, unchanged from their baselines. All are automatic, silent visual demos. No new music or interaction is added.
- Suggested command (machine availability depends on your setup): `openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart ORBITAL-GEO3D-V2.ROM -romtype ASCII16`.
- **Physical cartridges and BlueMSX+ V2 are unverified.** This is the author's development V2 protocol, distinct from existing V1 firmware. Existing emulator-specific limitations remain; no FPGA update is included or implied.

作者版V2 openMSXで検証しています。Geo3D V1では起動時に停止します。ROMマッパーは全てASCII16、容量は旧版のままです。実機・BlueMSX+ V2での動作保証ではありません。BIOS・エミュレータ・FPGAビットストリームは同梱しません。

## Measured improvement / 測定結果

Same V2 emulator, identical scene/texture data, baseline ROM versus new ROM. Numbers are completed display updates per **emulated** second. Z80 means the TurboR profile forced to Z80 for comparison, **not a real MSX2/2+ measurement**. R800/Z80 emulator timings do not establish FPGA performance.

同じV2エミュレータ上で旧ROMと新ROMを比較した描画更新/秒です。Z80欄はTurboRをZ80固定にした測定で、MSX2/2+実機の測定ではありません。

| Demo | R800 old → V2 | Gain | Z80 old → V2 | Gain |
|---|---:|---:|---:|---:|
| OBSIDIAN | 14.98 → 14.98 | +0.0% | 5.12 → 7.24 | +41.5% |
| ORBITAL TYPE REAL | 19.97 → 29.96 | +50.0% | 9.73 → 29.03 | +198.2% |
| ORBITAL | 19.97 → 29.96 | +50.0% | 9.73 → 29.03 | +198.2% |
| SKYBOUND | 20.13 → 29.93 | +48.7% | 11.92 → 27.45 | +130.2% |
| VECTOR RUSH | 19.97 → 28.54 | +42.9% | 8.98 → 17.17 | +91.2% |
| FOUR SEASONS | 27.23 → 29.93 | +9.9% | 12.68 → 16.76 | +32.1% |
| BASIC FUNCTIONS | 29.96 → 29.96 | -0.0% | 29.96 → 29.96 | +0.0% |
| LUNAR COMMUTE | 21.10 → 29.09 | +37.9% | 11.94 → 22.54 | +88.8% |

OBSIDIAN is already near its R800 frame-pacing limit; its main gain here is on Z80. BASIC FUNCTIONS remains near 30 updates/s on both CPUs: this edition demonstrates model residency, **not an observed FPS increase**. Improvements in the other demos come from ROM-side transfer reduction, not merely swapping emulator executables. FOUR SEASONS also uses an unrolled Geo3D-only transfer loop.

OBSIDIANはR800側のフレーム待ち上限に近く、主な改善はZ80側です。BASIC FUNCTIONSは両CPUとも約30更新/秒のままで、fps向上をうたう版ではありません。他のデモの改善はエミュレータを替えただけではなく、ROM側の転送削減によるものです。四季にはGeo3D転送ループの展開も含みます。

Original per-update motion steps are preserved. Faster rendering therefore shortens playback time where the old renderer was slower; no video speed-up or frame interpolation is used. There is no audio to desynchronize in this set.

1描画ごとの動きは旧版を維持しています。描画が速くなった分、演出全体の所要時間も短くなる場合があります。動画の早送りやフレーム補間による高速化ではありません。

## Implementation / 実装

- The builder deduplicates byte-identical source meshes, converts 8-bit face indices to V2's 10-bit/12-byte face format, and packs them back into geometry-only ROM banks. Vertex positions, normals, winding, UVs and face order are preserved and asserted during the build. Texture, palette, motion-matrix, lighting and HUD asset bytes are protected; scene records change only model-bank/pointer fields.
- Several geometry slots coexist in Geo3D RAM. Each descriptor selects VFIRST/FFIRST and vertex/face counts. Cache hits avoid vertex/face/UV uploads; a changed vertex pose can reuse identical face/UV data. Cache keys are reset at startup. Model-RAM ranges and indices are checked by the builder.
- FOUR SEASONS has a specialized layout: the four seasonal topologies occupy **654 vertex slots and 816 face/UV slots**. Faces/UVs remain resident across seasonal transitions; only changing pose vertices are uploaded. The transfer-loop optimization affects Geo3D, not VDP writes.
- SKYBOUND's terrain atlas shares the upper halves of original model banks 2/3; both banks are explicitly excluded from repacking. BASIC FUNCTIONS retains the dynamic texture-origin selection independently of relocated model banks.
- Version/capacity checks reject incompatible hardware before the scene loop. Geometry is still rendered by Geo3D + V9968 at runtime; this does not turn the demo into prerecorded video.

複数モデルをGeo3D RAMに保持し、モデルが変わった箇所だけを転送します。四季は4季節の面・UVを常駐させ、形が変わる頂点だけを更新します。頂点・面・UVの変換検査に加え、元の画像素材・カメラ・演出データが変更されていないことをビルド時に検証しています。

## Validation / 検証範囲

2026-10-15: each demo covered at least one scene loop plus wraparound, on both R800 and forced-Z80 configurations. FOUR SEASONS covered four loops. **10792 completed display-VRAM pages matched byte for byte** between old and new ROMs. A page comparison includes every update in the measured interval, not selected screenshots. Representative views were also inspected.

各デモを1周以上とループ境界まで、R800・Z80固定の両条件で比較しました（四季は4周）。測定区間の全表示VRAM、計10792画面が旧版と一致しています。抽出画像だけでの一致判定ではありません。

Method: independent userdata/home directories; same machine/system ROM files; speed 100; throttle disabled to skip host waiting; timestamps from `machine_info time`. Completion counter E420h sampled every 1 ms of emulated time, excluding uninitialized 65535. Counter sequences match. SCREEN 5/8 page selection uses R#2. Sound output is disabled. The forced-Z80 test changes only the existing BIOS CPU-selection immediate from 81h to 80h in temporary test copies; distributed ROMs retain their normal CPU selection.

The author's [timing caveat](https://github.com/alexmoncks/openMSX/blob/67811936bee936c15e3fbdbdffe01755fd349876/README.geo3d.md) remains: geometry consumes no emulated time. FPGA heap-sort/divider gains are not measured here. No claim of cycle-exact timing, real-cartridge speed, ordinary MSX2+ validation or BlueMSX+ V2 validation is made.

[Measurements and hashes](validation/comparison.json) · [V1 rejection tests](validation/version-gate.json) · [Public baseline allowlist](manifest.json). CSV files contain raw emulated timestamps. Existing detailed limitations in each original demo README still apply.

## Build / ビルド

Python 3 and SDCC's `sdasz80` / `sdldz80` are required. No NumPy/Pillow/image generation is required for this conversion. Set `SDCC_BIN` to your SDCC bin directory.

```powershell
$env:SDCC_BIN = 'C:/path/to/sdcc/bin'
python fetch_inputs.py
python build_v2.py
# Or rebuild one: python build_v2.py four-seasons
```

`fetch_inputs.py` obtains only the already-public baseline ROMs listed in `manifest.json`, checks their SHA-256, and preserves existing files. `build_v2.py` combines their unchanged assets with the editable Z80 sources in `sources/` and `cache.asm`. Generated assembly, ROMs and build checks go into `out/<demo>/`. For original asset-generation sources, see the corresponding original demo directories in this repository.

既存の公開ROMをハッシュ確認付きで取得し、その素材を維持したまま、新しいZ80コードと拡張モデル形式で再構築します。出力は `out/<demo>/` です。元の素材生成ソースは各従来版ディレクトリを参照してください。

## License and disclaimer / ライセンス・免責

Original code and geometry are covered by this repository's [MIT License](../../LICENSE), to the extent rights are held. Retain [third-party notices](../../THIRD_PARTY_NOTICES.md) and [Geo3D/V9968 notices](../../LICENSES). This conversion does not change the licensing of existing textures/fonts/other media or grant new rights in them. AI-created texture notices from the original releases remain applicable. LUNAR COMMUTE's NASA Earth imagery retains its NASA/Reto Stockli credit and applicable NASA media guidelines; NASA imagery is not relicensed as exclusively owned artwork. No new third-party artwork, music or models were added.

既存素材のライセンス・出典は従来版を引き継ぎます。Geo3D作者Alex Moncks氏、V9968作者HRA!氏への表記を維持します。NASA素材を含む画像の個別条件はMITコードと区別してください。

Experimental software, provided **as is, without warranty**. Emulator measurements are not a guarantee of compatibility, speed or fitness on physical hardware. No endorsement by hardware/emulator authors or NASA is implied. Users are responsible for their own emulator/system-ROM licensing and backups. Emulator binaries, BIOS, machine ROMs, FPGA sources/bitstreams and private demos are not bundled.

本版は実験用・無保証です。実機での動作・性能・用途適合性を保証せず、各作者やNASAによる公認を意味しません。エミュレータ・BIOS等は利用者が適法に用意してください。非公開デモは含みません。

# Internal 98h / External 88h ROM editions — 内蔵用・外付け用

[Download / ダウンロード](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/dual-io-v0.1.0)

Choose the **I/O connection** and **Geo3D protocol version** independently. The two archives each contain 28 current public variants, arranged into `Geo3D-V1/` and `Geo3D-V2/`. Original releases remain available. This package adds external-I/O builds; it does not upgrade your FPGA firmware.

接続方式とGeo3Dのバージョンをそれぞれ選んでください。各ZIPには現行の公開28種類を収録し、`Geo3D-V1/` と `Geo3D-V2/` に分けています。従来版は残しています。FPGAを書き換えるパッケージではありません。

| Archive / ZIP | Connection / 接続 | V9968 ports | Geo3D ports |
|---|---|---|---|
| `Geo3D-Demos-INTERNAL-98H-v0.1.0.zip` | V9968 as the main VDP / 内蔵VDP構成 | 98h–9Ch | 9Dh / 9Fh |
| `Geo3D-Demos-EXTERNAL-88H-v0.1.0.zip` | Cartridge alongside the built-in VDP / 外付け2nd VDP | 88h–8Ch | 8Dh / 8Fh |

For an external cartridge set to 88h, use `EXTERNAL-88H` and view the **cartridge's video output**. The computer's original VDP output is separate. Select V1 or V2 to match your Geo3D firmware. Do not infer protocol compatibility from the I/O suffix.

88h設定の外付けカートリッジには `EXTERNAL-88H` を使い、**カートリッジ側の映像出力**をご覧ください。本体VDP側の画面は別です。V1/V2は搭載ファームウェアに合わせて選びます。

## ROM inventory / ROM一覧

Append `-INTERNAL-98H.ROM` or `-EXTERNAL-88H.ROM` to the stem below. All ROMs use **ASCII16**. Required CPU, OPLL, controls and special emulator conditions remain those of the original release.

下記の名前に `-INTERNAL-98H.ROM` または `-EXTERNAL-88H.ROM` が付きます。マッパーは全て **ASCII16**。CPU・音源・操作方法などの条件は元版を引き継ぎます。

| ROM stem | Geo3D | Size / 容量 | Baseline / 元版 |
|---|---|---:|---|
| `OBSIDIAN` | V1 | 256 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `ORBITAL` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `ORBITAL-TYPE-REAL` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `SKYBOUND` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `VECTOR-RUSH` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `BULLRUSH` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `BULLRUSH-CROWD` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `NIGHT-RAVEN` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `NIGHT-RAVEN-FLIGHT` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) |
| `FOUR-SEASONS` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/four-seasons-v0.2.0) |
| `GEO3D-BASICS` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-basics-v0.1.0) |
| `LUNAR-COMMUTE` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/lunar-commute-v0.1.2) |
| `PAWS-BEATS` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/paws-beats-v0.1.1) |
| `NIGHT-RAVEN-OPLL-TEST` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-opll-test-v0.1.0) |
| `NIGHT-RAVEN-THREE-STAGE` | V1 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-three-stage-v0.5.0) |
| `BULLRUSH-CROWD-COCKPIT` | V1 | 2048 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/bullrush-crowd-cockpit-v0.1.0) |
| `OBSIDIAN-V2` | V2 | 256 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `ORBITAL-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `ORBITAL-TYPE-REAL-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `SKYBOUND-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `VECTOR-RUSH-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `FOUR-SEASONS-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `GEO3D-BASICS-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `LUNAR-COMMUTE-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/geo3d-v2-extra-v0.1.0) |
| `BULLRUSH-COCKPIT-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/bullrush-geo3d-v2-v0.1.0) |
| `BULLRUSH-CROWD-COCKPIT-V2` | V2 | 2048 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/bullrush-geo3d-v2-v0.1.0) |
| `NIGHT-RAVEN-GEO3D-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-geo3d-v2-v0.1.0) |
| `NIGHT-RAVEN-THREE-STAGE-GEO3D-V2` | V2 | 1024 KiB | [Original release](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-three-stage-geo3d-v2-v0.1.0) |

## Run / 実行例

With a matching developer openMSX installation and legally obtained system ROMs:

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart FOUR-SEASONS-V2-INTERNAL-98H.ROM -romtype ASCII16
openmsx -machine Panasonic_FS-A1ST -ext HRA_V9968 -ext geo3d88 -cart FOUR-SEASONS-V2-EXTERNAL-88H.ROM -romtype ASCII16
```

For external output, select `V9968` as the video source (console: `set videosource V9968` after the machine starts). Machine/extension names depend on the emulator installation. V2 ROMs require a V2-capable build.

外付け側は起動後に映像ソースを `V9968` に切り替えます。エミュレータの機種・拡張定義名は環境によって異なります。

## What changed / 変更点

The internal ROMs are byte-identical to their hash-pinned public baselines. The builder assembles each source snapshot and first verifies every emitted code/data byte against the published ROM. It then changes only explicit VDP/Geo3D I/O operands in the source, assembles again, and checks that only those port bytes differ in the external ROM. Texture, geometry, motion, gameplay and music assets remain byte-identical. This is not an indiscriminate binary search-and-replace.

内蔵用は元の公開ROMと完全一致です。外付け用は、公開ROMと一致することを確認したソースのVDP/Geo3D I/O指定だけを変更しています。画像・モデル・モーション・ゲーム処理・音楽素材は変更していません。

These programs poll **S#2 bit 6 on the selected VDP** for vertical blank; they do not use H.TIMI/H.KEYI as frame hooks. The external build reads status through **89h**, not the built-in VDP's 99h. Any future interrupt-driven external-VDP implementation must handle the external cause/acknowledgement at H.KEYI rather than treating H.TIMI as the external VBlank source.

同期は対象VDPの **S#2 bit6を直接読む方式**です。88h版は89hから外付けVDPの状態を読みます。H.TIMI/H.KEYIによるフレーム同期は使いません。将来割り込み方式を導入する場合は、H.KEYIで外付けVDPの割り込み要因を確認・解除する必要があります。

## Validation and limitations / 検証と制限

- 2026-10-19: all 28 variants were compared using a TurboR profile with an internal V9968 versus a normal TurboR VDP plus an external HRA_V9968 and geo3d88. **18,704 paired display-VRAM pages and their palettes matched** (650 updates per variant; 902 for each LUNAR COMMUTE edition). Interactive tests apply keyboard input at the same input-routine entry. This is a bounded regression test, not proof of every gameplay branch.
- Four additional C-BIOS MSX2+ / Z80 comparisons (FOUR SEASONS V1/V2, ORBITAL V2, LUNAR COMMUTE V2) matched **390 pages each**. Internal V9968 definitions include all five I/O ports; the external comparison retains a V9958/128 KiB built-in VDP.
- PAWS & BEATS collision counters and frame-driven music registers matched. Five OPLL editions also matched their common write-sequence prefixes over 32 emulated seconds. Real-time music and rendering run on different clocks, so frame-by-frame audio-register equality is not expected for timer-driven scores. This test does not measure analogue audio quality.
- External-output screenshots were inspected for all 28 variants.
- V1: existing integrated V9968/Geo3D evaluation emulator; V2: author's openMSX `67811936bee936c15e3fbdbdffe01755fd349876`. PAWS & BEATS retains its previously documented test-only sprite-collision patch requirement. **Changing I/O ports does not supply that patch or make its transparent collision effect work on unsupported emulators.**
- **Physical hardware and BlueMSX+ external-88h operation remain unverified.** These tests do not establish real-cartridge bus timing, FPGA speed, all CPU support, or compatibility with every emulator/firmware version. Existing CPU limitations (including TurboR-only music experiments) still apply. No emulator or firmware changes are included.

TurboR構成で28種類・計18,704組の表示VRAMとパレットが一致しました。代表4種類はC-BIOS MSX2+構成でも各390画面一致しています。演奏会の星は従来の専用衝突判定パッチに依存します。**実機およびBlueMSX+の外付け88h構成は未検証**です。実機動作や性能を保証するものではありません。

[Display comparison](validation/comparison.json) · [MSX2+ checks](validation/msx2plus.json) · [OPLL checks](validation/opll.json) · [Public input hashes](manifest.json)

## Rebuild / 再ビルド

Python 3 and SDCC (`sdasz80`, `sdldz80`) are required. The source ZIP contains only sources/notices; the fetch script downloads the explicitly listed public baseline ROMs and verifies SHA-256. Existing files are verified, not overwritten.

```powershell
$env:SDCC_BIN = 'C:/path/to/sdcc/bin'
python fetch_inputs.py
python build_dual.py
# Optional single variant:
python build_dual.py four-seasons-v2
```

Outputs appear in `out/<variant>/`. Original asset-generation sources remain in the corresponding demo directories.

## License and disclaimer / ライセンス・免責

Code is provided under the repository's [MIT license](../../LICENSE), to the extent rights are held. Retain [third-party/media notices](../../THIRD_PARTY_NOTICES.md) and [Geo3D/V9968 notices](../../LICENSES). Existing NASA imagery credits, AI-texture notices and other asset-specific conditions are unchanged. No new third-party assets are added.

Provided **as is, without warranty**. No endorsement by hardware/emulator authors or NASA is implied. Users must provide legally obtained system ROMs and compatible equipment. BIOS, emulator binaries, FPGA bitstreams and private works are not included.

既存のライセンス・素材出典を引き継ぎます。本版は無保証です。各作者・NASAによる公認を意味せず、実機での動作・性能を保証しません。BIOS・エミュレータ・FPGAデータは同梱しません。

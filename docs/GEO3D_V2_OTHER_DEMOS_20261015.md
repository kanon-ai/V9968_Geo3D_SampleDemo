# Geo3D v2.0: existing demo performance / 既存デモの速度比較

2026-10-15 — **Replacing the emulator alone produced no measurable speed gain in these nine unchanged public ROMs.** All completed 512 observed display updates; 45 sampled display-VRAM pages matched byte for byte. Existing downloads remain unchanged.

**公開済み9本は、エミュレータの置き換えだけでは実質的な速度向上がありませんでした。** 各512回の描画更新が進行し、抽出した45画面の表示VRAMが新旧で一致しました。既存ROMの差し替えはありません。

BULLRUSH/robot and NIGHT RAVEN editions are outside this report. Their separately published v2 editions reduce CPU transfers through resident model data; those gains must not be attributed to an emulator-only upgrade.

ロボット系・NIGHT RAVEN系は今回の対象外です。既公開のV2専用版で得られた改善は、モデル常駐化などROM側の転送削減を含む結果であり、エミュレータ交換だけの効果とは区別してください。

## Results / 結果

Completed display updates per emulated second; **not host speed, monitor refresh rate or physical-hardware FPS**. Values cover the tested opening segment, not necessarily a complete loop or every scene.

エミュレーション時間1秒あたりの描画更新回数です。ホストPCの処理速度や実機のfpsではありません。冒頭の測定区間の平均で、全シーン・全周回の保証ではありません。

| Demo | Previous openMSX | v2 openMSX | Change / 変化 |
|---|---:|---:|---:|
| OBSIDIAN | 14.980 | 14.980 | 0.000% |
| ORBITAL TYPE REAL | 19.974 | 19.974 | 0.000% |
| ORBITAL | 19.975 | 19.975 | 0.000% |
| SKYBOUND | 20.132 | 20.132 | 0.000% |
| VECTOR RUSH | 19.975 | 19.975 | 0.000% |
| FOUR SEASONS | 27.389 | 27.389 | 0.000% |
| BASIC FUNCTIONS | 29.962 | 29.962 | 0.000% |
| PAWS & BEATS | 19.974 | 19.974 | 0.000% |
| LUNAR COMMUTE | 22.060 | 22.060 | 0.000% |

The tiny ORBITAL TYPE REAL difference is below 0.0001%; treat it as unchanged, not an improvement.
ORBITAL TYPE REALの微小差は0.0001%未満であり、高速化とは扱いません。

## Why / 高速化が出ない理由

The author's [pinned emulator README](https://github.com/alexmoncks/openMSX/blob/67811936bee936c15e3fbdbdffe01755fd349876/README.geo3d.md) states that geometry consumes no emulated time. FPGA heap-sort/divider improvements therefore cannot be measured by this emulator comparison. V2 also expands model capacity and adds VFIRST/FFIRST/EFIRST; using these to reduce CPU transfers requires a separate ROM redesign. Such a redesign was not benchmarked for these nine demos, so no benefit is claimed here.

作者の説明では幾何演算にエミュレーション時間を計上しないため、FPGA側のソート・除算高速化はこの比較では測れません。V2のメモリ拡張や処理開始位置指定を用いた転送削減にはROMの別途改修が必要です。この9本ではその改修効果を測定していません。今回の結果は「実機でも速くならない」という意味ではありません。

V2 is the author's development branch, distinct from the v1 firmware in the official V9968 distribution. Its README describes it as not hardware-tested. Do not upgrade FPGA firmware based on these emulator results alone.

V2は作者の開発ブランチで、公式V9968配布のv1ファームとは別です。作者READMEでも実機未検証とされています。本結果はFPGA更新の動作保証ではありません。

## Method / 測定条件

- Previous author openMSX: `de29fb854885a38251c03e24596ad4ff95770ef2` (`geo3d`).
- Latest author v2 branch checked on the report date: `67811936bee936c15e3fbdbdffe01755fd349876` (`geo3d-v2.0`). Existing isolated MSVC Release x64 build reused after all 1,361 local source/README files matched upstream Git blob hashes. No emulator source changes.
- V2 cartridge reference: `885cff1fc5c3e8c38af9ac39112b7bdd73371b9e` (`geo3d-v2.0`).
- Same `Panasonic_FS-A1ST_V9968` TurboR/R800 profile, system ROMs, Geo3D extension, ASCII16 mapper, speed 100. Independent user/home folders. `throttle off` removes host waiting only; timestamps come from `machine_info time`. Audio output disabled for timing; no new audio validation.
- Each identical ROM was downloaded from this repository's public Releases, with asset SHA-256 checked. No private ROMs were used. See the [allowlist and hashes](validation/geo3d-v2-other-demos-20261015/manifest.json).
- Observe the display-completion counter at E420h every 1 ms of emulated time. Measure 511 intervals across 512 updates. Some ROMs increment this counter by 3; count update events, not the raw counter value. Both executions had identical counter sequences and consistent increments (1 or 3).
- Compare display VRAM at updates 30, 120, 250, 400 and 510. SCREEN 5 uses 27,136 bytes; SCREEN 8 uses 54,272 bytes, with displayed page selected through R#2. All 45 pairs matched. Host-rendered screenshot presentation may skip frames with throttle off and was not used for byte equality.
- This is an opening-segment performance/regression sample, not exhaustive gameplay, all-scene, Z80, audio or hardware certification. No new BlueMSX+ validation is claimed; existing release-specific validation remains applicable.

同一ROM・同一TurboR/R800構成で比較しました。測定は512描画更新の間隔、画面一致は各5点の抽出です。Z80・音声・BlueMSX+・実機を今回新たに検証したという意味ではありません。エミュレータ・BIOS・個人設定・非公開デモは配布しません。

## PAWS & BEATS limitation / 演奏会の制限

PAWS & BEATS' published collision-driven sparkle validation used a dedicated sprite-collision patch. Matching these two unmodified author builds does **not** validate that patch-dependent effect. This report confirms animation progress and sampled pages only; retain the [release's documented environment and limitations](../demos/paws-beats/README.md) for the full effect. No collision workaround or replacement ROM was introduced.

演奏会の接触による星の演出は、公開時に専用パッチ版で検証したものです。今回の無改変作者版同士の一致をもって、その演出まで対応したとは判断しません。完全な演出の条件は既存READMEのままです。

## Data, license and disclaimer / 記録・ライセンス・免責

[Timing and executable hashes](validation/geo3d-v2-other-demos-20261015/results.json) · [Page comparison](validation/geo3d-v2-other-demos-20261015/comparison.json) · [Source verification](validation/geo3d-v2-other-demos-20261015/source-verification.json). Numbered old/v2 CSV pairs follow the manifest order and preserve raw emulated timestamps.

Only this report and its measurement records were added. Demo code, ROMs, media and existing licenses are unchanged. Original project code remains under the repository's MIT terms; third-party assets and music retain their separate notices. Measurements are provided without warranty and do not establish performance or compatibility on physical cartridges.

更新は本説明と測定記録のみです。デモ本体・配布ROM・映像・既存ライセンスは変更していません。第三者素材・音楽の個別条件を含む従来の表記を維持します。測定結果は無保証で、実機の性能・互換性を保証しません。

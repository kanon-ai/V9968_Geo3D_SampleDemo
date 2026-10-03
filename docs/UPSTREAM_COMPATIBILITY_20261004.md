# Upstream compatibility audit / 上流互換性確認 — 2026-10-04

## Result / 結論

**Keep the existing Geo3D openMSX baseline. No emulator executable or demo ROM was replaced.** The cartridge integration has caught up with HRA!'s official V9968 source, but the published openMSX `geo3d` branch is still the previously tested revision. The repository's default `msx2pp` branch includes V9968 fixes but does not contain the Geo3D device. Switching the runtime to that branch would remove the device needed by all eleven demos.

**現行のGeo3D対応openMSXを維持します。エミュレータ本体・デモROMの更新はありません。** カートリッジ側はHRA氏の公式V9968ソースに追従していましたが、openMSXの `geo3d` ブランチは従来の検証版のままでした。既定の `msx2pp` ブランチにはV9968修正がある一方、Geo3Dデバイスがありません。そのため、今回の調査では移行条件を満たしません。独自に両ブランチを混合した版を公式最新版として扱うこともしません。

## Compared revisions / 比較した版

| Repository / branch | Commit |
|---|---|
| HRA V9968 / main | [`dceec5a50c7c2a5d107a0c6ce8d10cf232e43474`](https://github.com/hra1129/V9968_Cartridge/tree/dceec5a50c7c2a5d107a0c6ce8d10cf232e43474) |
| Alex V9968 + Geo3D / main | [`873188ab98efd13d17149f6e8f80070be0362d8d`](https://github.com/alexmoncks/V9968_Cartridge/tree/873188ab98efd13d17149f6e8f80070be0362d8d) |
| Alex openMSX / geo3d — retained baseline | [`de29fb854885a38251c03e24596ad4ff95770ef2`](https://github.com/alexmoncks/openMSX/tree/de29fb854885a38251c03e24596ad4ff95770ef2) |
| Alex openMSX / msx2pp — default branch | [`c620b693726b512c6860c7a0e01d3abf7b588b20`](https://github.com/alexmoncks/openMSX/tree/c620b693726b512c6860c7a0e01d3abf7b588b20) |

These are the branch heads observed on the audit date, not a promise about future updates. `geo3d`'s commit date is 2026-09-24 -03:00; `msx2pp`'s is 2026-09-23 +09:00. The recent cartridge update does not imply that the emulator branch was also updated.

## Cartridge findings / カートリッジ側

- In `fpga/V9968_Cartridge_TangNano20K/src/`, all **90 Verilog/constraint files** match by Git blob ID. Of 703 files under that source directory, the only difference is `geo3d/readme.md`.
- HRA's official project now contains Geo3D. Alex's `geo3d/rtl/` is also unchanged from the previously examined cartridge revision `c938150507f9763ac41720104135096776d9f2af`.
- The previously missing shared command/VRAM-cache changes, V58 handling and display-related fixes are therefore present in the common official V9968 source. This is source comparison, not a new FPGA synthesis or physical test.
- Generated bitstreams/build reports differ; source agreement does **not** mean identical binaries. Alex also retains a separate `_geo3d` project and additional demo/test files. Among the Verilog/constraint paths shared with that separate project, only the top-level cartridge module and `v9968/vdp.v` differ: inspection found formatting, comments and the VDP instance name (`u_v9968` versus `u_v9958`), with no logic change in those diffs. Older/test-only file inventories differ too.

公式プロジェクトの `src/` にあるVerilog・制約ファイル90本はGitの内容ハッシュで一致しました。ディレクトリ内703ファイルの差はGeo3Dのreadmeだけです。以前未統合だったV9968側の共有キャッシュ・V58・表示関連の変更は共通ソースに含まれています。Geo3D単体RTLも前回調査版から変更がありません。ただし生成済みビットストリーム等は異なり、バイナリ一致や実機での互換性を証明したものではありません。

## Emulator findings / エミュレータ側

| Item | Current `geo3d` branch | Default `msx2pp` branch |
|---|---|---|
| Geo3DCore / Geo3D device and XML extension | Present | Absent |
| Change since our tested `de29fb8` baseline | None | Separate branch, not a Geo3D update |
| Newer V58/FID/EVR capability-mask fixes | Not the same implementation | Present in `1d0ac55` / `c620b69` |
| Port #4 bit 7 extended-register lock | Not implemented | Not implemented |
| Explicit table-A17 clearing when writing V58=1 | Not implemented | Not implemented |

The current cartridge README still directs emulator users to the `geo3d` branch and explicitly describes the missing Port #4 lock and approximate timing. In the `msx2pp` source, Port #4 handles interrupt flags, while the R#21 handler updates chip ID and EVR mode; it does not implement the FPGA's lock or explicit table-A17 clearing. Do not describe either branch as a complete model of the latest cartridge.

現行カートリッジのREADMEもエミュレータは `geo3d` ブランチを案内し、Port #4ロック未実装とタイミングの限界を明記しています。`msx2pp` のV58関連修正だけをもって、最新実機との完全一致とは判断できません。

Pinned sources: [cartridge README](https://github.com/alexmoncks/V9968_Cartridge/blob/873188ab98efd13d17149f6e8f80070be0362d8d/geo3d/README.md), [FPGA CPU interface](https://github.com/hra1129/V9968_Cartridge/blob/dceec5a50c7c2a5d107a0c6ce8d10cf232e43474/fpga/V9968_Cartridge_TangNano20K/src/v9968/vdp_cpu_interface.v), [msx2pp VDP](https://github.com/alexmoncks/openMSX/blob/c620b693726b512c6860c7a0e01d3abf7b588b20/src/video/VDP.cc), [Geo3D emulator README](https://github.com/alexmoncks/openMSX/blob/de29fb854885a38251c03e24596ad4ff95770ef2/README.geo3d.md).

## All public demos / 公開11デモへの影響

BULLRUSH, BULLRUSH CROWD, FOUR SEASONS, BASIC FUNCTIONS, NIGHT RAVEN, NIGHT RAVEN FLIGHT, OBSIDIAN, ORBITAL, ORBITAL TYPE REAL, SKYBOUND and VECTOR RUSH were checked at source level.

All eleven explicitly write zero to Port #4 (`9Ch`) before their extended-register initialization, then set R#21 to zero for V9968 mode. Their R#20 values are 1 or 17 (HS, optionally EPAL). This startup sequence already accommodates the hardware lock and does not need conversion to the older independent ECOM/EVR layout. The inspected runtimes do not switch back to V58=1 during playback. Geo3D's RTL interface has not changed in the compared revisions.

全11本とも拡張レジスター設定前にPort #4へ0を書き込み、その後R#21=0でV9968モードへ移行しています。R#20は1または17です。実機の拡張レジスターロックを解除する初期化はすでにあり、旧ECOM/EVR方式へ戻す必要はありません。再生中にV58=1へ戻す処理もありません。今回の上流差分から移行が必要と判断したROMは **0本** です。

This is a **static impact audit**, not an all-hardware compatibility guarantee. No new emulator build was adopted, so the existing runtime/display validation remains the applicable evidence; no new hardware or BlueMSX+ validation is claimed. Existing I/O-base requirements (98h/9Dh/9Fh in these ROMs) remain unchanged.

本確認はソース上の影響調査です。新エミュレータを採用していないため、動作検証の根拠は既存の検証記録のままです。新たな実機・BlueMSX+検証を行ったという意味ではありません。ROMのI/Oアドレス条件も変更していません。

[Machine-readable audit / 調査記録](validation/upstream-audit-20261004.json)

## Next migration gate / 次回の移行条件

Adopt a published Geo3D-capable emulator revision after its V9968 changes are checked against the official RTL and the demos pass runtime regression tests. Until then, retain `de29fb8` as the evaluation baseline, with its documented limitations. Existing MIT licenses, upstream notices and disclaimers are unchanged.

今後、Geo3Dを含む公開エミュレータ版にV9968修正が統合された段階で再照合し、デモの回帰検証後に移行します。それまでは制限を明記した現行 `de29fb8` を評価基準として維持します。ライセンス・第三者表記・免責事項は変更しません。

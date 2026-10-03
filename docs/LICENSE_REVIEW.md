# License review / ライセンス確認

確認日: 2026-09-29。公開するファイルと固定した上流ソースのライセンス表記を確認しました。これは配布物の来歴・表記の記録であり、第三者の権利を保証する法的鑑定ではありません。

| 対象 | 確認・公開時の扱い |
|---|---|
| 独自デモのPython・Z80ソース、形状、HUD字体 | 本リポジトリのMIT License |
| Geo3Dの仕様・初期化・転送例 | 固定した上流READMEとZ80例にMIT / Copyright 2026 Alex Moncksの表記。MIT全文と帰属を保持 |
| V9968の設計資料 | 上流MIT / Copyright 2026 HRA!を確認。設計RTL・ビットストリームは配布しない |
| openMSX | 上流GPL表記を確認。本体、DLL、機種定義、BIOSは配布せず作者のリポジトリを案内 |
| 地形、地球、月の画像 | 参照画像なしのAI生成。生成元PNGとプロンプトを公開。独占的な権利を主張せず、保有する権利の範囲でMIT提供 |
| 動画の文字 | ローカルフォントでレンダリング済み。フォントファイルは同梱しない |
| コンパイラ、Pythonパッケージ、ffmpeg | 利用者が別途導入。実行ファイルやパッケージを同梱しない |

公開対象はドライブ・フライト・地球/月の3本のみです。ほかのデモ、評価用の上流checkout、商用BIOS、エミュレータ環境、個人の設定・保存データは含めません。

The release uses MIT for project-owned material, preserves upstream MIT credits, and excludes emulator/tool executables, firmware and third-party source trees. See [full notices](../THIRD_PARTY_NOTICES.md). AI-generated assets are licensed only to the extent rights are held; no rights clearance or endorsement guarantee is made.


## NIGHT RAVEN (v0.2.0)

See [NIGHT RAVEN usage, technical details, validation and license review](NIGHT_RAVEN.md). The existing three demos and v0.1.0 assets are unchanged.

## OBSIDIAN / TITAN PASS (v0.2.0)

[起動・ビルド・技術・検証・素材の来歴](OBSIDIAN.md)。256KiB / ASCII16、無音の自動再生デモです。


## BULLRUSH (2026-10-03)

[詳細と免責](BULLRUSH.md)。公開対象の独自ソース、手続き的形状、HUD、参照画像なしのAI生成テクスチャとその来歴を確認。MITで提供し、Geo3D / V9968の既存MIT帰属と全文を保持します。商用ゲーム素材、BIOS、エミュレータ、フォント、開発ツールは同梱しません。AI素材は保有する権利の範囲で提供します。


## BULLRUSH CROWD (2026-10-03)

The separate crowd load experiment in demos/bullrush-crowd reuses BULLRUSH code and the same reference-free AI-generated atlas, with original crowd scheduling changes. The same MIT and retained Geo3D/V9968 notices apply. Asset provenance is included in assets/PROVENANCE.md. No emulator, BIOS, firmware, tool binaries or font files are included. This is an emulator-tested experiment, not physical-hardware certification.

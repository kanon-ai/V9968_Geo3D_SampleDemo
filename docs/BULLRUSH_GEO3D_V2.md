# BULLRUSH — Geo3D V2.0対応版 / V2.0 edition

通常2機版と5機のにぎやか版を独立したバージョンとして提供します。旧版はそのまま利用できます。自動走行・無音の技術デモで、操作可能なゲームではありません。

## 必要環境・操作

TurboR/R800 + V9968 + **Geo3D v2.0（ID 0x20、1024エントリー構成）**。通常版1 MiB、5機版2 MiB、どちらもASCII16。v1や異なる容量構成では起動を停止します。

[作者openMSX geo3d-v2.0](https://github.com/alexmoncks/openMSX/tree/geo3d-v2.0) の commit `67811936bee936c15e3fbdbdffe01755fd349876` で確認しました。Geo3D v1用のエミュレータ・ファームウェアとは互換ではありません。BIOSと対応機種設定は利用者が正当に用意してください。

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart BULLRUSH-COCKPIT-GEO3D-V2.ROM -romtype ASCII16
```

5機版はROM名を `BULLRUSH-CROWD-COCKPIT-GEO3D-V2.ROM` に変更。C: 視点切替、T: テクスチャ切替。1周目追尾、2周目コックピット、以降交互です。

## 技術

Geo3Dの拡張面メモリへ静的な面情報を一度だけ転送し、FFIRSTで選択します。0–255は建物・遮蔽作業用、256から車輪、512から自機、640から青機、768から赤機（5機版）。FADDR_Hで高位アドレスを設定します。頂点番号は0–255と旧形式面ストリームを維持。関節頂点は毎回更新し、面の再転送を削減しました。

ポリゴン描画はリアルタイムです。経路・カメラ・関節姿勢・遮蔽データは事前計算。汎用Zバッファ・機体間衝突・自由移動AIは未実装で、機体が重なる場合があります。v2の全機能を使うデモではありません。

## 検証（2026-10-15）

同じv2エミュレータで旧ROMと新ROMの各視点378更新を比較しました。

|版・視点|旧ROM fps|V2対応ROM fps|改善|
|---|---:|---:|---:|
|通常・追尾|13.59|15.99|17.6%|
|通常・コックピット|16.99|17.98|5.8%|
|5機・追尾|11.87|14.27|20.3%|
|5機・コックピット|14.67|16.61|13.2%|

両版各759枚の完成表示VRAMが旧版と一致。C/T切替確認済み。[測定値・ROM SHA256](validation/bullrush-geo3d-v2-results.json)。このopenMSXは幾何計算の処理時間をモデル化しておらず、改善は転送削減によるエミュレーション時間の差です。**実機性能・最大性能を示す数値ではありません。BlueMSX+ v2・実機・FPGAは未検証、Z80での本版検証も未実施です。** 他デモの両エミュレータ検証結果は本版に適用できません。

GIFとMP4は等速・無音、速度変更・フレーム補間なし。通常約44.79秒、5機約49.33秒、両GIFとも15MB未満です。

## ビルド

Python 3、NumPy、Pillow、SDCCが必要です。SDCC binをPATHまたはSDCC_BINに設定してください。CROWD_EXTRASは未設定（既定3）のままにします。

```text
python -m pip install -r demos/bullrush-cockpit-v2/requirements.txt
python demos/bullrush-cockpit-v2/build.py
python demos/bullrush-crowd-cockpit-v2/build.py
```

各フォルダのout/BULLRUSH.ROMに出力します。

## ライセンス・免責

独自コード・形状・文書は[MIT](../LICENSE)、[第三者表記](../THIRD_PARTY_NOTICES.md)とLICENSESを継承します。既存の参照画像なしAI生成テクスチャと来歴をassets/PROVENANCE.mdに収録。保有する権利の範囲で提供し、第三者の権利不存在や独占的権利を保証しません。BIOS・エミュレータ・FPGAビットストリーム・ツール・フォントファイルは配布しません。

現状有姿・無保証の開発仕様向けサンプルです。実機動作、安全性、速度、将来仕様との互換性を保証せず、各開発者による承認や性能保証を意味しません。利用・改変は利用者の判断と責任で行ってください。適用法で認められる範囲で、作者・貢献者は利用に伴う損害の責任を負いません。

## English

Separate Geo3D v2.0-only automatic dual-view demos: 2 robots / 1 MiB and 5 robots / 2 MiB, ASCII16, TurboR/R800. C switches cameras; T toggles textures. Static face residency reduces transfers without changing the compared pixels. Tested only in the author's openMSX commit above. BlueMSX+ v2, physical hardware and this version on Z80 remain unverified. Emulator geometry processing is not cycle-timed; the measured gains do not predict hardware performance. Silent original-speed media; MIT and retained upstream notices; provided as is without warranty. Previous editions remain available.

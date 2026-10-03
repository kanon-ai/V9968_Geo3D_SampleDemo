# FOUR SEASONS — ポリゴン・テクスチャの基本デモ

黒背景で **桜 → 蛍 → 紅葉 → 雪** と遷移する、TurboR + V9968 + Geo3D用の無音・自動デモです。ポリゴンの輪郭、表裏、テクスチャ、回転、奥行き順描画を試す基本サンプルとして公開します。ゲームや物理シミュレーションではありません。

[ROM・GIF・無音MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/four-seasons-v0.1.0)

![Four seasons](media/four-seasons.gif)

## 実行方法

ROMは **1 MiB / ASCII16**。Geo3D開発者の[openMSX fork](https://github.com/alexmoncks/openMSX)で、V9968対応TurboR機種とGeo3D拡張を選びます。標準openMSXのみでは動作条件を満たしません。必要な機種ROMは利用者が正当に用意してください。

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart FOUR-SEASONS.ROM -romtype ASCII16
```

操作不要でループします。音楽・効果音なし。マッパーは自動判定に任せずASCII16を指定してください。

## 基本技術

- 16色テクスチャとポリゴン輪郭で花びら・葉・光・結晶を表現。桜の濃淡、もみじの葉脈、蛍の明るい中心、雪の色はPythonで手続き生成しています。画像生成AIや外部写真は使っていません。
- 7つの奥行き層を遠方から順に描き、表裏の三角形で薄い葉を表現します。完全なZバッファではなく、同一層内の交差をすべて解決するものではありません。
- 春126枚、夏336灯、秋42枚、冬126個を配置。最大投入面数は裏面を含め1,596三角形です。常に全オブジェクト・全三角形が見えるという意味ではありません。
- 各季節6種類の揺れメッシュと1,536組の姿勢レコードを事前計算。再生時はレコードを4つずつ進めます。個別の風・流体・物理演算ではなく、複数の層を動かす演出です。
- Geo3Dで投影・ポリゴン描画、V9968でテクスチャと画面更新を行います。録画済み動画をROMから再生する方式ではありません。
- 層ごとに季節をずらして切り替えます。黒背景は今後の背景表現を検討するための基本構成です。

## 検証（2026-10-03）

専用Geo3D openMSXで四季一周と代表フレームを確認。検証用openMSXソースは `de29fb854885a38251c03e24596ad4ff95770ef2`。384更新にエミュレーション時間約36.94秒、平均約10.40更新/秒でした。GIFと無音MP4は約36.95秒。速度変更・フレーム補間はしていません。

**本デモのBlueMSX+検証、実機・FPGA検証は未実施です。** この測定値は使用エミュレータの結果であり、実機性能・描画上限を示しません。公開ソースから再ビルドし、検証済みROMとSHA-256の一致を確認しています。

[描画・速度記録](validation/four-seasons-checks.json) · [キャプチャログ](validation/four-seasons-capture.txt) · [メディア情報](validation/four-seasons-media.json)

## ビルド

Python 3、NumPy、Pillow、SDCCのsdasz80 / sdldz80が必要です。SDCCのbinをPATHまたはSDCC_BINに設定し、PETAL_GROUPSは未設定（既定7）で実行してください。

```text
python -m pip install -r demos/four-seasons/requirements.txt
python demos/four-seasons/build.py
```

出力 `demos/four-seasons/out/PETAL-STORM.ROM` が配布物の `FOUR-SEASONS.ROM` と同一です。
SHA-256: `db0e1457a5f6f5076b8a6bbd3e4338857c1aacb73a50bdbfc1b438f88b999f8d`

## ライセンス・来歴・免責

独自コード・形状・手続き生成テクスチャ・文書は[MIT License](../LICENSE)。既存ORBITALの転送・初期化コードとメッシュ補助コードを再利用しています。Geo3DのAlex Moncks氏、V9968のHRA!氏のMIT表記を[第三者表記](../THIRD_PARTY_NOTICES.md)とLICENSESに保持しています。商用ゲームの画像・モデル・音楽は含みません。動画字幕は描画済みで、フォントファイルは配布しません。

BIOS、エミュレータ、FPGAビットストリーム、ツール本体、個人設定は同梱しません。本配布物は技術実験用で、現状有姿・無保証です。動作、安全性、速度、互換性や将来の仕様対応を保証しません。利用・改変は利用者の判断と責任で行ってください。適用法令で認められる範囲で、作者・貢献者は利用または利用不能から生じる損害について責任を負いません。各ハード・エミュレータ開発者による公式承認や性能保証を意味しません。詳細はMIT Licenseの免責条項に従います。

## English

A silent automatic polygon-and-texture basics demo: cherry petals, fireflies, maple leaves and snow on black. TurboR + V9968 + Geo3D, 1 MiB ASCII16. Geometry and movement tables are precomputed; polygon rendering runs in real time. Procedurally generated textures, no external artwork. Tested in developer Geo3D openMSX only; BlueMSX+ and physical hardware are unverified for this demo. Media is not sped up. MIT with upstream notices retained, provided as is without warranty.

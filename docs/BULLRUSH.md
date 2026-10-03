# GR-9 BULLRUSH — 256-color city pursuit demo

TurboR + V9968 + Geo3Dで、市街地をローラーダッシュするロボットを描く無音・自動走行デモです。探索から青い機体の発見、追跡、急旋回、屋上へのショートカットへ進みます。膝・腕・胴体の姿勢、旋回時の体重移動を見せる実験です。

**操作可能なゲームではありません。** 移動・カメラ・ポーズは事前計算したデータです。ポリゴンの投影・描画はGeo3Dで実行し、ROMに収録した動画を再生しているものではありません。追跡AI、自由操作、格闘、被害スコア、時間制限、ヘリによる回収は未実装です。

![BULLRUSH](media/bullrush.gif)

## ダウンロード・起動

[BULLRUSH v0.1.0 リリース](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/bullrush-v0.1.0)からROM、無音MP4、GIFを取得できます。ROMは1 MiB / ASCII16です。

Geo3D開発者の[openMSX fork](https://github.com/alexmoncks/openMSX)で、TurboRのV9968機種とGeo3D拡張を選びます。今回の検証用ソースは `de29fb854885a38251c03e24596ad4ff95770ef2`。標準openMSXだけでは必要な拡張を備えていません。

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart BULLRUSH.ROM -romtype ASCII16
```

必要な機種ROMは利用者が正当に用意してください。自動再生・ループです。**TキーでテクスチャON/OFF**。ヘッダーは両状態で共通です。終了はエミュレータの通常操作で行います。BGM・効果音はありません。

## 技術概要

- SCREEN 8相当の256×212・8bit画素、V9968 EPALのRGB555パレット256エントリー。背景と建物にテクスチャを使い、ロボット装甲はフラットシェーディングです。
- 576組の経路・姿勢レコードをROMに保存。ビル街の幾何形状、2機の関節ポーズと車輪をGeo3Dへ転送します。関節の姿勢計算はビルド時に実施します。
- 8×4の市街地タイル。冒頭は敵を離して配置し、約3.5秒の探索演出を経て追跡へ入ります。市街地内の敵経路は演出用に作成したものです。
- 建物の裏へ飛び降りる敵を隠すため、対象となる手前の壁・屋根を敵の描画後に再描画します。90組のレコードで使用。完全なZバッファではなく、任意の交差形状や自由移動に対応する汎用遮蔽処理ではありません。
- V9968で背景・HUD・画面切り替えを扱い、Geo3Dでポリゴンを描画します。将来のゲーム化を想定した試作ですが、現段階では自動演出です。

## 検証（2026-10-03）

専用Geo3D openMSXで一周の等速キャプチャ、探索開始と屋上からの降下の表示、Tキー切り替えを確認。公開ソースからの再ビルドと配布ROMのSHA-256一致も確認済みです。元の16色版の形状・自機ポーズの比較検証を実施しています。

最新映像は約30.27秒、記録区間の描画更新は平均約12.49fps。MP4/GIFは無音で、動画の速度変更や補間による高速化は行っていません。**これはエミュレータ上の測定であり、実機・FPGA・カートリッジの処理性能を証明するものではありません。BlueMSX Geo3Dでの本デモ検証も未実施です。**

[検証ログ](validation/bullrush-capture.txt)・[比較検証](validation/bullrush-mode.json)・[メディア情報](validation/bullrush-media.json)

## ソースからビルド

Python 3、NumPy、Pillow、SDCCの `sdasz80` / `sdldz80` が必要です。SDCCのbinをPATHに追加するか、環境変数 `SDCC_BIN` に指定してください。

```text
python -m pip install -r demos/bullrush/requirements.txt
python demos/bullrush/build.py
```

出力は `demos/bullrush/out/BULLRUSH.ROM`。ツールの版によって再現性が変わる可能性があります。生成される `src/palette.inc` と `out` はビルド成果物です。

## ライセンス・来歴・免責

独自のPython/Z80コード、形状、HUD、文書はリポジトリの[MIT License](../LICENSE)で提供します。Geo3Dの初期化・コマンド転送例の来歴に対してAlex Moncks氏のMIT表記、V9968についてHRA!氏のMIT表記を[第三者表記](../THIRD_PARTY_NOTICES.md)に保持しています。

テクスチャは参照画像なしのAI生成で、生成元とプロンプトを[同梱](../demos/bullrush/assets/PROVENANCE.md)しています。ロボット形状はソースで構築したオリジナルです。商用ゲームの画像・モデル・音楽は含みません。AI生成素材は保有する権利の範囲でMIT提供し、独占的権利や第三者の権利不存在を保証しません。

エミュレータ、BIOS、FPGA RTL/ビットストリーム、ツール本体、フォントファイル、個人設定は配布しません。映像字幕はローカルフォントで描画済みです。

本デモは現状有姿・無保証です。利用・改変に伴う不具合や損害についてMITの免責条項が適用されます。ハードやエミュレータの仕様変更で動作しなくなる場合があります。作者名・ハード名は帰属と識別のためで、公式承認や性能保証を意味しません。ライセンス確認は配布ファイルの来歴・表記の確認であり、法的な権利保証ではありません。

## English summary

A silent, automatic 1 MiB ASCII16 robot city-pursuit experiment for TurboR + V9968 + Geo3D. T toggles textures. Polygon rendering is real time; movement, camera and joint poses are precomputed. This is not an interactive game. Validated only in the developer Geo3D openMSX environment, not physical hardware or BlueMSX. Original code/assets are offered under MIT to the extent rights are held, with upstream notices retained. No emulator, BIOS, firmware or proprietary game assets are included. Provided as is, without warranty.

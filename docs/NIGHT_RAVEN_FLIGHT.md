# NIGHT RAVEN — Flight Development Demo

**あくまでデモです。空間を飛行する感覚を少しだけ楽しめる、操作可能な開発体験版です。完成ゲーム・最終版ではありません。** 内容、操作、敵の挙動、バランス、演出は今後変更する可能性があります。

**効果音は仮のPSG音です。最終版の音ではなく、操作・演出を確認するための暫定音です。BGMは未収録です。**

An interactive development demo: a short taste of flying through space. **This is not a finished game or final release. The PSG sound effects are temporary placeholders, not the final sound design. No BGM is included.**

![Flight development demo](media/night-raven-flight.gif)

## Download / 起動

[v0.4.0 開発体験版・ROM・動画](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.4.0)

従来の自動再生・無音NIGHT RAVENとは別版です。既存デモを置き換えません。

```powershell
& 'C:/path/to/geo3d-openmsx/openmsx.exe' -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart './NIGHT_RAVEN_FLIGHT_DEMO.ROM' -romtype ASCII16
```

1MiB / ASCII16。TurboR + V9968 + Geo3Dの開発者版openMSXが必要です。通常のopenMSXやGeo3D非対応VDPでは確認していません。BIOS・エミュレータは同梱しません。

|操作|キーボード|ジョイスティック1|
|---|---|---|
|操舵|方向キー|方向入力|
|射撃・開始・再挑戦|Space|第1ボタン|
|捕捉後の誘導ミサイル|X|第2ボタン|
|一時停止／再開|Esc|—|
|区間の最初へ|F1|—|

常時表示の中央サイトはありません。短いバルカン弾と敵の捕捉・ロック枠を目安に操舵してください。黒烏のバンク・ピッチは段階的に補間します。短い迎撃区間と最終防衛目標、再挑戦を含みますが、いずれも操作確認用の仮構成です。

## Build / 技術

Python 3、numpy、Pillow、SDCCのsdasz80/sdldz80を使用します。

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN='C:/path/to/sdcc/bin'
python demos/night-raven-flight/build.py
```

出力は `demos/night-raven-flight/out/NIGHT_RAVEN_FLIGHT_DEMO.ROM`。敵・射撃・HP・当たり判定・誘導弾・シールド・終了状態は実行時処理です。Geo3Dがポリゴンを変換・投影・描画し、V9968がVRAM描画を担当します。背景・壁のカメラ経路はテーブル方式です。通常弾の判定は射線判定で、短い飛翔弾はその視覚表現です。全面的な自由飛行・物理シミュレーションではありません。

画面内の効果はV9968のLINE等、背景変形はLRMMを使用。効果音は既存デモのPSG方式を実行時イベントへ接続し、ポーズ・再開始時に音を停止します。

## Verification / 検証

2026-09-30、Geo3D開発者 Alex Moncks氏のopenMSX commit `de29fb854885a38251c03e24596ad4ff95770ef2` で確認しています。**実機・FPGAは未検証。エミュレータ速度は実機性能の保証ではありません。**

キー入力のみの自動操作で区間完了、画面端、一時停止・再開、再開始、被撃墜と再挑戦を確認。物理ジョイスティックは未検証です。動画は同じ自動テストによるエミュレータ収録です。GIFは無音の抜粋、MP4には仮効果音を収録しています。

検証記録は `docs/validation/night-raven-flight-*`。自動検証はGEO3D_RUNTIMEに専用エミュレータのフォルダーを設定し、同デモのplaytest.py / edge-test.pyを実行します。BIOS検索先は利用者の環境に合わせてください。

## License / 免責

独自ソース・手続き生成素材・仮効果音は、権利を有する範囲で [MIT](../LICENSE)。[上流ライセンスと第三者通知](../THIRD_PARTY_NOTICES.md) を保持します。市販ゲームの画像・モデル・音楽や、参考画像そのものは使用していません。

試作・現状有姿・無保証です。動作、実機互換性、速度、保守、将来の完成や公開を保証しません。非公式の応援・開発デモであり、ハードウェア作者による品質認証ではありません。免責の適用は法令の認める範囲に限ります。

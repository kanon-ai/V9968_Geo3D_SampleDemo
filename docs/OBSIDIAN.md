# OBSIDIAN / TITAN PASS

**2026-10-03 Z80 update / Z80最適化版:** [ROM](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/z80-optimization-v0.1.0) · [測定・検証範囲 / Measurements and verification scope](Z80_OPTIMIZATION.md). Existing previews and earlier validation below describe previous releases. 以下の既存映像・過去検証は旧版の記録です。

最初の巨大戦艦への接近飛行デモです。TurboR + V9968 + Geo3Dによるリアルタイム・ポリゴン描画を観察する、自動再生の技術実験です。操作はできません。ROMに動画を収録しているものではありません。

**効果音・BGMはありません。カッコいいBGMを付けたいのですが、まだ決まらず悩み中です。今後BGMを追加する予定です。それまでは、それぞれの「心のBGM」を重ねてお楽しみください。** 追加時期は未定です。

A silent, automatic battleship flyby, rendered in real time. No SFX or music. BGM is planned for a future update; until then, enjoy it with the soundtrack in your imagination!

![OBSIDIAN](media/obsidian.gif)

## 起動 / Run

[v0.2.0 ROM and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.2.0)

まずはGeo3D開発者 Alex Moncks氏の [openMSX](https://github.com/alexmoncks/openMSX)、commit `de29fb854885a38251c03e24596ad4ff95770ef2` で確認しました。通常版openMSXではなくGeo3D拡張を備える版と、対応するマシン定義が必要です。

```powershell
& 'C:/path/to/geo3d-openmsx/openmsx.exe' -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart './OBSIDIAN_GEO3D.ROM' -romtype ASCII16
```

ROMは **256KiB / ASCII16**。自動起動・ループ再生します。内部VDPポート98h系、Geo3Dポート9Dh/9Fhを使用します。外部88h構成は未検証です。BIOSは適法に入手したものを使用してください。エミュレータ・BIOS・FPGAビットストリームは同梱しません。

## ビルド / Build

Python、numpy、Pillow、SDCCのsdasz80/sdldz80を用意します。

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN='C:/path/to/sdcc/bin'
$env:ROM_FONT='C:/Windows/Fonts/consola.ttf'
python demos/obsidian/build.py
```

出力: `demos/obsidian/out/OBSIDIAN_GEO3D.ROM`。ROM_FONTは使用権のあるTrueTypeフォントに変更できます（字体・ビルドハッシュは変わります）。フォントファイルは配布していません。

収録する場合はGEO3D_RUNTIMEを対応openMSXのフォルダーに設定し、capture.pyを実行します。必要なBIOSの検索場所は利用者の環境で設定してください。encode.pyにはFFMPEG（実行ファイルのフルパス）、CAPTION_FONT（使用権のあるフォント）も必要です。

## 技術 / Technical notes

- 184個の立体部品、護衛機8機、自機1機を構成。1フレームに1,816頂点・1,302面を9回のRUNバッチに分けて投入します。全ての面が常に可視になるわけではありません。
- モデル用データ24,968バイト。各バッチの上限に収まるよう船体を分割します。
- 経路・カメラのテーブルをビルド時に生成し、実行時にCPUがGeo3Dへ描画を指示します。Geo3Dが変換・投影・陰影・面描画を担当し、V9968 VRAMに描画します。テクスチャマッピングは使用していません。
- 512フレームで一周。遠近・遮蔽・船体の厚みを観察する実験であり、完成したゲームや汎用ベンチマークではありません。

## 検証 / Validation

2026-09-29に公開用ソースから再ビルドし、上記開発者版openMSXで一周を収録しました。512フレーム / 約34.179秒（約14.98描画fps）。MP4は30fpsコンテナーで、描画回数とは異なります。再生の早回しはしていません。GIFは16秒の抜粋で15MB未満です。

録画元のPCM 1,506,978サンプルは全て0でした。MP4も音声トラックなしです。結果は [manifest](validation/obsidian-manifest.json)、[capture log](validation/obsidian-record-log.txt)、[silence](validation/obsidian-silence-validation.json)、[media hashes](validation/obsidian-media.json) を参照してください。

**実機・FPGAは未検証です。エミュレータのGeo3D処理速度は実機性能の証明ではありません。** 他のエミュレータでの動作も保証しません。

## ライセンス・免責

ソースと独自の手続き生成モデルを権利のある範囲で [MIT](../LICENSE) として提供します。[第三者の権利・上流通知](../THIRD_PARTY_NOTICES.md) を参照してください。市販ゲームの画像・モデル・音楽は含みません。

試作・評価用、現状有姿・無保証です。ハードウェア開発者による認証を意味しません。動作・速度・保守・修正を保証せず、適用法で認められる範囲で責任を制限します。Experimental, AS IS, without warranty; see the license for full terms.

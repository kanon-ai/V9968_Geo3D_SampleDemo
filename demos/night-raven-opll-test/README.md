# NIGHT RAVEN — OPLL BGM test v0.1.0

黒烏の1ステージ自動デモに約30秒のOPLL BGMを追加したテスト版です。
**TurboR + V9968 + Geo3D + MSX-MUSIC向け、1 MiB / ASCII16。操作不要。**
v0.3.2の無音デモを基にした独立版です。別公開のFLIGHT版・3ステージ版の更新ではありません。

[ROM / 音声付きMP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-opll-test-v0.1.0)

## 楽曲 / Music
Suno（Premium）で作曲し、MSXミュージックエディタのMCP機能を使ってCodexがOPLL向けに編曲。
提供者の許可を受け、本デモに組み込んで公開しています。効果音はありません。
楽曲データはコードのMITライセンスとは別扱いです。楽曲単体の再利用権をこの文書で付与するものではありません。

Music created with Suno (Premium), then arranged for OPLL by Codex using the MSX Music Editor MCP interface. Published in this demo with the contributor's authorization. Music is separate from the MIT-licensed code; no standalone music reuse license is granted here.

## 実行 / Run
Geo3D対応の開発者版openMSX、またはBlueMSX+ Geo3D experimentalでTurboRとMSX-MUSICを選び、ROMをASCII16として起動してください。通常版エミュレータにはGeo3Dがない場合があります。
本版のBGMはTurboRのE6h/E7hタイマーに依存します。通常のMSX2/MSX2+はBGM対象外で、非TurboRのBIOS機種判定なら音楽を開始しません。OPLL未搭載時の代替音源はありません。
検証対象はR800です。TurboRのZ80モードと通常のMSX2+は同じ条件ではありません。

## 実装 / Implementation
OPLLレジスター列を毎秒約60回、描画待ち中のポーリングで再生。描画フレーム数に曲の進行を結び付けません。
1805音楽フレーム、11391 bytesをROM bank 63からRAM 8000hへコピーします。
ループ終了時のキーオフと先頭初期化は同一音楽フレーム。元データのOPLL書き込み順を維持。
アドレス書き込み後はタイマー3 ticks、データ書き込み後は8 ticks待機し、R800でも待ち時間を確保。
MP4はエミュレータ映像と音声の同時収録で、後付けBGMや速度変更ではありません。

## 検証 / Validation (2026-10-11)
- 専用openMSX / Panasonic FS-A1ST V9968 + Geo3D / R800：9794回のOPLL書き込みが元データと一致（2周以上）。約30.096秒で音楽ループ。
- 無音版との表示VRAM比較は一周512画面すべて一致。
- 最初から最後の描画完了まで24.749秒→25.383秒（約2.6%増）。起動時間を含まず、実機性能ではありません。
- BlueMSX+ v3.1.1 Geo3D experimental (2090cd2)：約38秒のRAM観測で映像一周以上と音楽ポインターのループを確認。音声波形比較は未実施。OPLL書き込み列・全画面一致の照合はopenMSX側のみです。
- 本BGM版の実機検証は未実施。過去の無音版の実機報告とは区別してください。無保証の実験版です。

[Validation data](../../docs/validation/night-raven-opll-test-v0.1.0.json)

## Build
Python 3、NumPy、Pillow、SDCCのsdasz80/sdldz80を使用します。SDCC_BINをbinディレクトリに設定して python build.py を実行してください。
music.binは各フレームのuint8書き込み数とregister/valueペアからなり、1805フレームをループします。
BIOS・エミュレータ・ツールチェーンは同梱しません。

# SEASON GLOBE
MSX turbo R、外部V9968（88h）とGeo3D V2向けの、四季のスノードームです。雪の山小屋、桜の京都、蛍の光が漂う池、紅葉の滝を表現しました。BGMには「Distant Music Box」をMSX-MUSIC（OPLL）用に変換して収録しました。

![四季のスノードーム（無音プレビュー）](SEASON-GLOBE.gif)

## 操作

| キー | 動作 |
| --- | --- |
| SPACE | ドームを左右に軽く揺らします。舞い上がった粒子はゆっくり沈みます。 |
| → / ← | 次の季節 / 前の季節に切り替えます。 |

操作せずに眺めていると約70秒で次の季節に移ります。底のランプによる弱い対流は常に続きます。ガラスの中の景色を楽しめるよう、画面内の操作説明は省いています。

## BlueMSX+で起動

1. [BlueMSX+ v3.2.0-alpha](https://github.com/Hesoten/blueMSX-plus/releases/tag/v3.2.0-alpha) のx64版と、利用権のあるFS-A1ST用システムROMを準備します。
2. 機種を **MSXturboR - Panasonic FS-A1ST** に設定します。
3. スロット1に **SEASON-GLOBE-88H.ROM** を **ASCII16** 指定で挿入し、スロット2に **V9968Cartridge** を設定して起動します。初回表示まで画像の読み込みがあります。

WindowsでROMをエミュレータのフォルダーに置いた場合の起動例です。

```bat
"blueMSX+.exe" /machine "MSXturboR - Panasonic FS-A1ST" /rom1 "SEASON-GLOBE-88H.ROM" /romtype1 ASCII16 /special2 V9968Cartridge
```

2026-11-24に公式x64配布版（62368a3）で起動、四季の描画、キー操作と音声出力を確認しました。実機では未検証です。ROMは4 MiBです。GIFは無音で、BGMはROMを起動すると再生されます。

## License and disclaimer / 利用条件・免責

[LICENSE.txt](LICENSE.txt) をご覧ください。

## English controls

Press **Space** to shake the globe. Press **Right / Left** for the next / previous season. Leave it running to cycle automatically. Use the 4 MiB ASCII16 ROM with the FS-A1ST profile and external V9968Cartridge in BlueMSX+.

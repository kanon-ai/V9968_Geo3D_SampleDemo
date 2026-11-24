# SEASON GLOBE
MSX turbo R、内蔵V9968（98h）または外付けV9968（88h）とGeo3D V2向けの、四季のスノードームです。雪の山小屋、桜の京都、蛍の光が漂う池、紅葉の滝を表現しました。BGMには「Distant Music Box」をMSX-MUSIC（OPLL）用に変換して収録しました。

![四季のスノードーム（無音プレビュー）](SEASON-GLOBE.gif)

## 操作

| キー | 動作 |
| --- | --- |
| SPACE | ドームを左右に軽く揺らします。舞い上がった粒子はゆっくり沈みます。 |
| → / ← | 次の季節 / 前の季節に切り替えます。 |

操作せずに眺めていると約70秒で次の季節に移ります。底のランプによる弱い対流は常に続きます。ガラスの中の景色を楽しめるよう、画面内の操作説明は省いています。

## BlueMSX+で起動

1. [BlueMSX+ v3.2.0-alpha](https://github.com/Hesoten/blueMSX-plus/releases/tag/v3.2.0-alpha) のx64版と、利用権のあるFS-A1ST用システムROMを準備します。
2. 接続方式に合わせて次のどちらかを選びます。どちらもスロット1に4 MiBのROMを **ASCII16** 指定で挿入します。初回表示まで画像の読み込みがあります。

| 接続方式 | ROM | BlueMSX+ の構成 |
| --- | --- | --- |
| 外付け88h | [SEASON-GLOBE-88H.ROM](SEASON-GLOBE-88H.ROM) | FS-A1STの標準機種設定。スロット2に V9968Cartridge を挿入。 |
| 内蔵98h | [SEASON-GLOBE-98H.ROM](SEASON-GLOBE-98H.ROM) | FS-A1STの機種設定を複製し、主VDPをV9968に変更。スロット2は空。 |

内蔵版を検証時と同じ設定で起動するには、`Machines/MSXturboR - Panasonic FS-A1ST` を `Machines/MSXturboR - Panasonic FS-A1ST V9968 INTERNAL` にコピーし、コピー側の `config.ini` の `[Video]` を `version=V9968`、`vram size=256kB` に設定します。

WindowsでROMをエミュレータのフォルダーに置いた場合の起動例です。

```bat
"blueMSX+.exe" /machine "MSXturboR - Panasonic FS-A1ST" /rom1 "SEASON-GLOBE-88H.ROM" /romtype1 ASCII16 /special2 V9968Cartridge
"blueMSX+.exe" /machine "MSXturboR - Panasonic FS-A1ST V9968 INTERNAL" /rom1 "SEASON-GLOBE-98H.ROM" /romtype1 ASCII16
```

2026-11-24に公式x64配布版（62368a3）で両構成の起動、四季の描画、キー操作と音声出力を確認しました。実機では未検証です。ROMは4 MiBです。GIFは無音で、BGMはROMを起動すると再生されます。

## License and disclaimer / 利用条件・免責

[LICENSE.txt](LICENSE.txt) をご覧ください。

## English controls

Press **Space** to shake the globe. Press **Right / Left** for the next / previous season. Leave it running to cycle automatically. Both ROMs use ASCII16. Choose 88H for an external V9968Cartridge or 98H for an FS-A1ST profile configured with V9968 as the main VDP.

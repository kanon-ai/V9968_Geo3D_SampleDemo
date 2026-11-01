# SKYBOUND / JAPAN ODYSSEY — Flight Demo Ver2.1

An automatic, silent V9968 + Geo3D V2 sightseeing flight in 256 colors. Depart Hokkaido, travel south past snow scenery, island coasts, Tokyo towers, Mount Fuji, Nagoya Castle, Kyoto Tower, Osaka landmarks, inland-sea bridges and islands, Kyushu volcanoes and Okinawa. Land in Okinawa, pause for 96 animation frames, then cut back to the Hokkaido departure and repeat. Geography and landmarks are intentionally stylized; this is not a geographic or flight-training simulator.

- ROM: **4 MiB / ASCII16**, Geo3D V2 required.
- `INTERNAL-98H`: main VDP. `EXTERNAL-88H`: external second VDP; select its video output.
- Automatic playback; no user flight controls or sound.
- Real-time Geo3D rendering with precomputed transforms. Near-plane-crossing geometry is clipped during data generation; it is not a video stored in ROM.
- Checked with Geo3D developer openMSX / TurboR. Hardware, BlueMSX+ V2 and Z80 performance are not verified for this edition.
- Existing published Flight Demo Ver2.0 is preserved separately.

## 日本語

北海道離陸から沖縄着陸までの日本縦断版 Ver2.1です。帰路は設けず、南下しながら各地の景色を巡ります。沖縄で着陸・停止し、96フレームの間を置いて北海道の離陸へ切り替わります。画面は256色、ROMは各4 MiB、マッパーはASCII16。Geo3D V2必須です。

内蔵98h版と外付け88h版を用意しています。外付け版ではV9968側の映像をご覧ください。無音・自動再生で、操作は未実装です。Geo3D作者版openMSX／TurboRで確認し、実機・BlueMSX+ V2・Z80性能は未検証です。既存の公開版は別途保存しています。

## License / 免責

See LICENSE, THIRD_PARTY_NOTICES.md and LICENSES. AI-generated texture provenance is recorded in assets/GENERATION.md. MIT applies to project code and assets to the extent rights can be granted; upstream notices remain applicable. No emulator, BIOS or FPGA bitstream is bundled. Provided as-is, without warranty. This is an experimental visual demonstration, not an actual navigation or aviation training system.

ライセンスと第三者への帰属は同梱文書をご覧ください。無保証の実験デモで、実際の航法や航空訓練に使用するものではありません。BIOS・エミュレータ・FPGAビットストリームは同梱しません。

## Download / ダウンロード

[ROMs, source, MP4 and GIF](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/skybound-flight-v2.1.0)

Developer openMSX / TurboR: approximately 176.7 seconds per cycle, averaging 24.6 rendered frames/s. Complete internal-ROM cycle and restart captured; six external-ROM frames matched exactly. See [VALIDATION.json](VALIDATION.json). Silent media, without speed-up or interpolation. GIF: 11.7 MB. Real hardware, BlueMSX+ V2 and Z80 performance remain unverified.

作者版openMSX／TurboRで一周約176.7秒、平均約24.6fps。内蔵版は全行程と再離陸を確認、外付け版は6箇所の比較画像が一致。動画は無音・早送り／補間なし、GIFは11.7MBです。実機・BlueMSX+ V2・Z80性能は未検証です。

## Build / ビルド

Install Python 3, NumPy, Pillow and the SDCC Z80 assembler/linker. In PowerShell:

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN = 'C:/path/to/sdcc/bin'
python build_all.py
```

Final V2 ROMs are in `out/rom/`; the base ROM is intermediate. The tested developer openMSX configuration uses:

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart SKYBOUND-JAPAN-V2-INTERNAL-98H.ROM -romtype ASCII16
openmsx -machine Panasonic_FS-A1ST -ext HRA_V9968 -ext geo3d88 -cart SKYBOUND-JAPAN-V2-EXTERNAL-88H.ROM -romtype ASCII16
```

For external output, select `set videosource V9968` in the console after boot. These configurations are not included in every openMSX distribution. No BIOS or emulator is bundled.

## Changes from Ver2.0 / 変更点

The Tokyo–Kyoto return trip becomes a one-way Hokkaido–Okinawa tour, adding snow scenery, coastal islands, inland-sea bridges and volcanoes. Landing, braking, a 96-frame pause and restart replace the airborne return loop. Near-plane-crossing faces are clipped throughout the route with UV interpolation; volcanic textures are continuous. The cockpit and dual-I/O design are retained. Flight Demo Ver2.1 requires the Geo3D **V2** interface: these version numbers describe different components.

東京～京都の往復から、北海道離陸・沖縄着陸の片道観光へ変更。景観、着陸・減速・96フレーム停止・再離陸を追加し、地面の欠け対策を全経路に適用しました。V2.0は引き続き利用できます。

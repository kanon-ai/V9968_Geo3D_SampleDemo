# SKYBOUND — Flight Demo Ver2.0 / Japan Tour

A silent, automatic sightseeing flight in 256 colors, rendered in real time by **V9968 + Geo3D V2**. Take off from a fictional Tokyo airfield, pass Tokyo Skytree and Tokyo Tower, admire Mount Fuji, Nagoya Castle and Osaka's Tsutenkaku, turn at Kyoto Tower and fly back toward Tokyo. After the first takeoff, the sightseeing route repeats continuously.

This is a separate edition of SKYBOUND. Earlier releases remain available. **Flight Demo Ver2.0 is the demo version; Geo3D V2 is the required hardware interface.**

## Download and run

[Release: ROMs, silent MP4 and GIF](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/skybound-flight-v2.0.0)

Both ROMs are **4 MiB, ASCII16 mapper**:

| ROM suffix | Connection |
|---|---|
| `INTERNAL-98H` | V9968 as the main VDP, ports 98h–9Ch |
| `EXTERNAL-88H` | External V9968 as a second VDP, ports 88h–8Ch; use its video output |

Use a Geo3D V2-capable emulator/configuration. On the tested developer openMSX installation:

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart SKYBOUND-JAPAN-V2-INTERNAL-98H.ROM -romtype ASCII16
openmsx -machine Panasonic_FS-A1ST -ext HRA_V9968 -ext geo3d88 -cart SKYBOUND-JAPAN-V2-EXTERNAL-88H.ROM -romtype ASCII16
```

For the external configuration, select the V9968 video source (console: `set videosource V9968`). Configuration names refer to that developer installation, not every openMSX distribution. This demo plays automatically; flight controls and sound are not implemented.

## Validation and performance

Verified on the Geo3D developer's openMSX, with a TurboR/R800 configuration. The internal edition was captured through takeoff, the entire route and the loop transition. Six sampled frames of the external edition matched exactly. A separate source rebuild reproduced both ROMs byte for byte. See [VALIDATION.json](VALIDATION.json) for hashes, timing and exact scope.

**Real hardware, BlueMSX+ Geo3D V2 and Z80 performance have not been verified for this edition.** Emulator timing is not a hardware speed guarantee. Videos preserve emulated time: no playback acceleration or interpolated frames.

## Rendering

Geo3D V2 resident geometry, VFIRST/FFIRST and extended indices reduce repeated model transfers. Five terrain chunks surround the route; the cockpit instruments show attitude, speed, altitude and heading. The heading needle follows the aircraft direction. Model transforms and the automatic flight are precomputed; polygons and texture mapping are rendered by Geo3D at runtime. This is not a prerecorded video in ROM.

Airport and nearby mountain faces that cross the camera's near plane are clipped during data generation, with UV interpolation. Small dynamic meshes share model slots. The return route keeps a greater distance from the mountains. The terrain, landmarks, sky and cockpit use generated textures. Building roofs have separate roof materials; Nagoya Castle has two gold roof ornaments. Geography and scale are deliberately simplified.

## Build

Python 3, NumPy, Pillow, and the SDCC Z80 assembler/linker are required. On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN = 'C:/path/to/sdcc/bin'
python build_all.py
```

Final ROMs are written to `out/rom/`. Distribute those V2 editions, not the intermediate base ROM. No emulator or BIOS is included.

## License and disclaimer

See [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [LICENSES](LICENSES) and [asset provenance](assets/GENERATION.md). Project code is provided under MIT; applicable upstream notices are retained. Generated artwork is provided under these terms to the extent rights can be granted; no exclusive copyright in AI output is asserted. Third-party emulators, BIOS files and hardware designs have their own licenses and are not bundled.

Provided as-is, without warranty. This is an experimental visual demonstration, not an accurate geographic model or a flight-training/navigation system. Compatibility and performance depend on the emulator, FPGA revision and host configuration.

---

## 日本語

**SKYBOUND フライトデモ Ver2.0** は、V9968＋Geo3D V2を使った256色・無音の自動遊覧飛行です。最初だけ東京の架空飛行場から離陸し、スカイツリー、東京タワー、富士山、名古屋城、通天閣を経由。京都タワーで旋回して東京方面へ戻り、以降は遊覧ルートを繰り返します。従来版を残した別バージョンです。

ROMは各 **4 MiB／ASCII16**。内蔵VDP用は `INTERNAL-98H`、外付け第2VDP用は `EXTERNAL-88H` を選んでください。外付け版はV9968側の映像出力を使用します。Geo3D V2必須で、自動再生のみ、操縦と音声は未実装です。

Geo3D開発者版openMSXのTurboR/R800構成で離陸から一周・ループまで確認しました。外付け版は6箇所の比較画像が内蔵版と一致し、公開ソースからの再ビルドも両ROMと一致しています。**本版の実機・BlueMSX+ Geo3D V2・Z80での性能は未検証です。** 動画に早送り・補間は加えていません。

V2のモデル常駐とVFIRST/FFIRSTで転送を抑え、ポリゴンとテクスチャをリアルタイム描画します。飛行経路と変換データは事前計算です。離陸時の地面や山の近接面にはUV補間を伴うクリッピングを施し、帰路は山から距離を取っています。計器は姿勢・速度・高度・方位を表示します。

ライセンス・素材の由来は上記各文書をご覧ください。無保証の実験デモで、実際の航空訓練・航法用途には使えません。BIOSやエミュレータは同梱しません。互換性や速度は使用環境に依存します。

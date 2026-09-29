# V9968 + Geo3D Sample Demos

**TurboR + V9968 + Geo3Dで「こんな映像も見てみたい」を試す、3本の無音・自動再生デモです。**

Three silent, non-interactive experiments: a coastal race, a low-altitude flight, and rotating Earth/Moon spheres. These are real-time polygon rendering demos, with precomputed movement/camera tables—not prerecorded raster movies in ROM.

**まずはGeo3D開発者 Alex Moncks氏のopenMSXで確認しています。実機動作・実機速度の保証ではありません。** These demos were checked with the Geo3D developer's openMSX build. Physical hardware and other emulators are not validated. See [validation details](docs/VALIDATION.md).

## ダウンロード / Download

[v0.1.1 リリース・ROMと無音MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.1.1)

ROMは各 **1MiB / ASCII16**。操作は不要です。音声はありません。エミュレータ・BIOS・FPGAビットストリームは同梱していません。

| Demo | 内容 | Preview |
|---|---|---|
| VECTOR / RUSH | 起伏とバンクのある海沿いコース、3台の車 / coastal race | [GIF](docs/media/vector-rush.gif) |
| SKYBOUND | テクスチャ付き地形、僚機2機、港湾・谷・橋 / textured low-altitude flight | [GIF](docs/media/skybound.gif) |
| ORBITAL | テクスチャ付き地球・月の自転と公転、7段階の陰影 / Earth and Moon | [GIF](docs/media/orbital.gif) |

### VECTOR / RUSH
![VECTOR / RUSH](docs/media/vector-rush.gif)

### SKYBOUND
![SKYBOUND](docs/media/skybound.gif)

### ORBITAL
![ORBITAL](docs/media/orbital.gif)

## 起動とビルド

- [使い方・必要な環境 / Usage and build](docs/USAGE.md)
- [技術説明 / Technical notes](docs/TECHNICAL.md)
- [検証した版・範囲・制約 / Validation](docs/VALIDATION.md)
- [ライセンス・素材の来歴 / Licenses and provenance](docs/LICENSE_REVIEW.md)

## クレジット / Credits

- V9968: **HRA!** — [V9968_Cartridge](https://github.com/hra1129/V9968_Cartridge)
- Geo3D: **Alex Moncks** — [Geo3D](https://github.com/alexmoncks/V9968_Cartridge/tree/main/geo3d), [Geo3D openMSX](https://github.com/alexmoncks/openMSX)
- openMSX contributors, SDCC contributors, and the authors of the build tools.
- Demo production: **Kanon**, with **ASTRA** assistance.
- SKYBOUND / ORBITAL texture images are AI-generated. 元画像と生成プロンプトを各デモの `assets/` に収録しています。

ハードウェアと周辺の創作活動を応援する非公式サンプルです。各ハードウェア開発者による認証・品質保証を意味するものではありません。

## ライセンスと免責事項 / License and disclaimer

本プロジェクトのソースコード・独自素材は、権利を有する範囲で [MIT License](LICENSE) により提供します。上流の権利・ライセンスは [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

**試作・実験用です。現状有姿、無保証で提供します。** 動作、速度、特定機器への適合性、安全性、継続的な保守、バグ修正は保証しません。使用は利用者の判断と責任で行ってください。損害に関する責任の制限は、適用法で許される範囲に限ります。ROM・BIOS等は適法に入手したものを使用してください。

Experimental software, provided **AS IS, without warranty**. Hardware compatibility, performance, maintenance and fixes are not guaranteed. Liability limitations apply only to the extent permitted by applicable law. Use lawfully obtained system ROMs. See the MIT license for its full terms.

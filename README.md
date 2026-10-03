# V9968 + Geo3D Sample Demos

## GR-9 BULLRUSH — 256色の市街地追跡デモ

探索から青い機体を発見し、ローラーダッシュ・横スライド・急旋回で市街地を追跡する無音の自動走行デモを追加しました。関節の姿勢と体重移動、屋上ショートカットを描きます。**まだ操作可能なゲームではありません。専用Geo3D openMSXで確認、実機未検証です。**

[ROM・GIF・無音MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/bullrush-v0.1.0) · [使い方・技術・検証・ライセンス・免責](docs/BULLRUSH.md)

![BULLRUSH](docs/media/bullrush.gif)


## NIGHT RAVEN — 操作できる開発体験デモ / Flight Development Demo

**完成ゲームではなく、空間を飛行する感覚を少しだけ楽しめる開発体験版です。** 従来の無音・自動再生デモとは別に追加しました。

**効果音は暫定のPSG音であり、最終版の音ではありません。BGMは未収録です。**

An interactive development demo, not a finished game. **Sound effects are temporary placeholders, not final audio.**

[ROM・動画 / v0.4.0 prerelease](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.4.0) · [操作・技術・検証・免責](docs/NIGHT_RAVEN_FLIGHT.md)

![Flight development demo](docs/media/night-raven-flight.gif)


## NIGHT RAVEN v0.3.2 — 高速版

画面外の壁の転送・描画を省略。元版と一周512画面の表示VRAMが完全一致し、開発者版openMSXで測定時間を約4.1%短縮しました。無音・1MiB / ASCII16。実機未検証です。

[高速版ROM](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.2) · [変更・検証詳細](docs/NIGHT_RAVEN.md)

以下のNIGHT RAVEN GIFはv0.2.0の映像です（画面内容は同じ、速度は旧版）。


**TurboR + V9968 + Geo3Dで「こんな映像も見てみたい」を試す、従来5本の無音・自動再生デモも収録しています。**

Five silent, non-interactive experiments, including NIGHT RAVEN space combat and OBSIDIAN battleship flyby: a coastal race, a low-altitude flight, and rotating Earth/Moon spheres. These are real-time polygon rendering demos, with precomputed movement/camera tables—not prerecorded raster movies in ROM.

**まずはGeo3D開発者 Alex Moncks氏のopenMSXで確認しています。実機動作・実機速度の保証ではありません。** These demos were checked with the Geo3D developer's openMSX build. Physical hardware and other emulators are not validated. See [validation details](docs/VALIDATION.md).

## ORBITAL — TYPE REAL / 別バージョン

地球が月の1公転につき約27.3回自転する高速回転版です。月は同じ面を地球に向けたまま公転します。**従来のORBITALも引き続き提供します。** 実時間や実機性能を示すものではありません。

[ROM・無音MP4・GIF / v0.3.1](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.1) · [使い方・技術説明・検証 / Details](demos/orbital-type-real/README.md)

![ORBITAL TYPE REAL](docs/media/orbital-type-real.gif)

## NIGHT RAVEN — 新着 / New

巨大艦の壁沿いを突破する、リアルタイム・ポリゴン宇宙戦デモを追加しました。**効果音・BGMなし版です。カッコいいBGMを付けたいのですが、まだ決まらず悩み中。今後BGMを追加する予定です。それまでは、それぞれの「心のBGM」を重ねてお楽しみください。**

NIGHT RAVEN is currently silent (no SFX or BGM). We are still looking for the right soundtrack and plan to add BGM later. Until then, enjoy it with the soundtrack in your imagination!

[無音ROM・MP4 / v0.2.0](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.2.0) · [使い方・技術説明・検証・免責 / Details](docs/NIGHT_RAVEN.md)

![NIGHT RAVEN](docs/media/night-raven.gif)

## OBSIDIAN / TITAN PASS — 最初の巨大戦艦デモ

巨大戦艦の近傍を飛行する、最初のGeo3D実験も無音版で追加しました。1フレームあたり1,816頂点・1,302面を投入します（全ての面が常に表示されるという意味ではありません）。

[使い方・技術説明・検証](docs/OBSIDIAN.md) · [v0.2.0 ROM・無音MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.2.0)

![OBSIDIAN](docs/media/obsidian.gif)

## ダウンロード / Download

[ORBITAL通常版・TYPE REAL 餅つきウサギ版 / v0.3.5](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.5) — 月の上に小さなポリゴンのウサギを追加。両版のROM・GIF・無音MP4を更新しました。

[ORBITAL通常版 自転方向修正版 / v0.3.3](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.3) — 通常版を西から東への自転に修正。TYPE REALはv0.3.1から変更ありません。

[ORBITAL通常版・TYPE REAL 地球テクスチャ修正版 / v0.3.1](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.1) — 両版の左右反転を修正しました。

[v0.1.1 リリース・ROMと無音MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.1.1)

ROMは **ASCII16**（OBSIDIAN: 256KiB、ほか: 1MiB）。操作は不要です。音声はありません。エミュレータ・BIOS・FPGAビットストリームは同梱していません。

| Demo | 内容 | Preview |
|---|---|---|
| OBSIDIAN / TITAN PASS | 巨大戦艦への接近飛行 / battleship flyby | [Details](docs/OBSIDIAN.md) |
| NIGHT RAVEN | 巨大艦沿いの宇宙迎撃戦 / space combat | [Details](docs/NIGHT_RAVEN.md) |
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

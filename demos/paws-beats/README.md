# PAWS & BEATS — A Magical Concert of Twinkling Stars / 星がきらめく魔法の演奏会

A cat plays the melody of **Twinkle, Twinkle, Little Star** on a xylophone while a rabbit accompanies it on drums. Geo3D draws the textured polygon characters and instruments in real time; OPLL produces the melody and percussion. This automatic, demo (approximately 32 seconds on R800, 60 seconds in our Z80 test) needs no controls.

猫が木琴で「きらきら星」を弾き、うさぎがたいこで伴奏します。Geo3Dのテクスチャ付きポリゴンとOPLLを組み合わせた、自動演奏デモ（R800で約32秒、今回のZ80測定で約60秒）です。

## Download / ダウンロード

[ROM, sound MP4, silent GIF and checksums](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/paws-beats-v0.1.1)

- ROM: **1 MiB / ASCII16**. Target: MSX2/2+ (Z80) or TurboR (R800), with V9968 + Geo3D + MSX-MUSIC (OPLL).
- MP4 includes audio; GIF is silent. Neither is sped up. MP4 gain is adjusted for listening.
- Tested on a dedicated patched openMSX build only. **Physical hardware, BlueMSX+, and stock/current upstream openMSX are not certified by this release.**
- 専用パッチ版openMSXで確認しています。実機・BlueMSX+・一般配布版openMSXでの同等動作を保証するものではありません。

## How the contact effect works / 星が出る仕組み

**Sprites are embedded at the mallet tips, and receiving sprites are placed at the instruments' playing surfaces. When the collision flag is set, stars briefly sparkle around that instrument.**

バチの先端には判定用スプライトを仕込み、楽器の打面にも受け側のスプライトを配置しています。実際にスプライトの接触フラグが立つと、その楽器の周囲に星が短くきらめきます。

The visible mallet-head sprites match the head color; the receiving sprites use transparent color 0. A blue-outline-style test overlay is not part of this performance. The CPU reads **S#0 bit 5** using IN, and uses that result to start a short sparkle lifetime. Cat and rabbit are polled in alternate frames, with two mallet/receiver pairs per instrument. Idle performers disable receiver hitboxes. Star tiles are drawn with transparent VDP copies.

This is **screen-space sprite overlap**, not an intrinsic Geo3D solid-to-solid collision engine. Coordinates place the proxy sprites; they do not award a hit through a software distance test. Detection is sampled and approximate, suitable here for a decorative effect. **Collision controls only the stars, never the score, melody or animation progression.**

これはGeo3Dの立体同士の物理判定ではなく、画面に投影したスプライト同士の判定です。座標計算は判定用スプライトの配置に使い、接触の成否はS#0から取得します。判定は星の演出専用で、発音・曲の進行・振付は独立しています。

## Emulator requirement / 検証環境の条件

Transparent receiver collisions were tested using Alex Moncks's **test-only** sprite-collision patch, adapted to our integrated V9968/Geo3D evaluation build. The patch is not assumed to be included in public openMSX builds.

- [Author's test-only patch](https://github.com/alexmoncks/V9968_Cartridge/blob/eeb13f460cfe531957eb3482195716cfd74b3fc0/geo3d/game/tests/openmsx_sprite_collision_v9968.patch)
- Local integration: buppu3 V9968 base `aea339bed64a63d851e14747cd2422dc02a02d82`, Geo3D source `de29fb854885a38251c03e24596ad4ff95770ef2`.
- For that integrated base, the patch's `hasECOM()` predicate was adapted to `canECOM()`. This records what was tested; it is not a universal patch-installation recipe.
- The tested rule lets a later, eligible transparent sprite collide with an earlier visible sprite dot. It does not imply arbitrary transparent-transparent collision.
- No modified emulator executable, BIOS, machine ROMs or FPGA bitstream is distributed here.

今回の透明受け側との判定には作者のテスト用パッチを利用しました。一般配布エミュレータへ適用済みと解釈しないでください。未対応環境では星の演出が成立しない可能性があります。まずは掲載動画でご覧いただけます。

For a compatible environment with the same machine/extension definitions:

```text
openmsx -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart PAWS-BEATS.ROM -romtype ASCII16
```

Use legally obtained BIOS and separately installed emulator resources. Machine names may differ in other builds.

## Build / ビルド

Python 3, NumPy, Pillow and SDCC's `sdasz80`/`sdldz80` are required. Install tools separately. On the verified Windows environment:

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN = "C:/path/to/sdcc/bin"
python build.py
```

Run from this demo directory. Default locally installed fonts are Consolas; set `ROM_FONT` and `ROM_SMALL_FONT` to alternative licensed font paths. Fonts are not bundled. Font changes can change the ROM's rasterized captions/hash. Output: `out/PAWS-CONCERT.ROM`.

## Z80 optimization v0.1.1 / Z80最適化

The same ROM selects Z80 on MSX2/2+ and R800 on TurboR. Z80 uses unrolled OUTI geometry transfers and CPU-appropriate OPLL settling waits. R800 retains its original transfer loop and audio waits. Models, textures, choreography and music data are unchanged.

A complete cycle in the dedicated patched emulator, with TurboR forced to Z80, improved from **8.91 to 10.70 fps (+20.1%)**. R800 remains **19.97 fps**. All 17 sampled images per CPU match the previous version pixel-for-pixel; collision polling counts match, and recorded audio contains all 56 melody attacks. This is not MSX2/2+ hardware validation. Frame-driven music remains slower on Z80.

Z80用のGeo3D転送とOPLL待ち時間を最適化。専用エミュレータのTurboRをZ80固定にした比較で平均8.91→10.70fps（約20%改善）、R800は19.97fpsを維持しました。各CPUで17場面の画像一致・接触回数一致・実音声56音を確認済み。MSX2/2+実機での確認ではありません。Z80では曲も描画速度に合わせてゆっくりになります。

[Timing and image comparison](../../docs/validation/paws-beats-z80-validation.json) · [Recorded audio check](../../docs/validation/paws-beats-z80-audio-validation.json)

## Verification / 検証

- Complete 640-frame cycle plus restart captured in the dedicated emulator.
- Exported public source rebuild is byte-identical to the approved ROM: `ab5299b409fcaaec396061a43e87f0f647ac618911cb099a74dd82d2b2e1bdf6`.
- Actual recorded PCM checked: **all 56 melody attacks present**, FFT peaks within 3 Hz of intended pitches. OPLL pitch/key/rhythm register checks were also performed. Runtime writes include R800-safe settling delays; key-off preserves pitch bits.
- A receiver-offset control produced no star triggers, while the score and animation continued. Both instruments triggered in the normal run. This control preceded the final audio-only fixes; collision geometry/code was unchanged by those fixes.
- Motion matrices are precomputed; geometry/texture drawing is real-time Geo3D. Emulator timing is not a physical-hardware benchmark. Music is frame-driven and can slow on a slower system.
- Sprite tables occupy 0xF000/0xF800/0xFA00, outside the SCREEN 5 display pages.

公開ソースからのROM再生成一致、全編再生、実音声56音の音程・欠落、接触演出を確認しています。実機確認や性能保証ではありません。

## Music, assets and license / 音楽・素材・ライセンス

The traditional melody is **Ah! vous dirai-je, maman**, commonly used for Twinkle, Twinkle, Little Star. [Mutopia's public-domain score reference](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2236). The simple drum accompaniment and OPLL programming are newly authored; no existing recording or lyrics are included. The xylophone is an FM approximation; drums use OPLL rhythm-mode snare and tom.

The cat/rabbit face texture is AI-generated and reused from our CAT ASCENT demo. Geometry and instruments are authored in code. See [asset provenance](assets/PROVENANCE.md). The original user reference illustration is not distributed.

Code and contributed assets are offered under the repository [MIT license](../../LICENSE), to the extent the contributors hold rights. Retained [Geo3D and V9968 notices](../../THIRD_PARTY_NOTICES.md) apply. External tools retain their own licenses. No exclusive copyright or complete absence of third-party claims is asserted for AI-generated assets.

旋律は古い「きらきら星」のもので、出典楽譜にはPublic Domain表記があります。たいこの伴奏とOPLLデータは本デモ用に作成し、既存録音や歌詞は収録していません。コード・提供素材には権利を有する範囲でMITを適用し、上流の表示を保持します。AI生成素材の独占的権利を主張するものではありません。

## Disclaimer / 免責

Experimental software, supplied **as is**, without warranty of compatibility, performance, accuracy or fitness for a particular purpose. Use at your own risk. The authors accept no liability to the extent permitted by applicable law and the MIT license. Hardware/tool names identify the tested technologies and do not imply endorsement or official certification by their developers.

実験的なデモを無保証で提供します。特定環境での互換性・速度・正確性・適合性を保証せず、利用に伴う損害等については適用法およびMITライセンスの範囲で責任を負いません。ハードウェア・ツール名の記載は、各開発者による公認や動作保証を示すものではありません。

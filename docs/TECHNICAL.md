# Technical notes / 技術説明

## 共通構成

TurboRでROM内のモデルと姿勢データを読み、Geo3Dへ転送します。Geo3Dが頂点変換、投影、面の裏面判定、面単位の陰影、描画順序の処理を行い、V9968へ描画コマンドを渡します。V9968のVRAMが描画先です。Geo3Dが独立した映像出力や独立したフレームバッファを持つ構成ではありません。

The TurboR streams models and precomputed poses. Geo3D transforms/projects geometry, performs per-face culling, lighting and painter sorting, and emits V9968 commands. V9968 owns the displayed framebuffer. Solid spans use LINE; textured spans use height-one LRMM commands.

- SCREEN 5、256×212、16色。表示用2ページを切り替え、別領域に背景・HUD・テクスチャを保持します。
- CPUはTurboRの高速モードを選択。表示ループは描画完了を待ち、垂直帰線期間に表示ページを切り替えます。
- R#21=0、R#20=1をPort#4のロック解除後に設定。Geo3D実行中はCPUから競合するVDP描画レジスターを書きません。
- 各モデルは1回のRUNにつき255頂点・255面以内。複数RUNで画面を組み立てます。
- **頂点描画は実行時、移動やカメラは事前計算**です。物理シミュレーションや遊べるゲームの処理能力をそのまま示すものではありません。

## VECTOR / RUSH

32区間のコースを用意し、直近4区間と3台の車を描きます。曲率・高低差・バンクを持つポリゴン道路、縁石、ガードレール、港、観客席などで奥行きと速度を表現します。背景の空にはV9968 LRMMを使用します。表示速度計は演出値です。

The camera follows the banked, elevated course. Vehicle paths are scripted, not AI or vehicle physics. Four road chunks plus three vehicles are submitted per frame. Distant-car occlusion over hills is approximate because there is no shared Z-buffer across RUN batches.

## SKYBOUND（テクスチャ版）

操縦席視点で港湾から谷へ進み、僚機2機が並走します。地形の草地・山腹にAI生成画像を既存の3色へ変換したテクスチャを貼っています。128×128の素材を横に複製して256×128のアトラスとし、VRAM Y=1024へ配置。モデルバンク2・3の空き領域を使ってROM容量を1MiBに保ちます。

Terrain uses per-face UV coordinates and LRMM spans. The texture revision increases rendering cost compared with the earlier flat-shaded version. The flight path remains the same, but waiting for rendering slows the loop. Cockpit needles are decoration; altitude is a scene-coordinate display, not a calibrated instrument. There is no interactive flight model or collision system.

## ORBITAL

地球は222頂点・240面、月は146頂点・160面、合計400面のモデルです。裏面判定があるため、400面が常に実際に塗られるわけではありません。月は地球へ常に同じ面を向ける姿勢で公転し、球体単位の前後関係も切り替えます。遠方を時々小さなUFO（96頂点・78面）が横切ります。

Texture atlas: 256×128, Earth in rows 0–63, Moon in 64–127. Seven pre-shaded copies occupy VRAM Y=1024–1919. Transformed normals and a fixed virtual light select the shade copy using Geo3D TSTRIDE=128. Textures are AI-generated approximations, not scientific maps. Orbital distances, sizes and periods are chosen for presentation; the bodies do not cast shadows on each other.

## 制約

- Zバッファなし。面のソートはRUN単位で、透明物・交差物・大きく入り組んだ地形の完全な隠面処理はできません。
- アフィンテクスチャ。透視補正やフィルタリングはなく、拡大時の歪み・遠景のちらつきがあり得ます。
- 近面をまたぐ面は完全なクリッピングではなく省略される場合があります。
- 1MiB ROMは空き・パディングを含むサイズです。3本をまとめた1MiB ROMではありません。
- エミュレータ上の描画速度はFPGA実機の性能評価値ではありません。

The Moon orientation is constructed from its direction toward Earth and the fixed orbital-plane normal. Earth rotation and all planetary positions are unchanged. A small UFO passes behind the planets once per loop (240 of 1536 pose records); this is an occasional visual cameo, not an astronomical claim.

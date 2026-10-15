# NIGHT RAVEN — Three-stage Geo3D v2 test v0.1.0

**3ステージ構成の操作可能な開発デモをGeo3D v2へ対応した別版です。完成ゲームではありません。** 1ステージ自動デモの「NIGHT RAVEN Geo3D V2.0 edition」とは異なります。旧3ステージ版v0.5.0は保持しています。

**音楽・効果音は暫定で更新予定、ステージ進行も最終版とは異なる可能性があります。**

[ROM・配布セット](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/night-raven-three-stage-geo3d-v2-v0.1.0)

## 対応環境・操作

1 MiB / ASCII16。TurboR/R800＋V9968＋**Geo3D v2専用**。v1への自動フォールバックはありません。作者の[openMSX geo3d-v2.0](https://github.com/alexmoncks/openMSX/tree/geo3d-v2.0)、commit `67811936bee936c15e3fbdbdffe01755fd349876` で確認しました。実機・FPGA・BlueMSX+ v2・Z80は本版では未検証です。一般配布のopenMSXで動くとは限りません。エミュレータ・BIOSは含めません。

```powershell
& 'C:/path/to/geo3d-v2-openmsx/openmsx.exe' -machine Panasonic_FS-A1ST_V9968 -ext geo3d -cart './NIGHT_RAVEN_GEO3D_V2.ROM' -romtype ASCII16
```

方向キーで移動、Spaceで開始・バルカン・再挑戦、Xでロック後のミサイル、Escで一時停止・再開、F1で区間再開始。物理ジョイスティックは本版では未検証です。

## 変更内容

Geo3D v2の拡張面RAMとFFIRSTを利用し、7種類282面を256番以降へ常駐。モデル変更時の面データ再転送を省きました。壁・床は低位面領域を使い、描画前にFFIRST/FADDR_Hを戻します。248頂点の共有プールと旧11バイト面形式を維持し、各モデルを256面境界をまたがないよう配置しています。画面は16色SCREEN 5のままです。

[仕様資料](https://github.com/alexmoncks/V9968_Cartridge/blob/885cff1fc5c3e8c38af9ac39112b7bdd73371b9e/geo3d/docs/geo3d_v2.md)。ゲーム進行、AI、モデル、配色、音、2面デザインは旧R27から変更していません。

## 性能比較 — 2026-10-15

ゲーム内ポーズで状態を固定し、各200描画フレームのDONEカウンタ増分÷3をopenMSX仮想経過秒で割ったfpsです。throttle offで収集していますがPCの実時間fpsではありません。固定場面の測定であり、ステージ全体の平均fpsではありません。

| 場面 | 旧openMSX＋旧ROM | v2 openMSX＋旧ROM | v2対応ROM |
|---|---:|---:|---:|
| 1面・外壁 | 20.04 | 20.04 | 20.04 |
| 2面・通路 | 30.10 | 30.08 | 30.09 |
| 2面・広間 | 30.08 | 30.11 | 30.11 |
| 白烏1対1 | 60.02 | 60.22 | 60.07 |
| 追加負荷試験：軽い背景＋異なる敵3種類 | 30.07 | 30.09 | 60.17 |

**通常場面では明確なfps改善を確認していません。** 追加の人工的な多機種同時表示試験では約30→60fpsとなりましたが、通常の3面やゲーム全体が2倍速くなるという意味ではありません。0.4%程度までの差は開始位相等の差として扱います。

openMSXのGeo3D幾何処理は実機相当の処理時間をモデル化していません。v2 RTLの除算・ソート高速化そのものはこの測定で評価できません。実機性能を保証する数値ではありません。

5固定場面で旧版・新版上の旧ROM・対応ROMの表示用VRAMが一致。自動操作で1・2面ボス撃破→3面進行→自機撃墜を確認しました。全3面クリア・全操作・全場面の回帰検証ではありません。

計測スクリプトの関数名がopenMSX内蔵setupと衝突する問題を修正済みです。修正後は全3条件が正常終了し、上表は再測定した結果です。ゲームROMへの回避処理は追加していません。

## ビルド・再測定

Python 3、NumPy、Pillow、SDCCのassembler/linkerが必要です。リポジトリ直下で：

```powershell
python -m pip install -r requirements.txt
$env:SDCC_BIN='C:/path/to/sdcc/bin'
python demos/night-raven-three-stage-geo3d-v2/build.py
```

出力は `out/NIGHT_RAVEN_GEO3D_V2.ROM`。SHA256：`e9a7961ea18c129f18dc56e3794fa64c7edd260575705ba97c7177e482cdbf47`。

比較には `NR_BASELINE_ROM` に旧3ステージv0.5.0 ROM、`GEO3D_OLD_RUNTIME` と `GEO3D_V2_RUNTIME` に各openMSX.exe/share/userdata/homeを持つ専用フォルダーを設定し、`python demos/night-raven-three-stage-geo3d-v2/compare.py` を実行します。旧openMSXは作者geo3dブランチ `de29fb854885a38251c03e24596ad4ff95770ef2`。生データとハッシュは `results/` に同梱しています。

## License / Disclaimer

独自ソース・手続き生成素材・暫定音楽／効果音は、権利を有する範囲で[MIT](../../LICENSE)。[第三者通知](../../THIRD_PARTY_NOTICES.md)、[Geo3D MIT](../../LICENSES/Geo3D-MIT.txt)、[V9968通知](../../LICENSES/V9968-MIT.txt)を保持しています。エミュレータ、BIOS、外部ツールはそれぞれのライセンスに従い、本配布には含めません。

現状有姿・無保証の非公式試験版です。動作、互換性、性能、保守、完成、将来の更新は保証しません。適用法令で認められる範囲で責任を負いません。ハードウェア作者による品質認証ではありません。

This unfinished playable three-stage demo requires Geo3D v2 and TurboR/R800. Music/SFX are provisional; stage progression may change. Only the pinned developer openMSX was tested. Physical hardware, FPGA, BlueMSX+ v2 and Z80 are unverified. Normal-scene frame rates are essentially unchanged; the approximately 2x gain applies only to the synthetic mixed-model test. Provided AS IS under the applicable MIT licenses, without warranty.

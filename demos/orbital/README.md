# orbital

See [repository README](../../README.md), [usage](../../docs/USAGE.md), [technical notes](../../docs/TECHNICAL.md), and [validation](../../docs/VALIDATION.md).

## v0.3.1 — Earth texture orientation fix

地球のテクスチャが左右反転していた問題を修正しました。両版の自転速度・月の動きは維持しています。
Corrected mirrored Earth UV mapping. Rotation speeds and lunar motion are unchanged.

[Updated ROM, GIF and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.1)

## v0.3.3 — Standard edition rotation direction

通常版の地球の自転方向を西から東へ修正。速度・月の公転・テクスチャは変更していません。TYPE REALは変更不要です。
Corrected the standard edition to rotate west to east; speed and lunar motion are unchanged. TYPE REAL is unchanged.

[Corrected standard ROM, GIF and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.3)

## v0.3.4 — Moon rabbit / 月の餅つきウサギ

月の上に小さなウサギ・杵・臼を追加。16姿勢のポリゴンモデルで餅つきします。ROMは1 MiBのままです。地球と月の運動データは維持していますが、描画負荷が増え、専用openMSXでの1周は約25.63秒になりました。TYPE REALの自転周期比27.3は維持しています。従来の18.42秒という計測値はウサギ追加前の値です。

Added a small polygon rabbit pounding mochi on the Moon. Sixteen animation poses reuse free ROM banks. One extra Geo3D object raises rendering load: a cycle now takes about 25.63 seconds in the evaluated emulator, not the earlier 18.42 seconds. This is not a physical hardware speed measurement.

[Updated ROM, GIF and silent MP4](https://github.com/kanon-ai/V9968_Geo3D_SampleDemo/releases/tag/v0.3.5)

### v0.3.5

ウサギと餅つき道具を月の姿勢に連動させ、常に地球側を向くよう調整しました。サイズ・餅つき動作・天体の動きは維持しています。
Rabbit and mochi tools now follow the lunar orientation, facing Earth. Size, animation and planetary motion are unchanged.

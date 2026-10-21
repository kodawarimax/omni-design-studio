# 🖼 Sana — flower_jewelry 画像の簡単入れ替えガイド（2-Way Manual Image Swap）

本パッケージでは、HTML内に巨大なBase64データを埋め込まず、すべての作品写真（全12枚＋パッケージ画像）を **`assets/` フォルダ（および `production/assets/`）** に独立配置しています。

---

## 方法A：ブラウザ上でドラッグ＆ドロップで入れ替える（一番簡単・3秒）
1. `website.html`、`flyer_a4.html`、`packaging_mockup.html` のいずれかをChrome等のブラウザで開きます。
2. 画面右下の **`[🖼 画像を簡単入れ替え: OFF]`** ボタンをクリックして **`ON`** にします。
3. 入れ替えたい作品写真をクリックして新しい画像を選ぶか、パソコン上の画像ファイルをその写真の枠へ直接 **ドラッグ＆ドロップ** します。
4. 右下の **`[💾 差替後のHTMLを保存]`** を押すと、差し替え後のHTMLファイルがそのまま保存されます。

---

## 方法B：`assets/` フォルダ内の同名ファイルを上書きする
以下のファイル名で `assets/`（および `production/assets/`）内の画像を上書き保存すると、HTMLを編集することなく即座にWebサイト・A4フライヤー・パッケージ仕様書の画像が一括更新されます。

| アセットファイル名 | 元ファイル名 (`Sana/` フォルダ) | 内容 |
| :--- | :--- | :--- |
| `assets/01_sana_brand_card_pansy.jpg` | `S__52355083_0.jpg` | `Sana flower_jewelry` 専用台紙付きビオラ耳飾り |
| `assets/02_mint_hydrangea_glass.jpg` | `S__52355088_0.jpg` | 氷翠アジサイの立体フラワークラスター耳飾り |
| `assets/03_wearing_white_blossom_hair.jpg` | `S__52355089_0.jpg` | 白花のクリアボタニカル・ポニーフック（着用カット） |
| `assets/04_white_rose_bridal_comb.jpg` | `S__52355082_0.jpg` | 白薔薇と淡水パール調ビジューのセレモニーコーム |
| `assets/05_cobalt_hydrangea_book.jpg` | `S__52355090_0.jpg` | 深蒼（コバルトブルー）アジサイのポニーフック |
| `assets/06_mint_cobalt_pair_stone.jpg` | `S__52355091_0.jpg` | 紫陽花ポニーフック 2カラー（アイスミント＆コバルト） |
| `assets/07_bouquet_trio_book.jpg` | `S__52355092_0.jpg` | パンジー＆小花ブーケの立体バレッタ・ポニーフック |
| `assets/08_sakura_pearl_stone.jpg` | `S__52355093_0.jpg` | 桜モーブの花びらとパール粒のポニーフック |
| `assets/09_ice_mint_long_barrette.jpg` | `S__52355094_0.jpg` | 淡翠アジサイと朝露ドロップのロングバレッタ |
| `assets/10_crystal_medallion_earrings.jpg` | `S__52355087_0.jpg` | フラワーメダリオン＆クリスタルドロップ耳飾り |
| `assets/11_teardrop_botanical_earrings.jpg` | `S__52355086_0.jpg` | ボタニカル・ティアドロップ耳飾り（3色） |
| `assets/12_pressed_strawberry_cases.jpg` | `S__52355084.jpg` | 本物の押し苺＆マーガレットのスマホケース（波なみ型はiPhoneのみ・全機種要相談） |
| `assets/qr_sana_official.png` | 自動生成QR | BASE公式ショップ（`https://shop.sanaflowerjewelry.com`）遷移用QRコード |

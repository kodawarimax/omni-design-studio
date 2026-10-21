# 🔍 E2E 自動検証レポート（エラー・画像・ページ内アンカー・外部リンク・QRコード・UI動作）

- **総合判定**: **✅ PASS (全項目エラー0・全リンク＆QR疎通確認済み)**
- **検証対象パッケージ**: `/Users/jungosakamoto/Downloads/GENMAI_CLEANSE_PARTNER_SUITE_V3`
- **検証HTMLファイル数**: `14 ファイル`（確認用・本番納品用すべて含む）

## 1. QRコード ＆ 外部遷移先URL 疎通検証

| 検証対象 | 抽出URL / リンク先 | 最終遷移先 (Redirect解決後) | HTTPステータス | 判定 |
| :--- | :--- | :--- | :---: | :---: |
| QRコード (`assets/qr_line_official.png`) ＆ 申込CTAボタン | `https://lin.ee/XOWYwEM` | `https://line.me/R/ti/p/@532tekda` | `200` | ✅ 正常遷移 |

## 2. 全HTMLファイル E2E ブラウザ検査結果（Playwright Chrome 実機検証）

| ファイル名 | Consoleエラー | JS例外 (`pageerror`) | 通信失敗 (`requestfailed`) | 画像読込 (`naturalWidth>0`) | リンク・アンカー (`#hash` / URL) | UIウィジェット動作 | 判定 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ai_clone_qa_spec.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `flyer_a4_back.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `flyer_a4_double.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `flyer_a4_front.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `manuals_organized.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `packaging_mockup.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `production/flyer_a4_double_production.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `production/packaging_mockup_production.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `production/website_production.html` | `0件` | `0件` | `0件` | `11/11枚 正常` | `11件 正常` | ai_clone_drawer_and_6_faqs:OK, image_swapper_toggle:OK | **✅ PASS** |
| `promo_video_studio_9x16.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `uword_banner.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `uword_page_kit.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `website.html` | `0件` | `0件` | `0件` | `11/11枚 正常` | `11件 正常` | ai_clone_drawer_and_6_faqs:OK, image_swapper_toggle:OK, review_production_mode_switcher:OK | **✅ PASS** |
| `ycs_creative_brief_b1_b7.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |

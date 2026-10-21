# 🔍 E2E 自動検証レポート（エラー・画像・ページ内アンカー・外部リンク・QRコード・UI動作）

- **総合判定**: **❌ FAIL**
- **検証対象パッケージ**: `/Users/jungosakamoto/Claude/dev/omni-showcase-pages`
- **検証HTMLファイル数**: `28 ファイル`（確認用・本番納品用すべて含む）

## 1. QRコード ＆ 外部遷移先URL 疎通検証

| 検証対象 | 抽出URL / リンク先 | 最終遷移先 (Redirect解決後) | HTTPステータス | 判定 |
| :--- | :--- | :--- | :---: | :---: |
| 外部リンク | `https://lin.ee/XOWYwEM` | `https://line.me/R/ti/p/@532tekda` | `200` | ✅ 正常遷移 |
| 外部リンク | `https://shop.sanaflowerjewelry.com` | `https://shop.sanaflowerjewelry.com` | `200` | ✅ 正常遷移 |

## 2. 全HTMLファイル E2E ブラウザ検査結果（Playwright Chrome 実機検証）

| ファイル名 | Consoleエラー | JS例外 (`pageerror`) | 通信失敗 (`requestfailed`) | 画像読込 (`naturalWidth>0`) | リンク・アンカー (`#hash` / URL) | UIウィジェット動作 | 判定 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `genmai/ai_clone_qa_spec.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `genmai/flyer_a4_back.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/flyer_a4_double.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/flyer_a4_front.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/manuals_organized.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `genmai/packaging_mockup.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/production/flyer_a4_double_production.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `1件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/production/packaging_mockup_production.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/production/website.html` | `0件` | `0件` | `0件` | `11/11枚 正常` | `11件 正常` | ai_clone_drawer_and_6_faqs:OK, image_swapper_toggle:OK | **✅ PASS** |
| `genmai/production/website_production.html` | `0件` | `0件` | `0件` | `11/11枚 正常` | `11件 正常` | ai_clone_drawer_and_6_faqs:OK, image_swapper_toggle:OK | **✅ PASS** |
| `genmai/promo_video_studio_9x16.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `genmai/uword_banner.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/uword_page_kit.html` | `0件` | `0件` | `0件` | `1/1枚 正常` | `0件 正常` | image_swapper_toggle:OK | **✅ PASS** |
| `genmai/website.html` | `0件` | `0件` | `0件` | `11/11枚 正常` | `11件 正常` | ai_clone_drawer_and_6_faqs:OK, image_swapper_toggle:OK, review_production_mode_switcher:OK | **✅ PASS** |
| `genmai/ycs_creative_brief_b1_b7.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `index.html` | `0件` | `0件` | `0件` | `2/2枚 正常` | `20件 正常` | 静的表示:OK | **✅ PASS** |
| `sana/flyer_a4.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/packaging_mockup.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/production/flyer_a4.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/production/packaging_mockup.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/production/website.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `25件 正常` | omni_image_swapper_toggle:OK, sana_concierge_qa:OK | **✅ PASS** |
| `sana/review/flyer_a4.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/review/packaging_mockup.html` | `0件` | `0件` | `0件` | `3/3枚 正常` | `2件 正常` | omni_image_swapper_toggle:OK | **✅ PASS** |
| `sana/review/website.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `25件 正常` | omni_image_swapper_toggle:OK, sana_concierge_qa:OK | **✅ PASS** |
| `sana/website.html` | `0件` | `0件` | `0件` | `17/17枚 正常` | `25件 正常` | omni_image_swapper_toggle:OK, sana_concierge_qa:OK | **✅ PASS** |
| `sana/ycs_creative_brief_b1_b7.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `0件 正常` | 静的表示:OK | **✅ PASS** |
| `sana/ycs_marketing_strategy_report.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `6件 正常` | 静的表示:OK | **✅ PASS** |
| `sana/ycs_user_hearing_sheet.html` | `0件` | `0件` | `0件` | `0/0枚 正常` | `7件 正常` | 静的表示:OK | **✅ PASS** |

# Omni-Design Studio (`omni-design-studio`)

**コンセプト質問シート・参考デザイン（画像/URL/100件人間キュレーション）から色彩・構図・テイストDNAとキャッチコピーを0msで決定論的抽出し、サブスク0円の最上位画像モデル（Codex `image_gen` [`gpt-image-2.5-sunburst`] または Antigravity `image-generator` [`Imagen 4 Ultra`]）の写真素材と合成して、以下の4大クリエイティブ＋事後編集データを3ステップで一括生成する統合デザインスキルです。**

1. 🌐 **Webサイト (`website.html` / `website_preview.png`)** — WordPress風ビジュアルエディタ（`✦ OMNI WP-STUDIO`）内蔵
2. 🖨️ **300DPI印刷ポスター (`poster.html` / `poster_300dpi.png` / `poster_print.pdf`)** — WordPress風ビジュアルエディタ内蔵＋A判ベクターPDF
3. 📦 **パッケージデザイン (`packaging_mockup.html` / `packaging_3d_mockup.png` / `packaging_dieline.svg`)** — WordPress風ビジュアルエディタ内蔵＋Illustrator用ダイライン展開図SVG
4. 🎬 **プロモーショナルビデオ (`promo_video_vertical_9x16.mp4` / `promo_video_landscape_16x9.mp4`)** — ブラウザ字幕＆タイムライン編集スタジオ（`promo_video_studio_9x16.html` / `16x9.html`）＋ Premiere/CapCut用 `.srt` / `.vtt` 字幕 ＋ 独立音声 `.wav` 付き

---

## 🚀 Codex / Claude Code へのインストール（1コマンド）

```bash
git clone https://github.com/kodawarimax/omni-design-studio.git
cd omni-design-studio
bash install.sh
```

### Codex での呼び出し方
* `$omni-design-studio で「小物アクセサリー（カジュアル）」のWeb・ポスター・パッケージ・プロモ動画を作って`
* `/prompts:omni-design-studio ブランド名「MERRY LOOP」で一式作成して`

### Claude Code での呼び出し方
* `/omni-design-studio 小物アクセサリー（カジュアル）のWeb・ポスター・パッケージ・プロモ動画を作って`

---

## 📂 ディレクトリ構成

* [`SKILL.md`](./SKILL.md) — 下位モデルでも同一品質を出せる「3ステップ決定論パイプライン」定義＆Mermaidステートマシン図
* [`agents/openai.yaml`](./agents/openai.yaml) — Codex ネイティブスキルUI定義
* [`commands/omni-design-studio.md`](./commands/omni-design-studio.md) — Claude Code `/omni-design-studio` スラッシュコマンド定義
* [`prompts/omni-design-studio.md`](./prompts/omni-design-studio.md) — Codex `/prompts:omni-design-studio` プロンプト定義
* [`templates/CONCEPT_QUESTION_SHEET.md`](./templates/CONCEPT_QUESTION_SHEET.md) — 5部構成コンセプト＆キャッチコピー質問シート
* [`scripts/build_omni_design.py`](./scripts/build_omni_design.py) — 全媒体統合ビルドパイプライン（エントリーポイント）
* [`scripts/cms_editor_runtime.py`](./scripts/cms_editor_runtime.py) — WordPress風ビジュアルブロック＆キャンバスエディタ・動画字幕スタジオ注入ランタイム
* [`scripts/build_promo_video.py`](./scripts/build_promo_video.py) — 24fps 1080p プロモーショナルビデオ＆SRT字幕・音声合成エンジン
* [`scripts/analyze_user_reference.py`](./scripts/analyze_user_reference.py) — 参考画像・参考URLからの色彩・フォント・枠形状・テイストDNA自動抽出エンジン
* [`scripts/build_concept_and_copy.py`](./scripts/build_concept_and_copy.py) — コンセプト質問シートからのキャッチコピー・ナレーション自動合成エンジン
* [`scripts/curate_human_designs.py`](./scripts/curate_human_designs.py) — 人間デザイナー100選キュレーション＆コンタクトシート生成
* [`samples/merry_loop_casual_accessory/`](./samples/merry_loop_casual_accessory/) — カジュアル小物アクセサリー「MERRY LOOP」の生成サンプル一式

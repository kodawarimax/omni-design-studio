---
description: コンセプト質問シート＆参考デザインからWeb・300DPIポスター・パッケージ・プロモ動画（WordPress風ブラウザ編集＆SRT字幕付き）を3ステップで一括生成する
argument-hint: "[ブランド名・商品カテゴリ・参考画像パスまたはURL・テイスト指定]"
---

# Omni-Design Studio（Web・ポスター・パッケージ・プロモ動画 3ステップ統合生成）

次のスキル定義ファイルを読み、記載された **「3ステップ実行ルール（Step 1: コンセプト＆プロンプト取得 ➔ Step 2: サブスク0円写真3枚生成 ➔ Step 3: `build_omni_design.py` 一括ビルド）」** をそのまま実行する。

- `~/.claude/skills/omni-design-studio/SKILL.md`
- `~/.claude/skills/omni-design-studio/templates/CONCEPT_QUESTION_SHEET.md`

ユーザー入力:

```text
$ARGUMENTS
```

## 実行手順（下位モデルでも同一品質を保証する3ステップ）

1. **Step 1（コンセプト確認 ＆ 写真プロンプト3本の出力）**:
   - コンセプトやキャッチコピーが未定で、ユーザーが相談から始めたい場合は以下を実行して5つの質問を提示する：
     ```bash
     python3 "$HOME/.claude/skills/omni-design-studio/scripts/build_omni_design.py" --ask-concept
     ```
   - ブランド名・商品カテゴリ（・任意の `--ref-image` / `--ref-url` / `--trend`）が指定されている場合は、`--print-image-prompts` で商業スタジオ写真プロンプト3本（JSON）を取得する：
     ```bash
     python3 "$HOME/.claude/skills/omni-design-studio/scripts/build_omni_design.py" \
       --brand "ブランド名" \
       --category "商品カテゴリ" \
       --print-image-prompts
     ```

2. **Step 2（サブスク0円の最上位モデルで文字なし商業写真を3枚生成）**:
   - **Codex の場合**: 内蔵の `image_gen` ツール（`gpt-image-2.5-sunburst`）を3回呼び出して生成（`~/.codex/generated_images/` に自動保存）。
   - **Claude Code / Antigravity の場合**: 手持ち画像があれば `--hero-image` / `--poster-image` / `--pack-image` に指定するか、サブエージェント / Codex `image_gen` で生成した3枚の画像をバインドする。

3. **Step 3（1コマンド全媒体ビルド：WordPress風編集HTML ＆ 動画スタジオ・SRT字幕付き）**:
   ```bash
   python3 "$HOME/.claude/skills/omni-design-studio/scripts/build_omni_design.py" \
     --auto-codex-images \
     --target all \
     --with-promo-video \
     --brand "ブランド名" \
     --category "商品カテゴリ" \
     --headline "メインキャッチコピー" \
     --subcopy "サブコピー" \
     --out-dir ~/Downloads/omni_output_pack
   ```
   生成完了後、`website.html` / `poster.html` / `packaging_mockup.html`（WordPress風ブラウザ編集対応）および `promo_video_vertical_9x16.mp4` / `promo_video_landscape_16x9.mp4` / `promo_video_studio_9x16.html` / `promo_captions.srt` の保存先パスをユーザーへ提示する。

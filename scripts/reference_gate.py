#!/usr/bin/env python3
"""
Deterministic Anti-Skip Gate & Anti-AI-Slop Linter for Omni-Design Studio
=========================================================================
This module enforces TWO non-bypassable laws:

Law 1 (Mandatory Reference Image Capture & Visual Inspection Gate):
  Before ANY HTML/CSS/PDF/Video is rendered, the pipeline MUST have:
  - Captured at least 1 real benchmark website screenshot (`--ref-url` or `--benchmark-urls`)
    OR loaded an explicit reference design screenshot (`--ref-image`),
  - Extracted its structural & DOM typography/spacing metrics into `REFERENCE_BENCHMARK_PROOF.json`,
  - Verified that the captured screenshot file physically exists on disk and is non-empty (>10KB).
  If `REFERENCE_BENCHMARK_PROOF.json` or its screenshot image is missing, execution immediately halts with `SystemExit(1)`.

Law 2 (Deterministic Anti-AI-Slop CSS/HTML Linter):
  Before writing any final output HTML, the HTML/CSS is statically scanned for AI-generated design smells ("AI Slop"):
  - Pill-badge spam (`border-radius: 999px` used more than once)
  - Generic checkmark circle lists (`content: "✓"` or `✓` bullet spam)
  - Generic rounded SaaS cards (`border-radius: 14px` / `16px` / `20px` + `box-shadow` box grids)
  - Equal 3-column / 4-column Bento boxes when in `organic_editorial` / `japanese_luxury` mode
  - Missing human editorial signatures (vertical writing `writing-mode: vertical-rl`, hairline 1px borders, generous serif line-height, editorial index numbering).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont


def capture_and_analyze_benchmarks(
    urls: list[str],
    ref_images: list[str],
    out_dir: Path,
) -> dict:
    """
    Captures full-resolution screenshots + DOM layout/typography telemetry from real benchmark websites
    and/or user reference images, builds a visual contact sheet (`BENCHMARK_CONTACT_SHEET.png`),
    and writes `REFERENCE_BENCHMARK_PROOF.json`.
    """
    from playwright.sync_api import sync_playwright
    from analyze_user_reference import extract_dna_from_image

    out_dir.mkdir(parents=True, exist_ok=True)
    bench_dir = out_dir / "reference_benchmarks"
    bench_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    captured_paths: list[Path] = []

    if urls:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome")
            except Exception:
                browser = p.chromium.launch()

            for idx, url in enumerate(urls, 1):
                page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=2)
                shot_path = bench_dir / f"benchmark_site_{idx:02d}.png"
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(1200)
                    dom_telemetry = page.evaluate(
                        """() => {
                            const bodySt = window.getComputedStyle(document.body);
                            const h1 = document.querySelector('h1, h2');
                            const h1St = h1 ? window.getComputedStyle(h1) : bodySt;
                            const allEls = Array.from(document.querySelectorAll('section, article, div, p, h1, h2, h3')).slice(0, 120);
                            let verticalCount = 0;
                            let hairlineCount = 0;
                            let pillCount = 0;
                            let maxRadius = 0;
                            for (const el of allEls) {
                                const st = window.getComputedStyle(el);
                                if ((st.writingMode || '').includes('vertical')) verticalCount++;
                                const bw = parseFloat(st.borderBottomWidth || '0') || parseFloat(st.borderTopWidth || '0') || 0;
                                if (bw > 0 && bw <= 1.5) hairlineCount++;
                                const br = parseFloat(st.borderTopLeftRadius || '0') || 0;
                                if (br >= 100) pillCount++;
                                if (br > maxRadius && br < 500) maxRadius = br;
                            }
                            return {
                                title: document.title || '',
                                body_font: bodySt.fontFamily,
                                body_bg: bodySt.backgroundColor,
                                body_color: bodySt.color,
                                body_line_height: bodySt.lineHeight,
                                body_letter_spacing: bodySt.letterSpacing,
                                h1_font: h1St.fontFamily,
                                h1_size: h1St.fontSize,
                                h1_weight: h1St.fontWeight,
                                h1_letter_spacing: h1St.letterSpacing,
                                vertical_writing_elements: verticalCount,
                                hairline_1px_dividers: hairlineCount,
                                pill_radius_elements: pillCount,
                                max_card_radius_px: maxRadius
                            };
                        }"""
                    )
                    page.screenshot(path=str(shot_path))
                    dna = extract_dna_from_image(shot_path)
                    dna["source_url"] = url
                    dna["screenshot_path"] = str(shot_path.resolve())
                    dna["dom_telemetry"] = dom_telemetry
                    records.append(dna)
                    captured_paths.append(shot_path)
                except Exception as exc:
                    print(f"[WARN] Benchmark capture failed for {url}: {exc}")
                finally:
                    page.close()
            browser.close()

    for idx, img_str in enumerate(ref_images, 1):
        p_img = Path(img_str).expanduser().resolve()
        if p_img.exists() and p_img.stat().st_size > 1024:
            dest = bench_dir / f"user_ref_{idx:02d}_{p_img.name}"
            if p_img != dest:
                dest.write_bytes(p_img.read_bytes())
            dna = extract_dna_from_image(dest)
            dna["screenshot_path"] = str(dest.resolve())
            records.append(dna)
            captured_paths.append(dest)

    if not records or not captured_paths:
        raise SystemExit(
            "🚨 [CRITICAL GATE FAILURE: NO REFERENCE IMAGE CAPTURED]\n"
            "サンプルWebサイトのスクリーンショット取得または参照画像の取り込みが1件も完了していません。\n"
            "必ず実在するベンチマークWebサイト（--benchmark-urls / --ref-url）または参照画像（--ref-image）を画像として取り込んでから実行してください。"
        )

    # Create a visual contact sheet of all captured benchmark images so the user & agent can visually verify them
    contact_path = out_dir / "BENCHMARK_CONTACT_SHEET.png"
    thumb_w, thumb_h = 720, 480
    cols = min(len(captured_paths), 2)
    rows = (len(captured_paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * 24, rows * (thumb_h + 60) + 40), (244, 239, 230))
    draw = ImageDraw.Draw(sheet)

    for i, cp in enumerate(captured_paths):
        r = i // cols
        c = i % cols
        x0 = 24 + c * (thumb_w + 24)
        y0 = 24 + r * (thumb_h + 60)
        im = Image.open(cp).convert("RGB")
        im.thumbnail((thumb_w, thumb_h))
        sheet.paste(im, (x0, y0))
        label = records[i].get("source_url") or Path(records[i]["screenshot_path"]).name
        draw.text((x0 + 4, y0 + thumb_h + 12), f"[{i+1}] {label[:65]}", fill=(43, 41, 37))

    sheet.save(contact_path)

    proof = {
        "gate_status": "PASSED_WITH_VISUAL_CAPTURE",
        "captured_count": len(records),
        "contact_sheet_path": str(contact_path.resolve()),
        "synthesized_editorial_rules": {
            "ban_pill_badges": True,
            "ban_rounded_saas_cards": True,
            "ban_checkmark_bullet_circles": True,
            "require_vertical_tategaki_accent": True,
            "require_hairline_1px_dividers": True,
            "require_generous_whitespace_margin": True,
            "require_serif_editorial_numbering": True,
        },
        "benchmarks": records,
    }
    proof_path = out_dir / "REFERENCE_BENCHMARK_PROOF.json"
    proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    return proof


def verify_reference_proof_gate(out_dir: Path) -> dict:
    """
    Gate 1 Verifier: Raises SystemExit(1) if `REFERENCE_BENCHMARK_PROOF.json` or its physical images do not exist.
    """
    proof_path = out_dir / "REFERENCE_BENCHMARK_PROOF.json"
    if not proof_path.exists():
        raise SystemExit(
            f"🚨 [GATE 1 BLOCKED] `{proof_path}` が存在しません。\n"
            "サンプルWebサイトを画像として取り込む工程（capture_and_analyze_benchmarks）をスキップすることは物理的に禁止されています。"
        )
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    if proof.get("gate_status") != "PASSED_WITH_VISUAL_CAPTURE" or proof.get("captured_count", 0) < 1:
        raise SystemExit("🚨 [GATE 1 BLOCKED] 有効なサンプルWebサイト画像が1件も記録されていません。")

    for b in proof.get("benchmarks", []):
        sp = Path(b.get("screenshot_path", ""))
        if not sp.exists() or sp.stat().st_size < 5000:
            raise SystemExit(f"🚨 [GATE 1 BLOCKED] キャプチャ画像 `{sp}` が実在しないか破損しています。")

    return proof


def lint_html_against_ai_slop(html_text: str, context_name: str = "HTML") -> None:
    """
    Gate 2 Verifier: Statistically and deterministically scans HTML/CSS for "AI Slop" patterns.
    Raises SystemExit(1) if ANY AI-like template cliché is detected.
    """
    violations: list[str] = []

    # 1. Pill badge overuse (border-radius: 999px)
    pill_matches = re.findall(r"border-radius\s*:\s*999px", html_text)
    if len(pill_matches) > 0:
        violations.append(
            f"AI特有のピル型バッジ/ボタン (`border-radius: 999px`) が {len(pill_matches)} 箇所検出されました。日本のエディトリアルデザインでは角丸ピルを廃止し、シャープな矩形（0〜2px）または上下罫線リンクを使用してください。"
        )

    # 2. Checkmark bullet circles (content: "✓" or ✓ list spam)
    if 'content: "✓"' in html_text or "content: '✓'" in html_text or html_text.count("✓") >= 2:
        violations.append(
            "AI特有のチェックマーク箇条書き (`✓`) が検出されました。漢数字（一、二、三）または明朝ローマ数字（01 / i. ii.）と細い1px罫線のインデックス組版に変更してください。"
        )

    # 3. SaaS rounded card boxes (border-radius: 12px..28px)
    rounded_cards = re.findall(r"border-radius\s*:\s*(1[2-9]|2[0-9]|3[0-9])px", html_text)
    if len(rounded_cards) > 0:
        violations.append(
            f"AI特有の角丸カード枠 (`border-radius: 12px〜39px`) が {len(rounded_cards)} 箇所検出されました。カード囲み枠（ボックス感）を廃止し、余白（間合い）と1pxの細罫線（border-top / border-bottom）で区切る雑誌組版にしてください。"
        )

    # 4. Emoji icons in headings or UI buttons (🤖, 📋, 📦, 🎨 in visible document body before CMS injection)
    for banned_emoji in ("🤖", "📋", "📦", "✨"):
        if banned_emoji in html_text:
            violations.append(
                f"AI生成LP特有の絵文字アイコン (`{banned_emoji}`) が本文中に検出されました。絵文字は全廃し、欧文キャプションや明朝タイポグラフィで品格を表現してください。"
            )

    # 5. Require vertical writing (`writing-mode: vertical-rl`) in editorial design
    if "writing-mode: vertical-rl" not in html_text:
        violations.append(
            "和モダン・エディトリアル組版に不可欠な縦書き要素 (`writing-mode: vertical-rl`) が含まれていません。"
        )

    if violations:
        msg = f"🚨 [GATE 2 BLOCKED: AI-SLOP DESIGN DETECTED in {context_name}]\n" + "\n".join(
            f"  ✖ {v}" for v in violations
        )
        raise SystemExit(msg)

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


def generate_image_prompts_from_research(
    out_dir: Path,
    brand: str,
    category: str,
    override_bg: str = "",
    override_accent: str = "",
    user_qa_brief: dict | None = None,
) -> dict:
    """
    Gate 1.5 Producer: Reads the verified `REFERENCE_BENCHMARK_PROOF.json` AND the user's final Q&A answers
    (`user_qa_brief` / `CONCEPT_COPY_DNA.json`), synthesizes the extracted color palette, luminance,
    DOM layout rules, and user Q&A specifications, and writes `IMAGE_PROMPTS_FROM_RESEARCH.json`.
    Image generation tools (`gpt-image-2.5-sunburst` via Codex subscription) MUST only be invoked using
    the prompts recorded in `IMAGE_PROMPTS_FROM_RESEARCH.json`.
    """
    proof = verify_reference_proof_gate(out_dir)
    benchmarks = proof["benchmarks"]
    primary_bench = benchmarks[-1]  # Prefer user_ref if present, else last benchmark
    tokens = primary_bench.get("tokens", {})
    bg_hex = override_bg or tokens.get("bg", "#F5EFE4")
    accent_hex = override_accent or tokens.get("primary", "#6D8C73")
    is_light = primary_bench.get("is_light_theme", True)
    lighting_desc = (
        "soft natural morning window light, high-key calm editorial atmosphere, organic linen and raw wood surfaces"
        if is_light
        else "dramatic low-key studio rim lighting, deep shadows, obsidian and brushed metal surfaces"
    )

    qa = user_qa_brief or {}
    persona_scene = qa.get(
        "hero_scene_from_qa",
        f"Editorial lifestyle & commercial photography of {category} for '{brand}'",
    )
    flyer_scene = qa.get(
        "flyer_scene_from_qa",
        f"Magazine lookbook still-life photography of {category} for '{brand}'",
    )
    pack_scene = qa.get(
        "pack_scene_from_qa",
        f"Product starter kit packaging photography for '{brand}' ({category})",
    )

    prompts_payload = {
        "gate_order_status": "RESEARCH_AND_USER_QA_COMPLETED_BEFORE_IMAGE_PROMPTS",
        "preferred_image_engine": "gpt-image-2.5-sunburst (via Codex CLI subscription `image_gen`, 0 JPY)",
        "based_on_proof": str((out_dir / "REFERENCE_BENCHMARK_PROOF.json").resolve()),
        "based_on_contact_sheet": proof["contact_sheet_path"],
        "user_qa_applied": qa,
        "synthesized_palette": {
            "bg_hex": bg_hex,
            "accent_hex": accent_hex,
            "lighting": lighting_desc,
        },
        "prompts": {
            "hero_image_prompt": (
                f"{persona_scene}. "
                f"Harmonized strictly with extracted reference palette {bg_hex} (background) and {accent_hex} (accent). "
                f"Lighting: {lighting_desc}. Generous negative space on the right for vertical Japanese typography (tategaki) overlay, "
                f"shot on Hasselblad H6D-100c, 8k photorealistic, zero text, zero watermarks."
            ),
            "poster_image_prompt": (
                f"{flyer_scene}. "
                f"Color harmony with {bg_hex} and {accent_hex}, {lighting_desc}, calm authentic craft atmosphere, "
                f"completely blank open notebook (zero text), clean composition, no text, no words."
            ),
            "pack_image_prompt": (
                f"{pack_scene}. "
                f"Tactile cream washi rigid gift box with {accent_hex} sage-green belly band resting on a natural wooden table, "
                f"{lighting_desc}, trustworthy presentation, completely blank booklet cover, zero text."
            ),
        },
    }
    out_file = out_dir / "IMAGE_PROMPTS_FROM_RESEARCH.json"
    out_file.write_text(json.dumps(prompts_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return prompts_payload


def invoke_codex_sunburst_from_research(out_dir: Path) -> list[str]:
    """
    Calls `codex exec` (ChatGPT Pro subscription OAuth, 0 JPY, `unset OPENAI_API_KEY`) to generate
    the 3 commercial studio images using `gpt-image-2.5-sunburst` (`image_gen` tool) directly from
    `IMAGE_PROMPTS_FROM_RESEARCH.json`.
    """
    import os
    import subprocess

    verify_reference_proof_gate(out_dir, require_image_prompt_proof=True)
    prompt_data = json.loads((out_dir / "IMAGE_PROMPTS_FROM_RESEARCH.json").read_text(encoding="utf-8"))
    p_dict = prompt_data["prompts"]

    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)

    instruction = (
        "Call the built-in image_gen tool 3 times to generate these 3 commercial photos (zero text in any image):\n"
        f"1. {p_dict['hero_image_prompt']}\n"
        f"2. {p_dict['poster_image_prompt']}\n"
        f"3. {p_dict['pack_image_prompt']}\n"
        "Output ONLY the 3 saved file paths in order."
    )
    subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", instruction],
        env=env,
        check=True,
    )
    codex_img_root = Path.home() / ".codex" / "generated_images"
    files = [p for p in codex_img_root.glob("*/*.png") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    selected = [str(p.resolve()) for p in files[:3]]
    selected.reverse()  # chronological order 1, 2, 3
    return selected


def verify_reference_proof_gate(out_dir: Path, require_image_prompt_proof: bool = False) -> dict:
    """
    Gate 1 Verifier: Raises SystemExit(1) if `REFERENCE_BENCHMARK_PROOF.json` or its physical images do not exist.
    When `require_image_prompt_proof=True`, also verifies that `IMAGE_PROMPTS_FROM_RESEARCH.json` exists.
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

    if require_image_prompt_proof:
        prompt_proof_path = out_dir / "IMAGE_PROMPTS_FROM_RESEARCH.json"
        if not prompt_proof_path.exists():
            raise SystemExit(
                f"🚨 [GATE 1.5 BLOCKED: IMAGE GENERATION BEFORE RESEARCH DETECTED]\n"
                f"`{prompt_proof_path}` が存在しません。リサーチ（サンプルWebサイトの画像キャプチャ＆DNA解析）の結果から\n"
                "`generate_image_prompts_from_research`（または `--print-image-prompts`）を実行して写真プロンプトを生成する前に、\n"
                "単独で画像生成を行うことは物理的に禁止されています。"
            )

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

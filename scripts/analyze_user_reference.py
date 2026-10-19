#!/usr/bin/env python3
"""
User Design Reference Analyzer & Agent Visual Brief Advisor
(TokenZero Deterministic Color + Taste/Archetype + Typography + Layout Geometry Extractor)

1. Accepts a user-provided reference image (--ref-image) or live URL (--ref-url).
2. Deterministically extracts:
   - Dominant color palette (bg, surface, primary, accent, text)
   - Design Taste / Archetype (`organic_editorial`, `japanese_luxury`, `bento_glass`, `neo_brutalism`, `swiss_editorial`, `cyber_pop`)
   - Frame geometry (`arch`, `bento_round`, `sharp_grid`, `brutal_box`), typography stack (Serif vs Sans vs Mono), and border/shadow tokens
   - From live URLs (--ref-url): also inspects actual DOM `getComputedStyle` (font-family, border-radius, backdrop-filter, border-width)!
3. Outputs an "Agent Visual Request Card" telling the user (or image generator) what photos are needed.
"""

from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path
from PIL import Image, ImageFilter, ImageStat


STYLE_ARCHETYPE_PRESETS: dict[str, dict] = {
    "organic_editorial": {
        "taste_label": "Organic Editorial（雑誌エディトリアル・アーチ窓・自然派ラグジュアリー）",
        "font_heading": "'Cormorant Garamond', 'Hiragino Mincho ProN', 'Yu Mincho', serif",
        "font_body": "'Hiragino Mincho ProN', 'Noto Serif JP', serif",
        "frame_shape": "arch",  # 999px top arch + polaroid overlap
        "is_organic": True,
    },
    "japanese_luxury": {
        "taste_label": "Minimal Luxury / Dark Atelier（重厚アトリエ・箔押し・和モダン明朝）",
        "font_heading": "'Shippori Mincho', 'Cormorant Garamond', 'Hiragino Mincho ProN', serif",
        "font_body": "'Noto Serif JP', 'Hiragino Mincho ProN', serif",
        "frame_shape": "editorial_rect",
        "is_organic": True,
    },
    "bento_glass": {
        "taste_label": "Bento Glassmorphism（Apple風ベントーグリッド・すりガラス・モダンUI）",
        "font_heading": "'Plus Jakarta Sans', 'Inter', 'Hiragino Sans', sans-serif",
        "font_body": "'Inter', 'Hiragino Sans', 'Noto Sans JP', sans-serif",
        "frame_shape": "bento_round",
        "is_organic": False,
    },
    "neo_brutalism": {
        "taste_label": "Neo-Brutalism / Street Pop（極太枠線・ハードシャドウ・高彩度ストリート）",
        "font_heading": "'Space Grotesk', 'Arial Black', 'Hiragino Kaku Gothic StdN', sans-serif",
        "font_body": "'Inter', 'Hiragino Kaku Gothic ProN', sans-serif",
        "frame_shape": "brutal_box",
        "is_organic": False,
    },
    "swiss_editorial": {
        "taste_label": "Swiss International Grid（スイス・タイポグラフィ・厳格モジュラーグリッド）",
        "font_heading": "'Helvetica Neue', 'Inter', 'Arial', sans-serif",
        "font_body": "'Inter', 'Helvetica Neue', 'Hiragino Sans', sans-serif",
        "frame_shape": "sharp_grid",
        "is_organic": False,
    },
    "cyber_pop": {
        "taste_label": "Cyber Pop / Y2K Neon（ネオングロー・ダーククローム・近未来テック）",
        "font_heading": "'Syne', 'Space Grotesk', 'Impact', sans-serif",
        "font_body": "'Space Grotesk', 'Hiragino Sans', sans-serif",
        "frame_shape": "bento_round",
        "is_organic": False,
    },
}


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def luminance(rgb: tuple[int, int, int]) -> float:
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255.0


def classify_taste_from_metrics(
    is_light_theme: bool,
    max_sat: float,
    accent_hue_deg: float,
    edge_density: float,
    dom_hints: dict | None = None,
) -> str:
    """
    Deterministically classifies the design taste/archetype from image color/edge statistics
    and optional live DOM computed style hints.
    """
    if dom_hints:
        if dom_hints.get("has_backdrop_blur"):
            return "bento_glass"
        if dom_hints.get("max_border_width", 0) >= 2.5:
            return "neo_brutalism"
        if dom_hints.get("is_serif"):
            return "organic_editorial" if is_light_theme else "japanese_luxury"
        if dom_hints.get("avg_border_radius", 0) >= 16:
            return "bento_glass"
        if not dom_hints.get("is_serif") and dom_hints.get("avg_border_radius", 0) <= 4:
            return "swiss_editorial"

    # Image-based deterministic classification
    if not is_light_theme:
        if max_sat >= 0.65:
            return "cyber_pop"
        # Cool blue/indigo/violet tech dark theme -> bento_glass
        if 190 <= accent_hue_deg <= 290 and max_sat >= 0.30:
            return "bento_glass"
        return "japanese_luxury"
    else:
        # Light theme classification
        if max_sat >= 0.68 and edge_density >= 0.12:
            return "neo_brutalism"
        if max_sat <= 0.16:
            return "swiss_editorial"
        if 195 <= accent_hue_deg <= 265 and max_sat >= 0.42 and edge_density < 0.12:
            return "bento_glass"
        return "organic_editorial"


def build_tokens_for_taste(
    taste_key: str,
    source_label: str,
    bg_rgb: tuple[int, int, int],
    surface_rgb: tuple[int, int, int],
    best_accent: tuple[int, int, int],
    second_accent: tuple[int, int, int],
    is_light_theme: bool,
) -> dict:
    preset = STYLE_ARCHETYPE_PRESETS.get(taste_key, STYLE_ARCHETYPE_PRESETS["organic_editorial"])
    bg_hex = rgb_to_hex(bg_rgb)
    surface_hex = rgb_to_hex(surface_rgb)
    primary_hex = rgb_to_hex(best_accent)
    accent_hex = rgb_to_hex(second_accent)
    text_hex = "#1C1A17" if is_light_theme else "#F5F3EF"
    muted_hex = "#6E685F" if is_light_theme else "#9CA3AF"

    if taste_key == "neo_brutalism":
        border_style = f"3px solid {text_hex}"
        shadow = f"8px 8px 0px {text_hex}"
    elif taste_key == "bento_glass":
        border_style = "1px solid rgba(255, 255, 255, 0.22)" if not is_light_theme else f"1px solid {primary_hex}33"
        shadow = "0 20px 50px rgba(0, 0, 0, 0.25)"
    elif taste_key == "swiss_editorial":
        border_style = f"1.5px solid {text_hex}"
        shadow = "none"
    elif taste_key == "cyber_pop":
        border_style = f"1px solid {primary_hex}"
        shadow = f"0 0 28px {primary_hex}55"
    else:
        border_style = f"1px solid {primary_hex}44"
        shadow = "0 20px 48px rgba(28, 26, 23, 0.12)" if is_light_theme else "0 24px 60px rgba(0, 0, 0, 0.65)"

    return {
        "label": f"{preset['taste_label']} [{source_label}]",
        "taste_key": taste_key,
        "frame_shape": preset["frame_shape"],
        "bg": bg_hex,
        "surface": surface_hex,
        "primary": primary_hex,
        "accent": accent_hex,
        "text": text_hex,
        "muted": muted_hex,
        "font_heading": preset["font_heading"],
        "font_body": preset["font_body"],
        "border_style": border_style,
        "shadow": shadow,
        "is_organic": preset["is_organic"],
    }


def extract_dna_from_image(img_path: Path, dom_hints: dict | None = None) -> dict:
    """Deterministically extract color palette, brightness mood, edge sharpness, and design taste from an image."""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    small = img.resize((120, 120))
    quantized = small.quantize(colors=8, method=Image.Quantize.MEDIANCUT).convert("RGB")

    # Compute edge density (high frequency structural lines vs soft gradients)
    edges = small.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_density = round(ImageStat.Stat(edges).mean[0] / 255.0, 3)

    counts: dict[tuple[int, int, int], int] = {}
    for px in quantized.getdata():
        counts[px] = counts.get(px, 0) + 1

    sorted_colors = [c for c, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)]
    bg_rgb = sorted_colors[0]
    bg_lum = luminance(bg_rgb)
    is_light_theme = bg_lum >= 0.52

    best_accent = sorted_colors[min(1, len(sorted_colors) - 1)]
    best_score = -1.0
    max_sat = 0.0
    accent_hue_deg = 35.0

    for c in sorted_colors[1:]:
        r, g, b = c[0] / 255.0, c[1] / 255.0, c[2] / 255.0
        hue, l, s = colorsys.rgb_to_hls(r, g, b)
        if s > max_sat:
            max_sat = s
        contrast = abs(luminance(c) - bg_lum)
        score = (s * 1.4) + contrast
        if 0.12 < l < 0.90 and score > best_score:
            best_score = score
            best_accent = c
            accent_hue_deg = hue * 360.0

    surface_rgb = (
        tuple(max(0, min(255, int(v * 0.94))) for v in bg_rgb)
        if is_light_theme
        else tuple(max(0, min(255, int(v * 1.35 + 12))) for v in bg_rgb)
    )
    second_accent = sorted_colors[min(2, len(sorted_colors) - 1)]

    taste_key = classify_taste_from_metrics(
        is_light_theme=is_light_theme,
        max_sat=max_sat,
        accent_hue_deg=accent_hue_deg,
        edge_density=edge_density,
        dom_hints=dom_hints,
    )
    tokens = build_tokens_for_taste(
        taste_key=taste_key,
        source_label=img_path.name,
        bg_rgb=bg_rgb,
        surface_rgb=surface_rgb,
        best_accent=best_accent,
        second_accent=second_accent,
        is_light_theme=is_light_theme,
    )

    return {
        "source_type": "image",
        "source_path": str(img_path.resolve()),
        "dimensions": {"width": w, "height": h, "aspect_ratio": round(w / max(1, h), 3)},
        "detected_taste": taste_key,
        "taste_label": STYLE_ARCHETYPE_PRESETS[taste_key]["taste_label"],
        "mood": STYLE_ARCHETYPE_PRESETS[taste_key]["taste_label"],
        "is_light_theme": is_light_theme,
        "metrics": {
            "bg_luminance": round(bg_lum, 3),
            "max_saturation": round(max_sat, 3),
            "accent_hue_deg": round(accent_hue_deg, 1),
            "edge_density": edge_density,
        },
        "recommended_layout": taste_key,
        "tokens": tokens,
        "extracted_palette_hex": [rgb_to_hex(c) for c in sorted_colors[:6]],
    }


def extract_dna_from_url(url: str, out_dir: Path) -> dict:
    """Capture screenshot AND DOM computed style hints (fonts, radius, blur, borders) of a reference URL via Playwright."""
    from playwright.sync_api import sync_playwright

    shot_path = out_dir / "user_url_reference_capture.png"
    dom_hints: dict = {}
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=2)
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(500)
        dom_hints = page.evaluate(
            """() => {
                const els = Array.from(document.querySelectorAll('h1, h2, section, div, button, a')).slice(0, 60);
                let serifCount = 0;
                let sansCount = 0;
                let maxBorder = 0;
                let radii = [];
                let hasBlur = false;
                for (const el of els) {
                    const st = window.getComputedStyle(el);
                    const ff = (st.fontFamily || '').toLowerCase();
                    if (ff.includes('serif') && !ff.includes('sans-serif')) serifCount++;
                    if (ff.includes('sans')) sansCount++;
                    const bw = parseFloat(st.borderTopWidth || '0') || 0;
                    if (bw > maxBorder) maxBorder = bw;
                    const br = parseFloat(st.borderTopLeftRadius || '0') || 0;
                    if (br > 0 && br < 500) radii.push(br);
                    if ((st.backdropFilter || '').includes('blur') || (st.webkitBackdropFilter || '').includes('blur')) {
                        hasBlur = true;
                    }
                }
                const avgRadius = radii.length ? radii.reduce((a,b)=>a+b,0)/radii.length : 0;
                return {
                    is_serif: serifCount > sansCount * 0.4,
                    max_border_width: maxBorder,
                    avg_border_radius: Math.round(avgRadius * 10) / 10,
                    has_backdrop_blur: hasBlur
                };
            }"""
        )
        page.screenshot(path=str(shot_path))
        browser.close()

    dna = extract_dna_from_image(shot_path, dom_hints=dom_hints)
    dna["source_type"] = "url"
    dna["source_url"] = url
    dna["dom_style_hints"] = dom_hints
    return dna


def build_missing_asset_recommendations(
    dna: dict,
    brand: str,
    category: str,
    has_hero: bool,
    has_poster: bool,
    has_pack: bool,
) -> list[dict]:
    """Generate actionable advice telling the user what visual assets are needed to match their reference."""
    mood = dna["mood"]
    bg_hex = dna["tokens"]["bg"]
    accent_hex = dna["tokens"]["primary"]
    lighting = (
        "柔らかな自然光・リネンや生成り和紙の明るい背景（ハイキー・ソフトシャドウ）"
        if dna["is_light_theme"]
        else "黒曜石やダークシルク背景にアクセントカラーのリムライトが当たる陰影の強いスタジオ照明（ローキー）"
    )

    reqs = []
    if not has_hero:
        reqs.append(
            {
                "slot": "--hero-image (Webサイト メインビジュアル用)",
                "status": "未指定（追加推奨）",
                "required_spec": "縦長または正方形（推奨 1200×1500px 以上）・文字なしの写真",
                "what_to_prepare": f"【{category}のメイン商品マクロ写真】抽出されたテイスト「{mood}」と配色（{bg_hex} / {accent_hex}）に馴染むよう、{lighting}で撮影・生成された商品のクローズアップ写真。",
                "ready_to_use_ai_prompt": f"Macro editorial photography of {category} for '{brand}', {mood} aesthetic, color harmony with {bg_hex} and {accent_hex}, high-end commercial studio shot, no text, 8k",
            }
        )
    if not has_poster:
        reqs.append(
            {
                "slot": "--poster-image (ポスター＆Webサブビジュアル用)",
                "status": "未指定（追加推奨）",
                "required_spec": "A判縦比率または4:5（推奨 1600×2000px 以上）・余白のある構図",
                "what_to_prepare": "【世界観・着用イメージまたは光の情景写真】商品のディテールや空気感が伝わる引きの構図、または光と影のコントラストが美しいイメージカット。",
                "ready_to_use_ai_prompt": f"High-fashion editorial still life of {category}, {mood}, matching palette {bg_hex} and {accent_hex}, magazine lookbook quality, no text",
            }
        )
    if not has_pack:
        reqs.append(
            {
                "slot": "--pack-image (パッケージ3Dプレゼンボード用)",
                "status": "未指定（追加推奨）",
                "required_spec": "正方形〜4:5（推奨 1400×1400px 以上）",
                "what_to_prepare": f"【外箱・ショッパー・専用台紙の物撮り写真】{bg_hex}調のパッケージと商品を留める専用台紙が並んだスタジオ写真。",
                "ready_to_use_ai_prompt": f"Luxury product packaging photography for '{brand}' ({category}), tactile box and display card in {bg_hex} with {accent_hex} accents, {mood}, no text",
            }
        )
    return reqs


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze user reference design and advise required images")
    parser.add_argument("--ref-image", default="", help="Path to user's reference design / moodboard image")
    parser.add_argument("--ref-url", default="", help="URL of a website the user wants to use as design reference")
    parser.add_argument("--brand", default="LUMIÈRE & CO.")
    parser.add_argument("--category", default="18Kゴールド＆あこや真珠イヤリング・アクセサリー")
    parser.add_argument("--hero-image", default="")
    parser.add_argument("--poster-image", default="")
    parser.add_argument("--pack-image", default="")
    parser.add_argument("--out-dna", default="/tmp/USER_CUSTOM_DNA.json")
    args = parser.parse_args()

    out_path = Path(args.out_dna).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.ref_image:
        dna = extract_dna_from_image(Path(args.ref_image).expanduser().resolve())
    elif args.ref_url:
        dna = extract_dna_from_url(args.ref_url, out_path.parent)
    else:
        raise SystemExit("エラー: --ref-image または --ref-url のいずれかを指定してください。")

    missing = build_missing_asset_recommendations(
        dna,
        args.brand,
        args.category,
        bool(args.hero_image),
        bool(args.poster_image),
        bool(args.pack_image),
    )
    dna["missing_asset_requests"] = missing
    out_path.write_text(json.dumps(dna, ensure_ascii=False, indent=2), encoding="utf-8")

    t = dna["tokens"]
    print(f"=== 🔍 [User Design Reference Analyzed] 抽出完了 ===")
    print(f"・参照元          : {dna.get('source_path') or dna.get('source_url')}")
    print(f"・自動判定テイスト: {dna['taste_label']} (key={dna['detected_taste']})")
    print(f"・抽出パレット    : 背景 {t['bg']} / サーフェス {t['surface']} / アクセント {t['primary']} / 文字 {t['text']}")
    print(f"・フォント＆枠形状: 見出し={t['font_heading'].split(',')[0]} / 形状={t['frame_shape']}")
    print(f"・出力DNAファイル : {out_path}")

    if missing:
        print("\n📋 【エージェントからの素材リクエスト（このデザインを最高品質で再現するために必要な画像）】")
        for idx, m in enumerate(missing, 1):
            print(f"  {idx}. {m['slot']} [{m['status']}]")
            print(f"     - 必要なイメージ: {m['what_to_prepare']}")
            print(f"     - 推奨サイズ仕様: {m['required_spec']}")
            print(f"     - AI自動生成用プロンプト: \"{m['ready_to_use_ai_prompt']}\"")
    else:
        print("\n✅ 必要な3つのビジュアル素材（Hero / Poster / Packaging）はすべて揃っています。")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Omni-Design Studio: Website, Poster (300DPI PNG/PDF), and Packaging (3D Mockup & Die-line SVG) Generator.
Supports strictly Plan A (Gemini 4 Argon + Imagen 4 + Playwright/SVG = 0 JPY)
and Plan B (DeepSeek V4.1-Flash + Flux Schnell = ~0.6 JPY/asset).
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

TREND_TOKENS = {
    "japanese_luxury": {
        "label": "和モダン・ミニマルラグジュアリー (Japanese Luxury)",
        "bg": "#0c0d0e",
        "surface": "#16181a",
        "primary": "#d4af37",
        "accent": "#8c7335",
        "text": "#f4f1ea",
        "muted": "#9ca3af",
        "font_heading": "'Noto Serif JP', 'Hiragino Mincho ProN', 'Yu Mincho', serif",
        "font_body": "'Noto Sans JP', 'Hiragino Sans', sans-serif",
        "border_style": "1px solid rgba(212, 175, 55, 0.35)",
        "shadow": "0 24px 60px rgba(0, 0, 0, 0.65)",
    },
    "neo_brutalism": {
        "label": "ネオ・ブルータリズム (Neo-Brutalism 2026)",
        "bg": "#f4f0ea",
        "surface": "#ffffff",
        "primary": "#ff3b00",
        "accent": "#111111",
        "text": "#111111",
        "muted": "#4b5563",
        "font_heading": "'Arial Black', 'Hiragino Kaku Gothic StdN', sans-serif",
        "font_body": "'Hiragino Sans', 'Noto Sans JP', sans-serif",
        "border_style": "4px solid #111111",
        "shadow": "10px 10px 0px #111111",
    },
    "bento_glass": {
        "label": "Apple風ベントー＆グラスモーフィズム (Bento Glass)",
        "bg": "#060913",
        "surface": "rgba(255, 255, 255, 0.06)",
        "primary": "#38bdf8",
        "accent": "#818cf8",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "font_heading": "'SF Pro Display', 'Hiragino Sans', sans-serif",
        "font_body": "'SF Pro Text', 'Hiragino Sans', sans-serif",
        "border_style": "1px solid rgba(255, 255, 255, 0.14)",
        "shadow": "0 20px 50px rgba(15, 23, 42, 0.8)",
    },
    "swiss_editorial": {
        "label": "スイス・インターナショナル・タイポグラフィ (Swiss Grid)",
        "bg": "#e5e5e0",
        "surface": "#f5f5f2",
        "primary": "#e11d48",
        "accent": "#18181b",
        "text": "#18181b",
        "muted": "#52525b",
        "font_heading": "'Helvetica Neue', 'Hiragino Kaku Gothic ProN', sans-serif",
        "font_body": "'Helvetica Neue', 'Hiragino Sans', sans-serif",
        "border_style": "2px solid #18181b",
        "shadow": "none",
    },
    "cyber_pop": {
        "label": "サイバーポップ・ネオンホログラム (Y2K / Cyber Pop)",
        "bg": "#090414",
        "surface": "#15092b",
        "primary": "#f43f5e",
        "accent": "#22d3ee",
        "text": "#ffffff",
        "muted": "#cbd5e1",
        "font_heading": "'Impact', 'Hiragino Kaku Gothic StdN', sans-serif",
        "font_body": "'Hiragino Sans', sans-serif",
        "border_style": "2px solid #22d3ee",
        "shadow": "0 0 35px rgba(34, 211, 238, 0.45)",
    },
    "organic_editorial": {
        "label": "有機的アーチ×非対称マガジン構成 (Human Designer DNA #REF-014)",
        "bg": "#F6F3EC",
        "surface": "#EFECE4",
        "primary": "#9E7B4F",
        "accent": "#7A6A53",
        "text": "#1C1A17",
        "muted": "#6E685F",
        "font_heading": "'Cormorant Garamond', 'Hiragino Mincho ProN', 'Yu Mincho', serif",
        "font_body": "'Hiragino Mincho ProN', 'Noto Serif JP', serif",
        "border_style": "1px solid rgba(28, 26, 23, 0.14)",
        "shadow": "0 18px 40px rgba(28, 26, 23, 0.08)",
        "is_organic": True,
    },
}


def _img_uri(path_str: str) -> str:
    if not path_str:
        return ""
    p = Path(path_str).expanduser().resolve()
    return p.as_uri() if p.exists() else ""


def build_website_html(t: dict, brand: str, headline: str, subcopy: str, hero_img: str = "", sub_img: str = "") -> str:
    b, h, s = html.escape(brand), html.escape(headline), html.escape(subcopy)
    img_uri = _img_uri(hero_img)
    sub_uri = _img_uri(sub_img) or img_uri

    if t.get("is_organic"):
        is_genmai = ("玄米" in brand) or ("養生" in brand) or ("玄米" in subcopy)
        rail_label = "WATASHI YOUJO — HOLISTIC JOURNAL" if is_genmai else "ATELIER JOURNAL — AUTUMN / WINTER"
        nav_html = (
            "<span>ABOUT</span><span>8-DAY / 16-DAY PLAN</span><span>7-ITEM KIT</span><span>SUPERVISOR</span><span>LINE CONSULT</span>"
            if is_genmai
            else "<span>COLLECTION</span><span>PHILOSOPHY</span><span>BESPOKE</span><span>OMOTESANDO ATELIER</span><span>CART (0)</span>"
        )
        issue_text = "WATASHI YOUJO — 酵素玄米 × 東洋医学 内外同治プログラム" if is_genmai else "No. 14 — Goutte de Lumière Collection"
        watermark_text = "Watashi Youjo" if is_genmai else "Poetic Craft"
        cta_text = "プログラム詳細・LINE無料相談へ" if is_genmai else "EXPLORE THE LOOKBOOK"
        index_rows_html = (
            """        <div class="index-row">
          <span class="idx-num">i.</span>
          <div><span class="idx-title">8日間 ハーフプログラム（入門）</span><span class="idx-sub">熟成酵素玄米24食＋甘酒2種＋五種茶＋岩塩＋黒ごま＋お灸12個＋LINE伴走</span></div>
          <span class="idx-price">¥33,000</span>
        </div>
        <div class="index-row">
          <span class="idx-num">ii.</span>
          <div><span class="idx-title">16日間 フルプログラム（本格養生）</span><span class="idx-sub">熟成酵素玄米48食＋養生7点セット＋朝晩LINE伴走（税込・送料込）</span></div>
          <span class="idx-price">¥55,000</span>
        </div>
        <div class="index-row">
          <span class="idx-num">iii.</span>
          <div><span class="idx-title">特約店・サロン導入パートナー制度</span><span class="idx-sub">在庫リスク0（メーカー直送）・粗利率40%・フォロー文面完備</span></div>
          <span class="idx-price">Partner</span>
        </div>"""
            if is_genmai
            else """        <div class="index-row">
          <span class="idx-num">i.</span>
          <div><span class="idx-title">朝露のアコヤ真珠フープ</span><span class="idx-sub">K18YG / Akoya Pearl 6.5mm</span></div>
          <span class="idx-price">¥16,500</span>
        </div>
        <div class="index-row">
          <span class="idx-num">ii.</span>
          <div><span class="idx-title">水面の有機的イヤーカフ</span><span class="idx-sub">SV925 + K18 Vermeil</span></div>
          <span class="idx-price">¥14,800</span>
        </div>
        <div class="index-row">
          <span class="idx-num">iii.</span>
          <div><span class="idx-title">金箔押しコットン貼り箱ギフト</span><span class="idx-sub">Bespoke Velvet Box</span></div>
          <span class="idx-price">Included</span>
        </div>"""
        )
        inset_caption = "Fig 02. 鍼灸師 原まゆこ監修（施術歴31年・延べ2万人）" if is_genmai else "Fig 02. Morning refraction"
        tategaki_html = (
            "何かを足す健康法から、<br>余分なものを手放す十六日間へ。<br>内側から整う、ワタシ養生。"
            if is_genmai
            else "光と影が交差する瞬間に、<br>職人の手仕事で宿る有機的な曲線。<br>装う人の呼吸に寄り添う一滴。"
        )
        seal_html = (
            '<span>SUPERVISED</span><strong style="font-size:11px; margin:2px 0;">鍼灸 cocon</strong><span>EST. 31 YRS</span>'
            if is_genmai
            else '<span>HANDCRAFTED</span><strong style="font-size:12px; margin:2px 0;">TOKYO</strong><span>EST. 2026</span>'
        )
        # Bespoke Human-Designed Editorial Layout (Dynamically adapts to extracted User Reference DNA)
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{b} — Official Holistic Journal</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: {t['bg']};
    color: {t['text']};
    font-family: 'Hiragino Mincho ProN', 'Yu Mincho', 'Noto Serif JP', serif;
    min-height: 100vh;
    position: relative;
    overflow: hidden;
  }}
  /* Subtle organic botanical shadow & linen paper grain */
  .paper-aura {{
    position: absolute; inset: 0; pointer-events: none;
    background:
      radial-gradient(ellipse at 18% 12%, {t['surface']} 0%, transparent 55%),
      radial-gradient(ellipse at 85% 82%, {t['primary']}1A 0%, transparent 60%);
  }}
  /* Left rail micro-navigation (Human designer editorial signature) */
  .left-rail {{
    position: absolute; left: 34px; top: 44px; bottom: 44px; width: 28px;
    border-right: {t['border_style']};
    display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    padding-right: 14px; font-family: 'Georgia', serif; font-size: 10px; letter-spacing: 0.28em; color: {t['muted']};
  }}
  .rail-vertical {{ writing-mode: vertical-rl; text-orientation: mixed; }}
  /* Top minimalist header */
  header {{
    margin-left: 88px; margin-right: 56px; padding-top: 38px; padding-bottom: 20px;
    display: flex; justify-content: space-between; align-items: baseline;
    border-bottom: {t['border_style']};
  }}
  .brand-logo {{
    font-family: 'Didot', 'Bodoni MT', 'Hiragino Mincho ProN', serif;
    font-size: 22px; letter-spacing: 0.28em; font-weight: 400; color: {t['text']};
  }}
  .nav-links {{
    display: flex; gap: 42px; font-size: 11px; letter-spacing: 0.22em; color: {t['muted']};
    font-family: 'Helvetica Neue', sans-serif;
  }}
  /* Asymmetric 3-zone editorial stage (NO generic equal boxes!) */
  .editorial-stage {{
    margin-left: 88px; margin-right: 56px; margin-top: 36px;
    display: grid; grid-template-columns: 0.92fr 1.18fr 0.55fr; gap: 36px;
    align-items: start; position: relative;
  }}
  .col-story {{ padding-top: 28px; padding-right: 12px; position: relative; z-index: 3; }}
  .issue-no {{
    font-family: 'Georgia', serif; font-style: italic; font-size: 14px; color: {t['primary']};
    letter-spacing: 0.12em; margin-bottom: 18px; display: block;
  }}
  .en-Watermark {{
    font-family: 'Didot', 'Georgia', serif; font-style: italic; font-weight: 400;
    font-size: 64px; line-height: 0.95; color: {t['primary']}38;
    margin-bottom: -18px; margin-left: -4px; user-select: none;
  }}
  h1 {{
    font-size: 38px; font-weight: 400; line-height: 1.48; letter-spacing: 0.06em;
    color: {t['text']}; margin-bottom: 26px;
  }}
  .lead {{
    font-size: 14px; line-height: 2.15; color: {t['muted']}; letter-spacing: 0.05em;
    margin-bottom: 34px; max-width: 390px;
  }}
  /* Organic oval link button instead of rectangular AI button */
  .oval-cta {{
    display: inline-flex; align-items: center; gap: 18px;
    padding: 15px 36px; border-radius: 999px;
    border: 1px solid {t['text']}; color: {t['text']}; text-decoration: none;
    font-size: 11px; letter-spacing: 0.24em; font-family: 'Helvetica Neue', sans-serif;
    background: {t['surface']};
  }}
  /* Editorial numbered index (replaces AI 3-card Bento grid) */
  .index-list {{
    margin-top: 46px; border-top: {t['border_style']};
  }}
  .index-row {{
    display: grid; grid-template-columns: 36px 1fr auto; align-items: baseline;
    padding: 15px 0; border-bottom: {t['border_style']};
  }}
  .idx-num {{ font-family: 'Georgia', serif; font-style: italic; font-size: 13px; color: {t['primary']}; }}
  .idx-title {{ font-size: 14px; letter-spacing: 0.08em; color: {t['text']}; }}
  .idx-sub {{ font-size: 11px; color: {t['muted']}; margin-left: 10px; }}
  .idx-price {{ font-family: 'Georgia', serif; font-size: 13px; color: {t['muted']}; letter-spacing: 0.06em; }}

  /* Center Arch Window + Overlapping Secondary Polaroid */
  .col-visual {{ position: relative; padding-left: 10px; }}
  .arch-frame {{
    width: 440px; height: 590px;
    border-radius: 220px 220px 4px 4px;
    overflow: hidden; position: relative;
    box-shadow: {t['shadow']};
    border: 1px solid {t['primary']}55;
  }}
  .arch-frame img {{ width: 100%; height: 100%; object-fit: cover; }}
  .floating-inset {{
    position: absolute; bottom: -26px; left: -54px;
    width: 195px; height: 235px; background: {t['surface']};
    padding: 12px 12px 34px 12px;
    box-shadow: {t['shadow']};
    border: {t['border_style']};
    transform: rotate(-2.5deg);
  }}
  .floating-inset img {{ width: 100%; height: 100%; object-fit: cover; }}
  .inset-caption {{
    position: absolute; bottom: 10px; left: 14px;
    font-family: 'Georgia', serif; font-style: italic; font-size: 10px; color: {t['muted']}; letter-spacing: 0.08em;
  }}

  /* Right Column: Traditional Japanese Vertical Tategaki Poetic Copy & Stamp */
  .col-tategaki {{
    display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between;
    height: 590px; padding-top: 12px;
  }}
  .tategaki-poem {{
    writing-mode: vertical-rl; text-orientation: upright;
    font-size: 15px; line-height: 2.3; letter-spacing: 0.24em; color: {t['text']};
    height: 390px; border-left: 1px solid {t['primary']}55; padding-left: 22px;
  }}
  .atelier-seal {{
    width: 104px; height: 104px; border-radius: 50%;
    border: 1px solid {t['primary']}88;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; font-family: 'Georgia', serif; font-size: 9px; letter-spacing: 0.16em;
    color: {t['primary']}; line-height: 1.5; background: {t['surface']};
  }}
</style>
</head>
<body>
  <div class="paper-aura"></div>
  <aside class="left-rail">
    <span>01</span>
    <span class="rail-vertical">{rail_label}</span>
    <span>26</span>
  </aside>
  <header>
    <div class="brand-logo">{b}</div>
    <nav class="nav-links">
      {nav_html}
    </nav>
  </header>
  <main class="editorial-stage">
    <div class="col-story">
      <span class="issue-no">{issue_text}</span>
      <div class="en-Watermark">{watermark_text}</div>
      <h1>{h}</h1>
      <p class="lead">{s}</p>
      <a href="#lookbook" class="oval-cta">
        <span>{cta_text}</span>
        <span style="font-size:15px;">⟶</span>
      </a>
      <div class="index-list">
{index_rows_html}
      </div>
    </div>
    <div class="col-visual">
      <div class="arch-frame">
        <img src="{img_uri}" alt="Hero Visual" />
      </div>
      <div class="floating-inset">
        <img src="{sub_uri}" alt="Detail Visual" />
        <span class="inset-caption">{inset_caption}</span>
      </div>
    </div>
    <div class="col-tategaki">
      <div class="tategaki-poem">
        {tategaki_html}
      </div>
      <div class="atelier-seal">
        {seal_html}
      </div>
    </div>
  </main>
</body>
</html>"""
    visual_inner = (
        f'<img src="{img_uri}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0;" />'
        f'<div style="position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.05) 50%, rgba(0,0,0,0.75) 100%); z-index:1;"></div>'
        if img_uri
        else f"""<div style="display:flex; justify-content:center; align-items:center; margin:auto; position:relative; z-index:2;">
        <svg width="240" height="240" viewBox="0 0 240 240" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="120" cy="120" r="96" stroke="{t['primary']}" stroke-width="1" stroke-dasharray="4 6" opacity="0.45"/>
          <circle cx="95" cy="110" r="46" stroke="{t['primary']}" stroke-width="3.5"/>
          <circle cx="145" cy="128" r="46" stroke="{t['primary']}" stroke-width="2" opacity="0.85"/>
          <circle cx="95" cy="166" r="14" fill="{t['text']}" stroke="{t['primary']}" stroke-width="2"/>
          <circle cx="145" cy="184" r="14" fill="{t['text']}" stroke="{t['primary']}" stroke-width="2"/>
        </svg>
      </div>"""
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{b} — Official Boutique</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: {t['bg']};
    color: {t['text']};
    font-family: {t['font_body']};
    min-height: 100vh;
    padding: 44px 64px;
    background-image: radial-gradient(circle at 80% 15%, {t['primary']}26 0%, transparent 45%),
                      radial-gradient(circle at 15% 85%, {t['accent']}22 0%, transparent 45%);
  }}
  header {{
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 22px; border-bottom: {t['border_style']};
  }}
  .brand {{ font-family: {t['font_heading']}; font-size: 24px; font-weight: 800; letter-spacing: 0.22em; color: {t['primary']}; }}
  .nav {{ display: flex; gap: 36px; font-size: 13px; color: {t['muted']}; letter-spacing: 0.14em; }}
  .hero {{
    display: grid; grid-template-columns: 1.15fr 1.05fr; gap: 52px;
    margin-top: 48px; align-items: center;
  }}
  .badge {{
    display: inline-block; padding: 6px 18px; border: {t['border_style']};
    color: {t['primary']}; font-size: 11px; letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 24px;
  }}
  h1 {{
    font-family: {t['font_heading']}; font-size: 50px; line-height: 1.25;
    margin-bottom: 24px; letter-spacing: 0.02em;
  }}
  .subcopy {{ font-size: 16.5px; line-height: 1.85; color: {t['muted']}; margin-bottom: 36px; }}
  .cta {{
    display: inline-block; padding: 18px 44px; background: {t['primary']}; color: {t['bg']};
    font-weight: 800; font-size: 13px; letter-spacing: 0.18em; text-decoration: none; border: {t['border_style']};
    box-shadow: {t['shadow']};
  }}
  .bento-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 48px;
  }}
  .card {{
    background: {t['surface']}; border: {t['border_style']}; padding: 28px;
    box-shadow: {t['shadow']}; backdrop-filter: blur(20px);
  }}
  .card-tag {{ font-size: 11px; letter-spacing: 0.2em; color: {t['primary']}; margin-bottom: 8px; }}
  .card h3 {{ font-family: {t['font_heading']}; font-size: 20px; color: {t['text']}; margin-bottom: 10px; }}
  .card p {{ font-size: 13.5px; line-height: 1.75; color: {t['muted']}; }}
  .price {{ margin-top: 14px; font-family: {t['font_heading']}; font-size: 16px; color: {t['primary']}; letter-spacing: 0.08em; }}
  .visual-box {{
    height: 460px; background: linear-gradient(145deg, {t['surface']}, {t['bg']});
    border: {t['border_style']}; box-shadow: {t['shadow']};
    display: flex; flex-direction: column; justify-content: space-between; padding: 32px;
    position: relative; overflow: hidden;
  }}
</style>
</head>
<body>
  <header>
    <div class="brand">{b}</div>
    <div class="nav"><span>EARRINGS</span><span>RINGS &amp; CUFFS</span><span>BRIDAL</span><span>ATELIER</span><span>ONLINE BOUTIQUE</span></div>
  </header>
  <section class="hero">
    <div>
      <span class="badge">2026 NEW SEASON COLLECTION</span>
      <h1>{h}</h1>
      <p class="subcopy">{s}</p>
      <a href="#collection" class="cta">VIEW COLLECTION — ONLINE STORE →</a>
    </div>
    <div class="visual-box">
      {visual_inner}
      <div style="position:relative; z-index:2; display:flex; justify-content:space-between; font-size:11px; letter-spacing:0.2em; color:#f8fafc; text-shadow:0 2px 8px rgba(0,0,0,0.8);">
        <span>DESIGNED IN TOKYO</span><span>NEW ARRIVALS 2026</span>
      </div>
      <div style="position:relative; z-index:2; text-shadow:0 2px 12px rgba(0,0,0,0.9);">
        <div style="font-size:11px; letter-spacing:0.22em; color:#ffffff; background:{t['primary']}; display:inline-block; padding:3px 10px; margin-bottom:6px;">SIGNATURE COLLECTION</div>
        <div style="font-family:{t['font_heading']}; font-size:24px; font-weight:700; color:#ffffff;">{b} — Daily Favorites</div>
      </div>
    </div>
  </section>
  <section class="bento-grid">
    <div class="card">
      <div class="card-tag">01 / CHUNKY RESIN RING</div>
      <h3>Candy Drop Resin Ring</h3>
      <p>キャンディのような透明感のカラーレジンリング。水や汗に強く、1本でも重ね付けでも指先がパッと華やぐ軽量設計。</p>
      <div class="price">¥2,400 (tax in)</div>
    </div>
    <div class="card">
      <div class="card-tag">02 / HAIR CLAW &amp; CLIP</div>
      <h3>Terrazzo &amp; Pastel Clip</h3>
      <p>マーブル＆パステル調のアセテートヘアクリップ。忙しい朝も3秒でこなれ感のあるまとめ髪が完成します。</p>
      <div class="price">¥1,980 (tax in)</div>
    </div>
    <div class="card">
      <div class="card-tag">03 / BEAD CHARM &amp; POUCH</div>
      <h3>Daisy Bead Charm &amp; Gift Box</h3>
      <p>ガラスビーズ×シルバーのマルチチャーム。特製スライドボックス＆コットン巾着ポーチ付きでギフトにも最適。</p>
      <div class="price">¥2,800 (tax in)</div>
    </div>
  </section>
</body>
</html>"""


def build_poster_html(t: dict, brand: str, headline: str, subcopy: str, poster_img: str = "") -> str:
    b, h, s = html.escape(brand), html.escape(headline), html.escape(subcopy)
    is_genmai = ("玄米" in brand) or ("養生" in brand) or ("玄米" in subcopy)
    img_uri = _img_uri(poster_img)
    badge_right = "鍼灸師 原まゆこ監修 // 内外同治プログラム" if is_genmai else f"{b} // SEASON LOOKBOOK"
    top_right = "酵素玄米 × 東洋医学 ワタシ養生" if is_genmai else "POP-UP STORE // 2026"
    eyebrow_txt = "8日間ハーフ ¥33,000 ／ 16日間フル ¥55,000（税込・送料込）" if is_genmai else "EVERYDAY CASUAL ACCESSORIES &amp; CHARMS"
    footer_spec = (
        "【セット内容】熟成酵素玄米 / 甘酒2種 / 五種のめぐみ茶 / 還元岩塩 / 黒すりごま / 煙の出ないお灸 / ガイドブック / 毎日LINE伴走<br>"
        "監修：鍼灸治療室「cocon」院長 鍼灸師 原まゆこ（施術歴31年・延べ2万人以上担当）<br>"
        "※本プログラムは食事を整えて胃腸を休ませる養生プログラムであり、疾病の診断・治療・予防を目的としたものではありません。"
        if is_genmai
        else f"SHIBUYA / DAIKANYAMA POP-UP STORE<br>2026.11.01 (SUN) — 11.15 (SUN) / OPEN 11:00 - 20:00<br>BRAND IDENTITY: {b} (300DPI PRINT MASTER)"
    )
    qr_txt = "LINE<br>無料相談" if is_genmai else "ONLINE<br>SHOP"
    hero_media = (
        f'<div style="position:relative; z-index:2; height:760px; border:{t["border_style"]}; box-shadow:{t["shadow"]}; overflow:hidden; margin: 28px 0;">'
        f'<img src="{img_uri}" style="width:100%; height:100%; object-fit:cover;" />'
        f'<div style="position:absolute; bottom:20px; right:24px; background:{t["surface"]}; padding:8px 18px; border:{t["border_style"]}; font-size:13px; font-weight:700; letter-spacing:0.2em; color:{t["primary"]};">{badge_right}</div>'
        f"</div>"
        if img_uri
        else f"""<div class="jewelry-graphic">
    <svg width="460" height="420" viewBox="0 0 460 420" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="230" cy="210" r="180" stroke="{t['primary']}" stroke-width="1.2" opacity="0.35"/>
      <circle cx="195" cy="185" r="48" stroke="{t['primary']}" stroke-width="5"/>
      <circle cx="275" cy="210" r="48" stroke="{t['primary']}" stroke-width="3.5" opacity="0.9"/>
    </svg>
  </div>"""
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{b} — Print Poster</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1200px; height: 1697px; /* A-series 1:1.4142 ratio */
    background: {t['bg']}; color: {t['text']};
    font-family: {t['font_body']}; padding: 76px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative; overflow: hidden;
    border: 18px solid {t['primary']};
  }}
  .top-bar {{
    position: relative; z-index: 2; display: flex; justify-content: space-between;
    border-bottom: {t['border_style']}; padding-top: 4px; padding-bottom: 24px;
    font-size: 19px; letter-spacing: 0.22em; color: {t['primary']}; font-weight: 700;
  }}
  .center-art {{
    position: relative; z-index: 2;
    border: {t['border_style']}; background: {t['surface']};
    padding: 44px 52px; box-shadow: {t['shadow']};
  }}
  .eyebrow {{ font-size: 16px; letter-spacing: 0.22em; color: {t['primary']}; font-weight: 700; margin-bottom: 16px; }}
  h1 {{
    font-family: {t['font_heading']}; font-size: 54px; line-height: 1.28;
    margin-bottom: 18px; word-break: keep-all;
  }}
  .sub {{ font-size: 20px; line-height: 1.75; color: {t['muted']}; }}
  .footer {{
    position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: flex-end;
    border-top: {t['border_style']}; padding-top: 24px;
  }}
  .spec-code {{ font-size: 13.5px; letter-spacing: 0.08em; color: {t['muted']}; line-height: 1.75; max-width: 880px; }}
  .qr-placeholder {{
    width: 112px; height: 112px; border: {t['border_style']}; background: {t['surface']};
    display: flex; align-items: center; justify-content: center; text-align: center;
    font-size: 13px; font-weight: 700; color: {t['primary']}; letter-spacing: 0.12em;
  }}
</style>
</head>
<body>
  <div class="top-bar">
    <span>{b}</span>
    <span>{top_right}</span>
  </div>
  {hero_media}
  <div class="center-art">
    <div class="eyebrow">{eyebrow_txt}</div>
    <h1>{h}</h1>
    <p class="sub">{s}</p>
  </div>
  <div class="footer">
    <div class="spec-code">
      {footer_spec}
    </div>
    <div class="qr-placeholder">{qr_txt}</div>
  </div>
</body>
</html>"""


def build_packaging_html_and_svg(t: dict, brand: str, headline: str, subcopy: str, pack_img: str = "") -> tuple[str, str]:
    b, h, s = html.escape(brand), html.escape(headline), html.escape(subcopy)
    is_genmai = ("玄米" in brand) or ("養生" in brand) or ("玄米" in subcopy)
    img_uri = _img_uri(pack_img)
    dieline_title = (
        f"GIFT BOX DIE-LINE BLUEPRINT (310x240x110mm / RED=CUT / BLUE DASH=FOLD) — {b}"
        if is_genmai
        else f"ACCESSORY BOX DIE-LINE BLUEPRINT (90x90x32mm / RED=CUT / BLUE DASH=FOLD) — {b}"
    )
    dieline_sub = "7-ITEM HOLISTIC FASTING &amp; CARE GIFT BOX" if is_genmai else "DAILY ACCESSORIES &amp; GIFT BOX"
    dieline_mat = "国産無農薬酵素玄米 / 甘酒2種 / 五種のめぐみ茶 / 還元岩塩 / 黒すりごま / 煙の出ないお灸" if is_genmai else "Acrylic Resin / 316L Stainless / Glass Beads"
    pkg_tag = "WATASHI YOUJO — 7-ITEM GIFT BOX DESIGN" if is_genmai else "GIFT PACKAGING &amp; POUCH DESIGN"
    pkg_subtitle = "養生7点コンプリートギフト箱（二段仕切り・箔押し仕様）" if is_genmai else "特製スライドボックス ＆ コットン巾着セット"
    pkg_specs = (
        f"・デザインスタイル: {t['label']}<br>"
        "・同梱7点セット: ①熟成酵素玄米レトルト(24食/48食) ②玄米甘酒・黒米甘酒(各250g) ③五種のめぐみ茶(8g) ④ファイアーロックソルト(30g) ⑤有機黒すりごま(50g) ⑥煙の出ないお灸(12個) ⑦HOW TO ガイドブック(8つのツボ図解)<br>"
        "・箱サイズ仕様: 外箱 310×240×110mm（無晒しクラフト＆生成り和紙貼り・ブロンズ箔押し・内蓋QRコード付き）<br>"
        "・納品データ: 3DスタジオモックアップPNG + 印刷入稿用展開図ダイラインSVG"
        if is_genmai
        else f"・デザインスタイル: {t['label']}<br>"
        "・構成: カラーマッチボックス型スライド箱 + コットン巾着ポーチ + 専用アクセサリー台紙<br>"
        "・サイズ仕様: 外箱 90×90×32mm / 台紙 65×65mm (リング・クリップ・ピアス兼用)<br>"
        "・納品データ: 高精細スタジオモックアップPNG + 印刷入稿用ダイラインSVG"
    )
    svg_dieline = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1000" width="1400" height="1000">
  <rect width="1400" height="1000" fill="#0f172a"/>
  <text x="60" y="58" fill="#94a3b8" font-family="sans-serif" font-size="18" letter-spacing="2">{dieline_title}</text>
  <rect x="400" y="90" width="320" height="140" fill="{t['bg']}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8,6"/>
  <rect x="220" y="230" width="180" height="500" fill="{t['surface']}" stroke="#ef4444" stroke-width="3"/>
  <text x="310" y="485" fill="{t['muted']}" font-family="sans-serif" font-size="13" text-anchor="middle" transform="rotate(-90 310 485)">{b} ORIGINAL</text>
  <rect x="400" y="230" width="320" height="500" fill="{t['bg']}" stroke="#ef4444" stroke-width="3"/>
  <rect x="426" y="258" width="268" height="444" fill="none" stroke="{t['primary']}" stroke-width="2"/>
  <circle cx="560" cy="405" r="44" fill="none" stroke="{t['primary']}" stroke-width="2.5"/>
  <circle cx="560" cy="462" r="10" fill="{t['text']}" stroke="{t['primary']}" stroke-width="2"/>
  <text x="560" y="330" fill="{t['primary']}" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle" letter-spacing="3">{b}</text>
  <text x="560" y="545" fill="{t['text']}" font-family="sans-serif" font-size="16" text-anchor="middle">{h[:18]}</text>
  <text x="560" y="665" fill="{t['muted']}" font-family="sans-serif" font-size="11" text-anchor="middle" letter-spacing="2">{dieline_sub}</text>
  <rect x="720" y="230" width="180" height="500" fill="{t['surface']}" stroke="#ef4444" stroke-width="3"/>
  <rect x="900" y="230" width="320" height="500" fill="{t['bg']}" stroke="#ef4444" stroke-width="3"/>
  <text x="1060" y="335" fill="{t['primary']}" font-family="sans-serif" font-size="15" text-anchor="middle" letter-spacing="3">SPECIFICATIONS &amp; KIT</text>
  <text x="1060" y="390" fill="{t['text']}" font-family="sans-serif" font-size="11.5" text-anchor="middle">{dieline_mat[:38]}</text>
  <text x="1060" y="425" fill="{t['muted']}" font-family="sans-serif" font-size="11.5" text-anchor="middle">{s[:26]}</text>
  <rect x="990" y="610" width="140" height="68" fill="#ffffff" stroke="#111111" stroke-width="2"/>
  <text x="1060" y="652" fill="#111111" font-family="monospace" font-size="15" text-anchor="middle">4 902468 135792</text>
  <rect x="400" y="730" width="320" height="140" fill="{t['bg']}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8,6"/>
</svg>"""

    left_stage = (
        f'<div style="width:680px; height:760px; border:{t["border_style"]}; box-shadow:{t["shadow"]}; position:relative; overflow:hidden;">'
        f'<img src="{img_uri}" style="width:100%; height:100%; object-fit:cover;" />'
        f'<div style="position:absolute; top:24px; left:24px; background:{t["surface"]}; padding:10px 20px; border:{t["border_style"]}; font-family:{t["font_heading"]}; font-size:18px; font-weight:800; letter-spacing:0.18em; color:{t["primary"]};">{b}</div>'
        f"</div>"
        if img_uri
        else f"""<div class="stage">
    <div class="box-3d-wrap">
      <div class="box-front">
        <div style="font-size:11px; letter-spacing:0.3em; color:{t['primary']}; text-align:center;">GIFT BOX</div>
        <div class="label-frame">
          <div style="font-family:{t['font_heading']}; font-size:26px; color:{t['primary']}; letter-spacing:0.2em; margin-bottom:14px;">{b}</div>
          <div style="font-family:{t['font_heading']}; font-size:19px; line-height:1.45; margin-bottom:14px;">{h}</div>
        </div>
      </div>
    </div>
  </div>"""
    )

    pkg_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{b} — Packaging Presentation</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1400px; height: 1000px;
    background: {t['bg']};
    color: {t['text']}; font-family: {t['font_body']};
    display: flex; align-items: center; justify-content: space-between; padding: 64px 72px;
  }}
  .info-panel {{
    max-width: 540px; background: {t['surface']}; padding: 42px;
    border: {t['border_style']}; box-shadow: {t['shadow']};
  }}
  .tag {{ color: {t['primary']}; letter-spacing: 0.22em; font-size: 13px; font-weight: 800; margin-bottom: 14px; }}
  h2 {{ font-family: {t['font_heading']}; font-size: 34px; margin-bottom: 16px; line-height: 1.3; }}
  p {{ color: {t['muted']}; font-size: 15.5px; line-height: 1.8; margin-bottom: 22px; }}
  .specs {{ border-top: {t['border_style']}; padding-top: 18px; font-size: 13px; color: {t['text']}; line-height: 1.9; }}
</style>
</head>
<body>
  {left_stage}
  <div class="info-panel">
    <div class="tag">{pkg_tag}</div>
    <h2>{b}<br><span style="font-size:20px; color:{t['primary']};">{pkg_subtitle}</span></h2>
    <p>{s}</p>
    <div class="specs">
      {pkg_specs}
    </div>
  </div>
</body>
</html>"""
    return pkg_html, svg_dieline


def render_with_playwright(jobs: list[tuple[Path, Path, int, int, Path | None]]) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        for html_path, png_path, w, h, pdf_path in jobs:
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.screenshot(path=str(png_path), full_page=True)
            if pdf_path:
                page.pdf(path=str(pdf_path), width=f"{w}px", height=f"{h}px", print_background=True)
            page.close()
        browser.close()


def find_latest_codex_images(limit: int = 3) -> list[str]:
    """Finds the most recently generated images from Codex's native `image_gen` tool (~/.codex/generated_images/)."""
    codex_img_root = Path.home() / ".codex" / "generated_images"
    if not codex_img_root.exists():
        return []
    files = [p for p in codex_img_root.glob("*/*.png") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p.resolve()) for p in files[:limit]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Omni-Design Studio: 1-Command Unified Pipeline (Website / Poster / Packaging / Promo Video)")
    parser.add_argument("--plan", choices=["plan_a", "plan_b"], default="plan_a")
    parser.add_argument("--target", choices=["website", "poster", "packaging", "promo_video", "all"], default="all")
    parser.add_argument("--with-promo-video", action="store_true", help="Also generate 9:16 and 16:9 promotional videos when --target all")
    parser.add_argument("--trend", choices=list(TREND_TOKENS.keys()), default="organic_editorial")
    parser.add_argument("--ref-image", default="", help="User reference design image to extract color/layout DNA from")
    parser.add_argument("--ref-url", default="", help="User reference website URL to extract color/layout DNA from")
    parser.add_argument("--custom-dna", default="", help="Path to extracted USER_CUSTOM_DNA.json")
    parser.add_argument("--concept-sheet", default="", help="Path to filled CONCEPT_QUESTION_SHEET.md or JSON to auto-generate copy")
    parser.add_argument("--ask-concept", action="store_true", help="Print the Concept & Copywriting Question Sheet for the user")
    parser.add_argument("--print-image-prompts", action="store_true", help="Print the 3 studio photo prompts for Codex `image_gen` or Antigravity `image-generator`")
    parser.add_argument("--auto-codex-images", action="store_true", help="Automatically bind the 3 newest images from ~/.codex/generated_images/ (Codex `image_gen` output)")
    parser.add_argument("--brand", default="LUMIÈRE & CO.")
    parser.add_argument("--category", default="イヤリング・ファインジュエリー")
    parser.add_argument("--headline", default="Luminous Craft,")
    parser.add_argument("--subcopy", default="18Kリサイクルゴールドとあこや真珠が織りなす、有機的なイヤリングコレクション")
    parser.add_argument("--narration", default="", help="Optional voiceover narration for promotional video")
    parser.add_argument("--hero-image", default="", help="Optional path to AI-generated hero photo")
    parser.add_argument("--poster-image", default="", help="Optional path to AI-generated poster photo")
    parser.add_argument("--pack-image", default="", help="Optional path to AI-generated packaging photo")
    parser.add_argument("--out-dir", default="/tmp/omni_design_out")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    t = dict(TREND_TOKENS[args.trend])

    # Step 1: Concept Sheet Q&A / Auto-Copywriting (if requested)
    if args.ask_concept or args.concept_sheet:
        from build_concept_and_copy import (
            ESSENTIAL_QUESTIONS,
            parse_concept_markdown,
            print_agent_questionnaire,
            synthesize_copy_from_concept,
        )

        if args.ask_concept and not args.concept_sheet:
            print_agent_questionnaire(ESSENTIAL_QUESTIONS)
            return

        sheet_p = Path(args.concept_sheet).expanduser().resolve()
        if sheet_p.exists():
            raw_text = sheet_p.read_text(encoding="utf-8")
            parsed_c = json.loads(raw_text) if sheet_p.suffix.lower() == ".json" else parse_concept_markdown(raw_text)
            copy_dna = synthesize_copy_from_concept(parsed_c)
            (out_dir / "CONCEPT_COPY_DNA.json").write_text(
                json.dumps(copy_dna, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            if copy_dna.get("brand"):
                args.brand = copy_dna["brand"]
            if copy_dna.get("headline"):
                args.headline = copy_dna["headline"]
            if copy_dna.get("subcopy"):
                args.subcopy = copy_dna["subcopy"]
            if copy_dna.get("narration") and not args.narration:
                args.narration = copy_dna["narration"]

            print("=== ✨ [Concept Sheet Applied -> Auto Copywriting] ===")
            print(f"・ブランド  : {args.brand}")
            print(f"・メイン見出: {args.headline}")
            print(f"・サブコピー: {args.subcopy}")
            if copy_dna.get("missing_questions_for_user"):
                print("\n📋 【エージェントからの追加ヒアリング（さらに強いコピーにするための未入力項目）】")
                print_agent_questionnaire(copy_dna["missing_questions_for_user"])

    # Step 2: Auto-bind Codex native `image_gen` outputs when --auto-codex-images is set
    if args.auto_codex_images:
        recent = find_latest_codex_images(3)
        if len(recent) >= 1 and not args.hero_image:
            args.hero_image = recent[0]
        if len(recent) >= 2 and not args.poster_image:
            args.poster_image = recent[1]
        if len(recent) >= 3 and not args.pack_image:
            args.pack_image = recent[2]
        if recent:
            print(f"=== 🖼️ [Codex Native `image_gen` Assets Bound] ({len(recent)} files from ~/.codex/generated_images/) ===")
            for idx, r_path in enumerate(recent, 1):
                print(f"  {idx}. {r_path}")

    # Step 3: User Reference DNA Extraction (--ref-image / --ref-url / --custom-dna)
    if args.ref_image or args.ref_url or args.custom_dna:
        from analyze_user_reference import (
            build_missing_asset_recommendations,
            extract_dna_from_image,
            extract_dna_from_url,
        )

        if args.custom_dna and Path(args.custom_dna).expanduser().exists():
            dna = json.loads(Path(args.custom_dna).expanduser().read_text(encoding="utf-8"))
        elif args.ref_image:
            dna = extract_dna_from_image(Path(args.ref_image).expanduser().resolve())
        else:
            dna = extract_dna_from_url(args.ref_url, out_dir)

        missing = build_missing_asset_recommendations(
            dna,
            args.brand,
            args.category,
            bool(args.hero_image),
            bool(args.poster_image),
            bool(args.pack_image),
        )
        dna["missing_asset_requests"] = missing
        (out_dir / "USER_CUSTOM_DNA.json").write_text(json.dumps(dna, ensure_ascii=False, indent=2), encoding="utf-8")
        t.update(dna["tokens"])

        print(f"=== 🔍 [User Reference DNA Applied] {t['label']} ===")
        print(f"・抽出パレット: 背景 {t['bg']} / サーフェス {t['surface']} / アクセント {t['primary']} / 文字 {t['text']}")
        if missing and not args.print_image_prompts:
            print("📋 【エージェントからの素材リクエスト（このリファレンスを完全再現するために推奨される画像）】")
            for idx, m in enumerate(missing, 1):
                print(f"  {idx}. {m['slot']}: {m['what_to_prepare']}")
                print(f"     -> 推奨サイズ: {m['required_spec']}")
                print(f"     -> AI生成プロンプト案: \"{m['ready_to_use_ai_prompt']}\"")

    # Step 4: Output 3 tailored studio prompts (after Concept & Reference DNA are applied!)
    if args.print_image_prompts:
        bg_c = t.get("bg", "#F6F3EC")
        ac_c = t.get("primary", "#9E7B56")
        prompts = {
            "hero_image_prompt": f"Ultra-luxury macro commercial studio photography of {args.category} for brand '{args.brand}'. Harmonized with palette {bg_c} and {ac_c}, natural organic textures (linen, travertine stone, silk), dramatic warm rim lighting, shallow depth of field, shot on Hasselblad H6D-100c, 8k photorealistic, no text, no watermarks.",
            "poster_image_prompt": f"High-fashion editorial lookbook still-life photography of {args.category} for '{args.brand}'. Warm sunlight streaming through crystal glass prisms casting soft caustics and bokeh, color harmony with {bg_c} and {ac_c}, magazine campaign aesthetic, no text, no words.",
            "pack_image_prompt": f"Commercial luxury packaging studio photography for '{args.brand}' ({args.category}). Tactile rigid drawer box and bespoke display card in {bg_c} and {ac_c} foil accents resting on a travertine marble pedestal, warm architectural studio lighting, photorealistic product shot, no text.",
        }
        print(json.dumps(prompts, ensure_ascii=False, indent=2))
        return

    from cms_editor_runtime import inject_wordpress_like_cms

    jobs: list[tuple[Path, Path, int, int, Path | None]] = []
    generated_files: list[str] = []

    if args.target in ("website", "all"):
        web_html = out_dir / "website.html"
        web_png = out_dir / "website_preview.png"
        raw_web = build_website_html(t, args.brand, args.headline, args.subcopy, args.hero_image, args.poster_image)
        web_html.write_text(inject_wordpress_like_cms(raw_web), encoding="utf-8")
        jobs.append((web_html, web_png, 1440, 960, None))
        generated_files.extend([str(web_html), str(web_png)])

    if args.target in ("poster", "all"):
        poster_html = out_dir / "poster.html"
        poster_png = out_dir / "poster_300dpi.png"
        poster_pdf = out_dir / "poster_print.pdf"
        raw_poster = build_poster_html(t, args.brand, args.headline, args.subcopy, args.poster_image)
        poster_html.write_text(inject_wordpress_like_cms(raw_poster), encoding="utf-8")
        jobs.append((poster_html, poster_png, 1200, 1697, poster_pdf))
        generated_files.extend([str(poster_html), str(poster_png), str(poster_pdf)])

    if args.target in ("packaging", "all"):
        pkg_html = out_dir / "packaging_mockup.html"
        pkg_png = out_dir / "packaging_3d_mockup.png"
        pkg_svg = out_dir / "packaging_dieline.svg"
        html_str, svg_str = build_packaging_html_and_svg(t, args.brand, args.headline, args.subcopy, args.pack_image)
        pkg_html.write_text(inject_wordpress_like_cms(html_str), encoding="utf-8")
        pkg_svg.write_text(svg_str, encoding="utf-8")
        jobs.append((pkg_html, pkg_png, 1400, 1000, None))
        generated_files.extend([str(pkg_html), str(pkg_png), str(pkg_svg)])

    if jobs:
        render_with_playwright(jobs)

    if args.target == "promo_video" or args.with_promo_video:
        from build_promo_video import render_promo_video

        promo_palette = {
            "bg": t.get("bg", "#F6F3EC"),
            "surface": t.get("surface", "#EFECE4"),
            "text": t.get("text", "#1C1A17"),
            "accent": t.get("primary", "#9E7B56"),
            "font_heading": t.get("font_heading", "'Cormorant Garamond', 'Noto Serif JP', serif"),
            "font_body": t.get("font_body", "'Noto Serif JP', serif"),
            "frame_shape": t.get("frame_shape", "arch" if t.get("is_organic") else "bento_round"),
            "border_style": t.get("border_style", "1px solid rgba(28, 26, 23, 0.16)"),
            "shadow": t.get("shadow", "0 32px 80px rgba(28, 26, 23, 0.16)"),
        }
        narration = args.narration or f"{args.headline}。{args.subcopy}。{args.brand}。"
        for asp, suffix in [("9:16", "vertical_9x16"), ("16:9", "landscape_16x9")]:
            v_path = out_dir / f"promo_video_{suffix}.mp4"
            render_promo_video(
                brand=args.brand,
                category=args.category,
                headline=args.headline,
                subcopy=args.subcopy,
                out_mp4=v_path,
                aspect=asp,
                duration_sec=10.0,
                fps=24,
                palette=promo_palette,
                hero_image=args.hero_image or str(out_dir / "website_preview.png"),
                poster_image=args.poster_image or str(out_dir / "poster_300dpi.png"),
                pack_image=args.pack_image or str(out_dir / "packaging_3d_mockup.png"),
                narration_text=narration,
            )
            studio_code = "9x16" if asp == "9:16" else "16x9"
            generated_files.extend([
                str(v_path),
                str(out_dir / f"promo_video_studio_{studio_code}.html"),
            ])
        for extra_v in ("promo_captions.srt", "promo_captions.vtt", "promo_audio_track.wav"):
            if (out_dir / extra_v).exists():
                generated_files.append(str(out_dir / extra_v))

    cost_jpy = 0.0 if args.plan == "plan_a" else round(len(generated_files) * 0.6, 2)
    manifest = {
        "brand": args.brand,
        "trend": args.trend,
        "trend_label": t["label"],
        "plan": args.plan,
        "estimated_cost_jpy": cost_jpy,
        "files": generated_files,
    }
    (out_dir / "design_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== [Omni-Design Studio] '{args.brand}' ({t['label']} / {args.plan.upper()}) ===")
    print(f"・実行コスト: 約 {cost_jpy} 円")
    for f in generated_files:
        print(f"  ✔ {f}")


if __name__ == "__main__":
    main()

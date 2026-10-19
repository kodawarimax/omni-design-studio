#!/usr/bin/env python3
"""
Omni-Design Studio: Promotional Video Generator (Image & DNA -> Promo MP4)
Integrates:
  1. EveryInc/product-launch-video: 4-Scene Storyboard (Hook -> Macro -> Packaging -> CTA)
  2. haidrrrry/claude-remotion-skill: 10 Motion Rules (Custom Bezier Easing, Parallax, Staggered Type, Film Grain, Light Leaks)
  3. whaleyxbt/claude-motion: Frame-accurate Headless Chromium -> FFmpeg image2pipe renderer (Zero Node.js bloat)
  4. Strict Cost Discipline:
     - Plan A (0 JPY): Local frame-accurate HTML/CSS/SVG motion engine + harmonic ambient BGM + edge-tts narration
     - Plan B (~30.9 JPY): DeepSeek V4.1-Flash script + Wan 2.1 I2V B-roll integration
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


def _file_uri(path_str: Optional[str]) -> str:
    if not path_str:
        return ""
    p = Path(path_str).expanduser().resolve()
    return p.as_uri() if p.exists() else ""


def generate_luxury_ambient_audio(
    out_wav: Path,
    duration_sec: float = 10.0,
    narration_text: str = "",
    voice: str = "ja-JP-NanamiNeural",
) -> Path:
    """
    Generates a warm, organic luxury boutique ambient soundscape (Fmaj9 -> Em7 -> Dm9 -> Cmaj9 warm pad + crystal chime)
    using FFmpeg aevalsrc, and optionally mixes edge-tts voiceover. Cost: 0 JPY.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    # Warm luxury chord frequencies (Fmaj7 / Cmaj9 ambient shimmer)
    expr = (
        "0.12*sin(2*PI*174.61*t)*exp(-0.15*mod(t,2.5))"
        "+0.10*sin(2*PI*220.00*t)*exp(-0.12*mod(t,2.5))"
        "+0.10*sin(2*PI*261.63*t)*exp(-0.10*mod(t,2.5))"
        "+0.09*sin(2*PI*329.63*t)*exp(-0.14*mod(t,2.5))"
        "+0.06*sin(2*PI*523.25*t)*exp(-0.65*mod(t,1.25))"
        "+0.04*sin(2*PI*659.25*t)*exp(-0.80*mod(t+0.625,1.25))"
    )
    bgm_wav = out_wav.parent / "_tmp_bgm.wav"
    cmd_bgm = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"aevalsrc='{expr}':s=44100:d={duration_sec}",
        "-af", f"lowpass=f=2800,aecho=0.8:0.88:60|120:0.35|0.25,afade=t=in:st=0:d=0.8,afade=t=out:st={max(0.5, duration_sec-1.8):.2f}:d=1.8",
        str(bgm_wav),
    ]
    subprocess.run(cmd_bgm, check=True)

    if not narration_text.strip():
        shutil.move(str(bgm_wav), str(out_wav))
        return out_wav

    # Synthesize narration via edge-tts (Plan A = 0 JPY)
    tts_mp3 = out_wav.parent / "_tmp_tts.mp3"
    try:
        import edge_tts

        async def _run_tts() -> None:
            comm = edge_tts.Communicate(narration_text, voice, rate="-5%", pitch="-2Hz")
            await comm.save(str(tts_mp3))

        asyncio.run(_run_tts())
    except Exception:
        shutil.move(str(bgm_wav), str(out_wav))
        return out_wav

    if tts_mp3.exists() and tts_mp3.stat().st_size > 100:
        cmd_mix = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(bgm_wav),
            "-i", str(tts_mp3),
            "-filter_complex",
            "[1:a]adelay=600|600,volume=1.55[vo];[0:a]volume=0.55[bg];[bg][vo]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            str(out_wav),
        ]
        subprocess.run(cmd_mix, check=True)
        bgm_wav.unlink(missing_ok=True)
        tts_mp3.unlink(missing_ok=True)
    else:
        shutil.move(str(bgm_wav), str(out_wav))
    return out_wav


def build_motion_html(
    brand: str,
    category: str,
    headline: str,
    subcopy: str,
    aspect: str,
    palette: Dict[str, str],
    hero_uri: str,
    poster_uri: str,
    pack_uri: str,
) -> str:
    """
    Builds a frame-accurate, deterministic HTML5/CSS3/JS motion composition
    implementing the 10 Motion Design Rules from `haidrrrry/claude-remotion-skill`
    and the 4-Scene Storyboard from `EveryInc/product-launch-video`.
    """
    is_vertical = aspect == "9:16"
    width = 1080 if is_vertical else 1920
    height = 1920 if is_vertical else 1080

    bg = palette.get("bg", "#F6F3EC")
    surface = palette.get("surface", "#EFECE4")
    text = palette.get("text", "#1C1A17")
    accent = palette.get("accent", "#9E7B56")
    border = palette.get("border", "rgba(28, 26, 23, 0.16)")
    font_heading = palette.get("font_heading", "'Cormorant Garamond', 'Noto Serif JP', serif")
    font_body = palette.get("font_body", "'Noto Serif JP', serif")
    frame_shape = palette.get("frame_shape", "arch")
    border_style = palette.get("border_style", f"1px solid {border}")
    shadow_style = palette.get("shadow", "0 32px 80px rgba(28, 26, 23, 0.16)")

    if frame_shape == "brutal_box":
        hero_radius = "0px"
        card_radius = "0px"
    elif frame_shape == "sharp_grid":
        hero_radius = "2px"
        card_radius = "2px"
    elif frame_shape == "bento_round":
        hero_radius = "32px"
        card_radius = "24px"
    elif frame_shape == "editorial_rect":
        hero_radius = "8px"
        card_radius = "8px"
    else:
        hero_radius = "999px 999px 18px 18px"
        card_radius = "18px"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Noto+Serif+JP:wght@200;300;400&family=Plus+Jakarta+Sans:wght@300;400;500;700&family=Space+Grotesk:wght@500;700&family=Syne:wght@700;800&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background: {bg};
    color: {text};
    font-family: {font_heading};
    position: relative;
    -webkit-font-smoothing: antialiased;
  }}

  /* Tactile Paper Grain & Warm Sunlight Prism Leak */
  .grain-overlay {{
    position: absolute; inset: 0; pointer-events: none; z-index: 90;
    opacity: 0.24;
    background-image: radial-gradient(rgba(28,26,23,0.09) 1px, transparent 0);
    background-size: 16px 16px;
  }}
  .light-leak {{
    position: absolute;
    width: {int(width * 0.9)}px;
    height: {int(height * 0.9)}px;
    border-radius: 50%;
    background: radial-gradient(circle, {accent}44 0%, {accent}18 45%, transparent 72%);
    filter: blur(45px);
    z-index: 5;
    pointer-events: none;
  }}

  /* Persistent Editorial Frame & Header */
  .editorial-border {{
    position: absolute;
    inset: 36px;
    border: {border_style};
    pointer-events: none;
    z-index: 80;
  }}
  .top-bar {{
    position: absolute;
    top: 62px; left: 72px; right: 72px;
    display: flex; justify-content: space-between; align-items: center;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 15px; letter-spacing: 0.28em; text-transform: uppercase;
    z-index: 85;
    opacity: 0.85;
  }}
  .bottom-bar {{
    position: absolute;
    bottom: 62px; left: 72px; right: 72px;
    display: flex; justify-content: space-between; align-items: center;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 14px; letter-spacing: 0.22em; text-transform: uppercase;
    z-index: 85;
    opacity: 0.72;
  }}

  /* Scene Container */
  .scene {{
    position: absolute;
    inset: 0;
    opacity: 0;
    z-index: 20;
  }}

  /* Vertical Japanese Tategaki Accent */
  .tategaki {{
    writing-mode: vertical-rl;
    font-family: {font_body};
    font-weight: 300;
    letter-spacing: 0.38em;
    color: {text};
    line-height: 2.0;
  }}

  /* Dynamic Shape Photo Mask (Arch / Bento / Brutal / Grid) */
  .arch-frame {{
    border-radius: {hero_radius};
    overflow: hidden;
    box-shadow: {shadow_style};
    border: {border_style};
    background: {surface};
    position: relative;
  }}
  .arch-frame img, .polaroid img, .pack-card img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}

  /* Polaroid Inset */
  .polaroid {{
    background: #FCFBF8;
    padding: 18px 18px 46px 18px;
    box-shadow: 0 28px 65px rgba(28, 26, 23, 0.20);
    border: 1px solid {border};
    position: absolute;
  }}
  .polaroid-caption {{
    position: absolute;
    bottom: 14px; left: 20px; right: 20px;
    display: flex; justify-content: space-between;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 12px; letter-spacing: 0.18em; color: #6E665E;
    text-transform: uppercase;
  }}

  .badge-pill {{
    display: inline-block;
    padding: 9px 22px;
    border: 1px solid {accent};
    border-radius: 999px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: {accent};
    background: rgba(255,255,255,0.55);
  }}
</style>
</head>
<body>

  <div class="light-leak" id="lightLeak"></div>
  <div class="editorial-border"></div>

  <div class="top-bar">
    <span>{brand}</span>
    <span id="sceneCounter">01 / ATELIER COLLECTION</span>
  </div>

  <!-- SCENE 1: HOOK & ORGANIC ARCH REVEAL (0.0s - 2.6s) -->
  <div class="scene" id="scene1">
    <div id="s1Arch" class="arch-frame" style="
      position: absolute;
      {'left: 140px; top: 220px; width: 800px; height: 1040px;' if is_vertical else 'right: 130px; top: 130px; width: 640px; height: 820px;'}
    ">
      <img id="s1Img" src="{hero_uri}" alt="Hero" />
    </div>

    <div id="s1Tategaki" class="tategaki" style="
      position: absolute;
      {'right: 78px; top: 250px; font-size: 26px;' if is_vertical else 'right: 820px; top: 170px; font-size: 24px;'}
    ">{category[:18]}</div>

    <div id="s1TextWrap" style="
      position: absolute;
      {'left: 96px; right: 96px; bottom: 200px; text-align: left;' if is_vertical else 'left: 120px; top: 250px; width: 690px;'}
    ">
      <div class="badge-pill" style="margin-bottom: 24px;">2026 NEW SEASON COLLECTION</div>
      <h1 style="
        font-size: {'86px' if is_vertical else '90px'};
        font-weight: 600;
        line-height: 0.98;
        letter-spacing: -0.02em;
        margin-bottom: 24px;
      ">{headline}</h1>
      <p style="
        font-family: {font_body};
        font-size: {'24px' if is_vertical else '21px'};
        font-weight: 400;
        line-height: 1.75;
        opacity: 0.88;
      ">{subcopy}</p>
    </div>
  </div>

  <!-- SCENE 2: MACRO CRAFTSMANSHIP & PARALLAX DUAL SHOT (2.6s - 5.4s) -->
  <div class="scene" id="scene2">
    <div id="s2BgPhoto" style="
      position: absolute;
      {'left: 84px; top: 210px; width: 720px; height: 920px;' if is_vertical else 'left: 120px; top: 140px; width: 760px; height: 800px;'}
      overflow: hidden;
      border-radius: {card_radius};
      box-shadow: {shadow_style};
      border: {border_style};
    ">
      <img id="s2MainImg" src="{poster_uri}" style="width:100%; height:100%; object-fit:cover;" />
    </div>

    <div id="s2Polaroid" class="polaroid" style="
      {'right: 78px; top: 820px; width: 490px; height: 560px;' if is_vertical else 'left: 660px; top: 340px; width: 440px; height: 520px;'}
    ">
      <img id="s2SubImg" src="{hero_uri}" />
      <div class="polaroid-caption">
        <span>FIG. 02 — {brand}</span>
        <span>TOKYO STUDIO</span>
      </div>
    </div>

    <div id="s2Specs" style="
      position: absolute;
      {'left: 96px; right: 96px; bottom: 185px;' if is_vertical else 'right: 120px; top: 250px; width: 580px;'}
    ">
      <div class="badge-pill" style="margin-bottom: 20px;">SIGNATURE DETAILS</div>
      <h2 style="font-size: {'64px' if is_vertical else '62px'}; font-weight: 600; line-height: 1.08; margin-bottom: 22px;">
        Designed for<br><i style="color:{accent};">Everyday Joy.</i>
      </h2>
      <div style="border-top: {border_style}; padding-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; font-family: {font_body}; font-size: 18px;">
        <div><strong style="display:block; font-size:13px; letter-spacing:0.2em; color:{accent}; font-family:'Plus Jakarta Sans';">CATEGORY</strong>{category}</div>
        <div><strong style="display:block; font-size:13px; letter-spacing:0.2em; color:{accent}; font-family:'Plus Jakarta Sans';">COLLECTION</strong>{brand} 2026</div>
      </div>
    </div>
  </div>

  <!-- SCENE 3: TACTILE PACKAGING & UNBOXING EXPERIENCE (5.4s - 8.0s) -->
  <div class="scene" id="scene3">
    <div id="s3Card" class="pack-card" style="
      position: absolute;
      {'left: 96px; right: 96px; top: 230px; height: 920px;' if is_vertical else 'right: 130px; top: 145px; width: 820px; height: 790px;'}
      border-radius: {card_radius};
      overflow: hidden;
      box-shadow: {shadow_style};
      border: {border_style};
    ">
      <img id="s3PackImg" src="{pack_uri}" />
    </div>

    <div id="s3Copy" style="
      position: absolute;
      {'left: 96px; right: 96px; bottom: 210px;' if is_vertical else 'left: 120px; top: 270px; width: 680px;'}
    ">
      <div class="badge-pill" style="margin-bottom: 20px;">SPECIAL GIFT PACKAGING</div>
      <h2 style="font-size: {'64px' if is_vertical else '66px'}; font-weight: 600; line-height: 1.06; margin-bottom: 20px;">
        Unbox Your<br><i style="color:{accent};">Daily Sparkle.</i>
      </h2>
      <p style="font-family: {font_body}; font-size: 21px; font-weight: 400; line-height: 1.8; opacity: 0.88;">
        そのままギフトにも使える特製スライドボックス＆オリジナルポーチ付き。手元に届いた瞬間から気分が上がるパッケージデザイン。
      </p>
    </div>
  </div>

  <!-- SCENE 4: GRAND FINALE & CALL TO ACTION (8.0s - 10.0s) -->
  <div class="scene" id="scene4">
    <div id="s4Center" style="
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 80px;
    ">
      <div style="width: 190px; height: 240px; border-radius: {hero_radius}; overflow: hidden; margin-bottom: 38px; border: {border_style}; box-shadow: {shadow_style};">
        <img src="{hero_uri}" style="width:100%; height:100%; object-fit:cover;" />
      </div>
      <div style="font-family:'Plus Jakarta Sans'; font-size:15px; letter-spacing:0.35em; color:{accent}; margin-bottom:18px;">
        {category.upper()}
      </div>
      <h1 style="font-size: {'92px' if is_vertical else '100px'}; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 18px;">
        {brand}
      </h1>
      <p style="font-family:{font_body}; font-size: 22px; font-weight: 400; letter-spacing: 0.08em; margin-bottom: 44px; opacity: 0.88;">
        {subcopy}
      </p>
      <div style="
        padding: 18px 48px;
        background: {accent};
        color: #FFFFFF;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        border-radius: 999px;
        border: {border_style};
        box-shadow: {shadow_style};
      ">
        CHECK ONLINE STORE — {brand}
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span>OMNI-DESIGN STUDIO // ORGANIC MOTION DNA</span>
    <span id="timecode">00:00:00</span>
  </div>

  <div class="grain-overlay"></div>

<script>
  // Custom Bezier-like easeOutExpo & easeInOutCubic (haidrrrry/claude-remotion-skill rule)
  function clamp(v, min, max) {{ return Math.max(min, Math.min(max, v)); }}
  function easeOutCubic(x) {{ return 1 - Math.pow(1 - clamp(x, 0, 1), 3); }}
  function easeInOutQuad(x) {{
    x = clamp(x, 0, 1);
    return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
  }}

  function sceneOpacity(t, start, end, fadeIn, fadeOut) {{
    if (t < start || t > end) return 0;
    if (t < start + fadeIn) return easeOutCubic((t - start) / fadeIn);
    if (t > end - fadeOut) return easeOutCubic((end - t) / fadeOut);
    return 1;
  }}

  window.setFrame = function(frame, fps) {{
    const t = frame / fps;

    // Subtle organic drift of sunlight leak
    const leak = document.getElementById('lightLeak');
    const lx = Math.sin(t * 0.9) * 120 + 180;
    const ly = Math.cos(t * 0.7) * 90 + 120;
    leak.style.transform = `translate3d(${{lx}}px, ${{ly}}px, 0) scale(${{1 + 0.08 * Math.sin(t * 1.5)}})`;

    // Timecode & scene counter
    const sec = Math.floor(t);
    const fr = Math.floor(frame % fps);
    document.getElementById('timecode').textContent =
      `00:00:${{String(sec).padStart(2,'0')}}:${{String(fr).padStart(2,'0')}}`;

    const counter = document.getElementById('sceneCounter');
    if (t < 2.6) counter.textContent = '01 / ATELIER COLLECTION';
    else if (t < 5.4) counter.textContent = '02 / FINE CRAFTSMANSHIP';
    else if (t < 8.0) counter.textContent = '03 / BESPOKE PACKAGING';
    else counter.textContent = '04 / TOKYO — PARIS';

    // SCENE 1 (0.0 - 2.8s)
    const s1 = document.getElementById('scene1');
    const op1 = sceneOpacity(t, 0.0, 2.75, 0.45, 0.45);
    s1.style.opacity = op1;
    if (op1 > 0) {{
      const p1 = easeOutCubic(t / 2.75);
      document.getElementById('s1Img').style.transform = `scale(${{1.14 - 0.12 * p1}}) translate3d(0, ${{18 * (1 - p1)}}px, 0)`;
      document.getElementById('s1Arch').style.transform = `translate3d(0, ${{35 * (1 - easeOutCubic(t / 1.1))}}px, 0)`;
      document.getElementById('s1TextWrap').style.transform = `translate3d(0, ${{42 * (1 - easeOutCubic(Math.max(0, t - 0.18) / 1.1))}}px, 0)`;
      document.getElementById('s1Tategaki').style.opacity = easeOutCubic(Math.max(0, t - 0.3) / 1.0);
    }}

    // SCENE 2 (2.45 - 5.55s)
    const s2 = document.getElementById('scene2');
    const op2 = sceneOpacity(t, 2.45, 5.55, 0.45, 0.45);
    s2.style.opacity = op2;
    if (op2 > 0) {{
      const localT = t - 2.45;
      const p2 = easeOutCubic(localT / 3.0);
      document.getElementById('s2MainImg').style.transform = `scale(${{1.02 + 0.10 * (localT / 3.1)}})`;
      document.getElementById('s2Polaroid').style.transform =
        `translate3d(0, ${{65 * (1 - easeOutCubic(Math.max(0, localT - 0.25) / 1.2))}}px, 0) rotate(${{-2.5 + 1.8 * p2}}deg)`;
      document.getElementById('s2Specs').style.transform =
        `translate3d(0, ${{36 * (1 - easeOutCubic(Math.max(0, localT - 0.35) / 1.1))}}px, 0)`;
    }}

    // SCENE 3 (5.25 - 8.15s)
    const s3 = document.getElementById('scene3');
    const op3 = sceneOpacity(t, 5.25, 8.15, 0.45, 0.45);
    s3.style.opacity = op3;
    if (op3 > 0) {{
      const localT = t - 5.25;
      const p3 = easeOutCubic(localT / 2.8);
      document.getElementById('s3PackImg').style.transform = `scale(${{1.12 - 0.10 * p3}})`;
      document.getElementById('s3Card').style.transform = `translate3d(0, ${{40 * (1 - easeOutCubic(localT / 1.1))}}px, 0)`;
      document.getElementById('s3Copy').style.transform = `translate3d(0, ${{35 * (1 - easeOutCubic(Math.max(0, localT - 0.25) / 1.1))}}px, 0)`;
    }}

    // SCENE 4 (7.85 - 10.0s)
    const s4 = document.getElementById('scene4');
    const op4 = sceneOpacity(t, 7.85, 10.0, 0.45, 0.25);
    s4.style.opacity = op4;
    if (op4 > 0) {{
      const localT = t - 7.85;
      const p4 = easeOutCubic(localT / 1.4);
      document.getElementById('s4Center').style.transform = `scale(${{0.94 + 0.06 * p4}}) translate3d(0, ${{24 * (1 - p4)}}px, 0)`;
    }}
  }};
</script>
</body>
</html>
"""


def render_promo_video(
    brand: str,
    category: str,
    headline: str,
    subcopy: str,
    out_mp4: Path,
    aspect: str = "9:16",
    duration_sec: float = 10.0,
    fps: int = 24,
    palette: Optional[Dict[str, str]] = None,
    hero_image: Optional[str] = None,
    poster_image: Optional[str] = None,
    pack_image: Optional[str] = None,
    narration_text: str = "",
) -> Path:
    """
    Renders a frame-accurate 1080p Promotional Video (.mp4) using Playwright + FFmpeg image2pipe + ambient audio.
    """
    from playwright.sync_api import sync_playwright

    out_mp4 = out_mp4.expanduser().resolve()
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    is_vertical = aspect == "9:16"
    width = 1080 if is_vertical else 1920
    height = 1920 if is_vertical else 1080

    default_palette = {
        "bg": "#F6F3EC",
        "surface": "#EFECE4",
        "text": "#1C1A17",
        "accent": "#9E7B56",
        "border": "rgba(28, 26, 23, 0.16)",
    }
    if palette:
        default_palette.update({k: v for k, v in palette.items() if v})

    hero_uri = _file_uri(hero_image)
    poster_uri = _file_uri(poster_image) or hero_uri
    pack_uri = _file_uri(pack_image) or hero_uri

    html_str = build_motion_html(
        brand=brand,
        category=category,
        headline=headline,
        subcopy=subcopy,
        aspect=aspect,
        palette=default_palette,
        hero_uri=hero_uri,
        poster_uri=poster_uri,
        pack_uri=pack_uri,
    )

    from cms_editor_runtime import generate_subtitle_files, inject_video_studio_cms

    studio_suffix = "9x16" if is_vertical else "16x9"
    studio_html_path = out_mp4.parent / f"promo_video_studio_{studio_suffix}.html"
    studio_html_path.write_text(inject_video_studio_cms(html_str), encoding="utf-8")

    srt_str, vtt_str = generate_subtitle_files(brand, headline, subcopy, narration_text)
    (out_mp4.parent / "promo_captions.srt").write_text(srt_str, encoding="utf-8")
    (out_mp4.parent / "promo_captions.vtt").write_text(vtt_str, encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="omni_promo_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        html_file = tmp_path / "promo_motion.html"
        html_file.write_text(html_str, encoding="utf-8")

        audio_wav = out_mp4.parent / "promo_audio_track.wav"
        if not audio_wav.exists():
            generate_luxury_ambient_audio(
                out_wav=audio_wav,
                duration_sec=duration_sec,
                narration_text=narration_text,
            )

        total_frames = int(duration_sec * fps)
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-r", str(fps),
            "-i", "-",
            "-i", str(audio_wav),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(out_mp4),
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        try:
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(channel="chrome", headless=True)
                except Exception:
                    browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(html_file.as_uri(), wait_until="networkidle")
                page.wait_for_timeout(300)

                for frame_idx in range(total_frames):
                    page.evaluate(f"window.setFrame({frame_idx}, {fps})")
                    jpg_bytes = page.screenshot(type="jpeg", quality=92)
                    if proc.stdin:
                        proc.stdin.write(jpg_bytes)

                browser.close()
        finally:
            if proc.stdin:
                proc.stdin.close()
            proc.wait()

    return out_mp4


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Promotional Video from Images & Design DNA")
    parser.add_argument("--brand", default="LUMIÈRE & CO.")
    parser.add_argument("--category", default="Fine Jewelry & Artisan Earrings")
    parser.add_argument("--headline", default="Luminous Craft,")
    parser.add_argument("--subcopy", default="18Kリサイクルゴールドとあこや真珠が織りなす、有機的なイヤリングコレクション")
    parser.add_argument("--aspect", choices=["9:16", "16:9", "both"], default="both")
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--hero-image", default=None)
    parser.add_argument("--poster-image", default=None)
    parser.add_argument("--pack-image", default=None)
    parser.add_argument("--dna-json", default=None, help="Optional USER_REFERENCE_DNA.json or DESIGN_DNA.json")
    parser.add_argument(
        "--narration",
        default="光と静寂を纏う、手仕事の造形美。リュミエール・アンド・コー、2026年オータムコレクション。",
        help="Optional Japanese/English voiceover script (synthesized at 0 JPY via edge-tts)",
    )
    parser.add_argument("--out-dir", default="/tmp/omni_promo_video")
    args = parser.parse_args()

    palette = None
    if args.dna_json and Path(args.dna_json).expanduser().exists():
        data = json.loads(Path(args.dna_json).expanduser().read_text(encoding="utf-8"))
        pal = data.get("extracted_palette") or data.get("palette") or {}
        if pal:
            palette = {
                "bg": pal.get("bg", "#F6F3EC"),
                "surface": pal.get("surface", "#EFECE4"),
                "text": pal.get("text", "#1C1A17"),
                "accent": pal.get("accent", "#9E7B56"),
            }

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    aspects = ["9:16", "16:9"] if args.aspect == "both" else [args.aspect]
    for asp in aspects:
        tag = "vertical_9x16" if asp == "9:16" else "landscape_16x9"
        out_path = out_dir / f"promo_video_{tag}.mp4"
        print(f"🎬 Rendering Promotional Video ({asp}) -> {out_path} ...")
        render_promo_video(
            brand=args.brand,
            category=args.category,
            headline=args.headline,
            subcopy=args.subcopy,
            out_mp4=out_path,
            aspect=asp,
            duration_sec=args.duration,
            fps=args.fps,
            palette=palette,
            hero_image=args.hero_image,
            poster_image=args.poster_image,
            pack_image=args.pack_image,
            narration_text=args.narration,
        )
        print(f"  ✔ {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

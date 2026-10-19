#!/usr/bin/env python3
"""
Omni-Design Studio: WordPress/Studio-like Visual Block & Canvas Editor Runtime
Injects a zero-dependency, browser-native visual CMS into generated HTML files
(`website.html`, `poster.html`, `packaging_mockup.html`).

Capabilities when opened in any browser:
  1. Inline WYSIWYG Text Editing (click any text to edit content, font size, color, weight)
  2. 1-Click / Drag-and-Drop Image Replacement + Shape Mask Switcher (Arch / Rounded / Sharp / Circle)
  3. WordPress Gutenberg-style Block Controls (Move Up/Down, Free Drag X/Y, Duplicate, Delete, Add Text/Image Block)
  4. Global Theme Customizer (Background, Surface, Accent, Text Color Pickers + Font Family Switcher + Layout Flip)
  5. 1-Click Export ("💾 編集済みHTMLを保存" & "🖨️ 印刷/PDF保存")
  * Automatically hides itself during Playwright headless screenshot/PDF capture (`navigator.webdriver`) and `@media print`.
"""
from __future__ import annotations


CMS_EDITOR_SNIPPET = r"""
<!-- ==================== OMNI-CMS WORDPRESS-LIKE VISUAL EDITOR ==================== -->
<style id="omni-cms-styles">
  @media print {
    #omni-cms-root, .omni-block-toolbar { display: none !important; }
    [data-omni-selected] { outline: none !important; }
  }
  html.omni-headless #omni-cms-root,
  html.omni-headless .omni-block-toolbar {
    display: none !important;
  }
  #omni-cms-root {
    position: fixed;
    top: 14px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    user-select: none;
  }
  .omni-cms-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(20, 20, 23, 0.94);
    color: #fff;
    padding: 8px 14px;
    border-radius: 999px;
    box-shadow: 0 12px 36px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.14);
    backdrop-filter: blur(16px);
    font-size: 12px;
    white-space: nowrap;
  }
  .omni-cms-brand {
    font-weight: 700;
    letter-spacing: 0.06em;
    color: #E5C158;
    margin-right: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .omni-cms-btn {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.16);
    padding: 5px 11px;
    border-radius: 999px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
  .omni-cms-btn:hover { background: rgba(255,255,255,0.22); }
  .omni-cms-btn.active { background: #E5C158; color: #141417; border-color: #E5C158; font-weight: 700; }
  .omni-cms-btn.primary { background: #2563EB; border-color: #3B82F6; font-weight: 600; }
  .omni-cms-btn.primary:hover { background: #1D4ED8; }
  .omni-cms-sep { width: 1px; height: 18px; background: rgba(255,255,255,0.18); margin: 0 2px; }
  .omni-color-input {
    width: 22px; height: 22px; border: none; padding: 0; border-radius: 50%;
    overflow: hidden; cursor: pointer; background: transparent;
  }
  .omni-cms-select {
    background: rgba(255,255,255,0.12);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    cursor: pointer;
  }
  .omni-cms-select option { background: #1c1c21; color: #fff; }

  /* Floating Inspector for Selected Element */
  .omni-inspector {
    margin-top: 8px;
    background: rgba(24, 24, 28, 0.95);
    color: #fff;
    padding: 10px 16px;
    border-radius: 14px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.14);
    display: none;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .omni-inspector.visible { display: flex; }

  /* Edit Mode Outlines */
  body.omni-edit-mode [data-omni-editable]:hover {
    outline: 2px dashed rgba(59, 130, 246, 0.75) !important;
    outline-offset: 3px;
    cursor: pointer;
  }
  body.omni-edit-mode [data-omni-selected="true"] {
    outline: 2px solid #2563EB !important;
    outline-offset: 4px;
  }
  body.omni-edit-mode img:hover {
    outline: 3px solid #E5C158 !important;
    cursor: pointer;
  }
</style>

<div id="omni-cms-root">
  <div class="omni-cms-bar">
    <span class="omni-cms-brand">✦ OMNI WP-STUDIO</span>
    <button class="omni-cms-btn active" id="omniToggleEditBtn" title="編集モードとプレビューを切り替えます">✏️ 編集モード ON</button>
    <div class="omni-cms-sep"></div>

    <label title="背景色を変更" style="display:flex;align-items:center;gap:4px;cursor:pointer;">
      <span>背景</span><input type="color" id="omniBgColor" class="omni-color-input" value="#F6F3EC" />
    </label>
    <label title="文字色を変更" style="display:flex;align-items:center;gap:4px;cursor:pointer;">
      <span>文字</span><input type="color" id="omniTextColor" class="omni-color-input" value="#1C1A17" />
    </label>
    <select id="omniFontSelect" class="omni-cms-select" title="全体のフォントテイストを変更">
      <option value="">フォント切替...</option>
      <option value="'Cormorant Garamond', 'Noto Serif JP', serif">エレガント明朝 (Editorial Serif)</option>
      <option value="'Shippori Mincho', 'Hiragino Mincho ProN', serif">和モダン明朝 (Japanese Luxury)</option>
      <option value="'Plus Jakarta Sans', 'Inter', 'Hiragino Sans', sans-serif">モダンゴシック (Bento Sans)</option>
      <option value="'Space Grotesk', 'Arial Black', sans-serif">ストリート太ゴシック (Neo-Brutal)</option>
      <option value="'Helvetica Neue', 'Arial', sans-serif">スイスグリッド (Swiss Grid)</option>
    </select>

    <div class="omni-cms-sep"></div>
    <button class="omni-cms-btn" id="omniAddTextBtn" title="新しいテキストブロックを追加">＋ 文字追加</button>
    <button class="omni-cms-btn" id="omniAddImgBtn" title="新しい画像ブロックを追加">🖼️ 画像追加</button>
    <button class="omni-cms-btn" id="omniFlipLayoutBtn" title="左右レイアウトを反転">⇄ レイアウト反転</button>

    <div class="omni-cms-sep"></div>
    <button class="omni-cms-btn primary" id="omniSaveHtmlBtn" title="編集した内容をHTMLファイルとして保存">💾 HTML保存</button>
    <button class="omni-cms-btn" id="omniPrintPdfBtn" title="PDFまたは高解像度印刷">🖨️ PDF出力</button>
  </div>

  <!-- Selected Element Inspector Bar -->
  <div class="omni-inspector" id="omniInspector">
    <span id="omniSelectedTag" style="color:#93C5FD;font-weight:700;">選択中: 要素</span>
    <button class="omni-cms-btn" id="omniMoveUpBtn">↑ 前へ</button>
    <button class="omni-cms-btn" id="omniMoveDownBtn">↓ 次へ</button>
    <button class="omni-cms-btn" id="omniMoveLeftBtn">← 左</button>
    <button class="omni-cms-btn" id="omniMoveRightBtn">→ 右</button>
    <button class="omni-cms-btn" id="omniFontDecBtn">A-</button>
    <button class="omni-cms-btn" id="omniFontIncBtn">A+</button>
    <label style="display:flex;align-items:center;gap:4px;cursor:pointer;">
      <span>要素色</span><input type="color" id="omniElemColor" class="omni-color-input" value="#1C1A17" />
    </label>
    <select id="omniShapeSelect" class="omni-cms-select" title="画像や枠の形状を変更">
      <option value="">枠の形状...</option>
      <option value="999px 999px 18px 18px">アーチ窓 (Arch)</option>
      <option value="28px">角丸カード (Bento 28px)</option>
      <option value="0px">直角ボックス (Sharp 0px)</option>
      <option value="9999px">円形・ピル型 (Circle)</option>
    </select>
    <button class="omni-cms-btn" id="omniReplaceImgBtn" style="display:none;background:#D97706;">📷 画像を差し替え</button>
    <button class="omni-cms-btn" id="omniDupBtn">⧉ 複製</button>
    <button class="omni-cms-btn" id="omniDelBtn" style="background:#DC2626;border-color:#EF4444;">🗑️ 削除</button>
  </div>
  <input type="file" id="omniFileInput" accept="image/*" style="display:none;" />
</div>

<script id="omni-cms-script">
(function() {
  if (navigator.webdriver || window.location.search.includes('export=1')) {
    document.documentElement.classList.add('omni-headless');
    return;
  }

  let editMode = true;
  let selectedEl = null;
  let pendingImgTarget = null;
  const fileInput = document.getElementById('omniFileInput');
  const inspector = document.getElementById('omniInspector');
  const selectedTag = document.getElementById('omniSelectedTag');
  const replaceImgBtn = document.getElementById('omniReplaceImgBtn');

  function initEditableNodes() {
    document.body.classList.add('omni-edit-mode');
    const selectors = 'h1, h2, h3, h4, p, span, a, button, li, div, section, article, figure, img';
    document.querySelectorAll(selectors).forEach(el => {
      if (el.closest('#omni-cms-root')) return;
      el.setAttribute('data-omni-editable', 'true');
      const tag = el.tagName.toLowerCase();
      if (['h1','h2','h3','h4','p','span','li','a','button'].includes(tag) || (tag === 'div' && el.children.length === 0 && el.textContent.trim())) {
        el.setAttribute('contenteditable', 'true');
        el.style.outline = 'none';
      }
    });
  }

  initEditableNodes();

  // Select element on click
  document.addEventListener('click', function(e) {
    if (!editMode) return;
    if (e.target.closest('#omni-cms-root')) return;
    const target = e.target.closest('[data-omni-editable]');
    if (!target) return;

    if (selectedEl && selectedEl !== target) {
      selectedEl.removeAttribute('data-omni-selected');
    }
    selectedEl = target;
    selectedEl.setAttribute('data-omni-selected', 'true');
    const tag = selectedEl.tagName.toLowerCase();
    selectedTag.textContent = '選択中: <' + tag + '>';
    inspector.classList.add('visible');

    if (tag === 'img') {
      replaceImgBtn.style.display = 'inline-flex';
    } else {
      replaceImgBtn.style.display = 'none';
    }
  }, true);

  // Double click image to replace immediately
  document.addEventListener('dblclick', function(e) {
    if (!editMode) return;
    if (e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
      pendingImgTarget = e.target;
      fileInput.click();
    }
  });

  // Drag & Drop image replacement from desktop
  document.addEventListener('dragover', function(e) { e.preventDefault(); });
  document.addEventListener('drop', function(e) {
    if (!editMode) return;
    if (!e.dataTransfer || !e.dataTransfer.files || !e.dataTransfer.files.length) return;
    const file = e.dataTransfer.files[0];
    if (!file.type.startsWith('image/')) return;
    e.preventDefault();
    const imgEl = e.target.closest('img') || (selectedEl && selectedEl.tagName === 'IMG' ? selectedEl : null);
    const reader = new FileReader();
    reader.onload = function(ev) {
      if (imgEl) {
        imgEl.src = ev.target.result;
      } else {
        const wrap = document.createElement('div');
        wrap.style.cssText = 'max-width:420px;margin:24px auto;border-radius:16px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.15);';
        wrap.setAttribute('data-omni-editable', 'true');
        wrap.innerHTML = '<img src="' + ev.target.result + '" style="width:100%;height:auto;display:block;" data-omni-editable="true" />';
        (selectedEl ? selectedEl.parentNode : document.body).appendChild(wrap);
      }
    };
    reader.readAsDataURL(file);
  });

  fileInput.addEventListener('change', function() {
    if (!fileInput.files || !fileInput.files[0]) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
      if (pendingImgTarget) {
        pendingImgTarget.src = ev.target.result;
        pendingImgTarget = null;
      } else {
        const wrap = document.createElement('div');
        wrap.style.cssText = 'max-width:420px;margin:24px auto;border-radius:16px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.15);';
        wrap.setAttribute('data-omni-editable', 'true');
        wrap.innerHTML = '<img src="' + ev.target.result + '" style="width:100%;height:auto;display:block;" data-omni-editable="true" />';
        (selectedEl ? selectedEl.parentNode : document.body).appendChild(wrap);
      }
    };
    reader.readAsDataURL(fileInput.files[0]);
    fileInput.value = '';
  });

  // Toggle Edit / Preview Mode
  document.getElementById('omniToggleEditBtn').addEventListener('click', function() {
    editMode = !editMode;
    this.classList.toggle('active', editMode);
    this.textContent = editMode ? '✏️ 編集モード ON' : '👁️ プレビュー中';
    document.body.classList.toggle('omni-edit-mode', editMode);
    document.querySelectorAll('[contenteditable]').forEach(el => {
      el.setAttribute('contenteditable', editMode ? 'true' : 'false');
    });
    if (!editMode && selectedEl) {
      selectedEl.removeAttribute('data-omni-selected');
      inspector.classList.remove('visible');
    }
  });

  // Global Theme Controls
  document.getElementById('omniBgColor').addEventListener('input', function(e) {
    document.body.style.background = e.target.value;
    document.documentElement.style.background = e.target.value;
  });
  document.getElementById('omniTextColor').addEventListener('input', function(e) {
    document.body.style.color = e.target.value;
  });
  document.getElementById('omniFontSelect').addEventListener('change', function(e) {
    if (!e.target.value) return;
    document.body.style.fontFamily = e.target.value;
    document.querySelectorAll('h1, h2, h3, .headline, .brand').forEach(el => {
      el.style.fontFamily = e.target.value;
    });
  });

  // Add Text / Image / Flip Layout
  document.getElementById('omniAddTextBtn').addEventListener('click', function() {
    const p = document.createElement('div');
    p.setAttribute('contenteditable', 'true');
    p.setAttribute('data-omni-editable', 'true');
    p.style.cssText = 'padding:16px 24px;margin:16px auto;max-width:680px;font-size:20px;line-height:1.6;border:1px dashed rgba(150,150,150,0.4);border-radius:8px;';
    p.textContent = '新しいテキストブロック（クリックして自由に文字を編集・移動できます）';
    (selectedEl ? selectedEl.parentNode : document.body).appendChild(p);
  });

  document.getElementById('omniAddImgBtn').addEventListener('click', function() {
    pendingImgTarget = null;
    fileInput.click();
  });

  document.getElementById('omniFlipLayoutBtn').addEventListener('click', function() {
    document.querySelectorAll('section, .hero, .grid, main, .split').forEach(el => {
      const st = window.getComputedStyle(el);
      if (st.display === 'grid' || st.display === 'flex') {
        const children = Array.from(el.children);
        if (children.length >= 2) {
          children.reverse().forEach(c => el.appendChild(c));
        }
      }
    });
  });

  // Selected Element Inspector Actions
  function nudgeSelected(dx, dy) {
    if (!selectedEl) return;
    const curX = parseFloat(selectedEl.getAttribute('data-ox') || '0') + dx;
    const curY = parseFloat(selectedEl.getAttribute('data-oy') || '0') + dy;
    selectedEl.setAttribute('data-ox', curX);
    selectedEl.setAttribute('data-oy', curY);
    selectedEl.style.transform = `translate(${curX}px, ${curY}px)`;
  }

  document.getElementById('omniMoveUpBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    if (selectedEl.previousElementSibling && selectedEl.previousElementSibling.id !== 'omni-cms-root') {
      selectedEl.parentNode.insertBefore(selectedEl, selectedEl.previousElementSibling);
    } else {
      nudgeSelected(0, -16);
    }
  });
  document.getElementById('omniMoveDownBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    if (selectedEl.nextElementSibling) {
      selectedEl.parentNode.insertBefore(selectedEl.nextElementSibling, selectedEl);
    } else {
      nudgeSelected(0, 16);
    }
  });
  document.getElementById('omniMoveLeftBtn').addEventListener('click', function() { nudgeSelected(-16, 0); });
  document.getElementById('omniMoveRightBtn').addEventListener('click', function() { nudgeSelected(16, 0); });

  document.getElementById('omniFontIncBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    const cur = parseFloat(window.getComputedStyle(selectedEl).fontSize) || 18;
    selectedEl.style.fontSize = (cur + 3) + 'px';
  });
  document.getElementById('omniFontDecBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    const cur = parseFloat(window.getComputedStyle(selectedEl).fontSize) || 18;
    selectedEl.style.fontSize = Math.max(10, cur - 3) + 'px';
  });
  document.getElementById('omniElemColor').addEventListener('input', function(e) {
    if (!selectedEl) return;
    selectedEl.style.color = e.target.value;
  });
  document.getElementById('omniShapeSelect').addEventListener('change', function(e) {
    if (!selectedEl || !e.target.value) return;
    const box = selectedEl.tagName === 'IMG' && selectedEl.parentElement ? selectedEl.parentElement : selectedEl;
    box.style.borderRadius = e.target.value;
    box.style.overflow = 'hidden';
  });
  replaceImgBtn.addEventListener('click', function() {
    if (selectedEl && selectedEl.tagName === 'IMG') {
      pendingImgTarget = selectedEl;
      fileInput.click();
    }
  });
  document.getElementById('omniDupBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    const clone = selectedEl.cloneNode(true);
    clone.removeAttribute('data-omni-selected');
    selectedEl.parentNode.insertBefore(clone, selectedEl.nextSibling);
  });
  document.getElementById('omniDelBtn').addEventListener('click', function() {
    if (!selectedEl) return;
    const toRemove = selectedEl;
    selectedEl = null;
    inspector.classList.remove('visible');
    toRemove.remove();
  });

  // Save edited HTML
  document.getElementById('omniSaveHtmlBtn').addEventListener('click', function() {
    if (selectedEl) selectedEl.removeAttribute('data-omni-selected');
    const htmlContent = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    const pageName = (window.location.pathname.split('/').pop() || 'edited_design.html').replace(/\.html?$/i, '') + '_edited.html';
    a.download = pageName;
    a.click();
  });

  // Print / Save PDF
  document.getElementById('omniPrintPdfBtn').addEventListener('click', function() {
    window.print();
  });
})();
</script>
<!-- ==================== /OMNI-CMS WORDPRESS-LIKE VISUAL EDITOR ==================== -->
"""


def inject_wordpress_like_cms(html_str: str) -> str:
    """Injects the WordPress-like visual block & canvas editor right before </body>."""
    if "id=\"omni-cms-root\"" in html_str:
        return html_str
    if "</body>" in html_str:
        return html_str.replace("</body>", f"{CMS_EDITOR_SNIPPET}\n</body>", 1)
    return html_str + "\n" + CMS_EDITOR_SNIPPET


VIDEO_STUDIO_SNIPPET = r"""
<!-- ==================== OMNI VIDEO & CAPTION TIMELINE STUDIO ==================== -->
<style id="omni-video-studio-styles">
  html.omni-headless #omni-video-timeline-bar,
  html.omni-headless #omni-caption-overlay {
    display: none !important;
  }
  #omni-caption-overlay {
    position: absolute;
    left: 50%;
    bottom: 88px;
    transform: translateX(-50%);
    z-index: 95;
    background: rgba(15, 15, 18, 0.78);
    color: #F6F3EC;
    padding: 14px 28px;
    border-radius: 14px;
    font-family: 'Noto Serif JP', 'Hiragino Sans', sans-serif;
    font-size: 24px;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-align: center;
    max-width: 82%;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.22);
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    cursor: text;
  }
  #omni-video-timeline-bar {
    position: fixed;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(20, 20, 24, 0.95);
    color: #fff;
    padding: 10px 18px;
    border-radius: 999px;
    box-shadow: 0 14px 40px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.16);
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
    font-size: 12px;
    white-space: nowrap;
  }
  #omniScrubber {
    width: 220px;
    accent-color: #E5C158;
    cursor: pointer;
  }
</style>

<div id="omni-caption-overlay" contenteditable="true" data-omni-editable="true" title="クリックしてこのシーンの字幕（キャプション）を直接編集できます">
  光と静寂を纏う、手仕事の造形美
</div>

<div id="omni-video-timeline-bar">
  <button class="omni-cms-btn active" id="omniPlayPauseBtn">⏸ 一時停止 (編集)</button>
  <input type="range" id="omniScrubber" min="0" max="239" value="30" />
  <span id="omniTimeLabel" style="font-variant-numeric:tabular-nums;min-width:78px;">01.2s / 10.0s</span>
  <div class="omni-cms-sep"></div>
  <button class="omni-cms-btn" data-jump-sec="0.8">Scene 1 (導入)</button>
  <button class="omni-cms-btn" data-jump-sec="3.5">Scene 2 (造形)</button>
  <button class="omni-cms-btn" data-jump-sec="6.2">Scene 3 (箱・包装)</button>
  <button class="omni-cms-btn" data-jump-sec="8.8">Scene 4 (CTA)</button>
  <div class="omni-cms-sep"></div>
  <button class="omni-cms-btn primary" id="omniExportSrtBtn" title="編集したキャプションをPremiere/CapCut用のSRT字幕ファイルとして保存">📝 SRT字幕を保存</button>
</div>

<script id="omni-video-studio-script">
(function() {
  if (navigator.webdriver || window.location.search.includes('export=1')) {
    return;
  }

  const fps = 24;
  const totalFrames = 240;
  let currentFrame = 30;
  let playing = false;
  const scrubber = document.getElementById('omniScrubber');
  const timeLabel = document.getElementById('omniTimeLabel');
  const playBtn = document.getElementById('omniPlayPauseBtn');
  const captionBox = document.getElementById('omni-caption-overlay');

  // Per-scene editable captions (synchronized with SRT export)
  const sceneCaptions = [
    { start: 0.0, end: 2.6, text: "光と静寂を纏う、手仕事の造形美。" },
    { start: 2.6, end: 5.4, text: "18Kリサイクルゴールドと、あこや真珠の有機的な輝き。" },
    { start: 5.4, end: 8.0, text: "箱を開ける瞬間から始まる、特別な余韻をお届けします。" },
    { start: 8.0, end: 10.0, text: "LUMIÈRE & CO. — 公式オンラインアトリエにて公開中。" }
  ];

  function activeSceneIdx(t) {
    if (t < 2.6) return 0;
    if (t < 5.4) return 1;
    if (t < 8.0) return 2;
    return 3;
  }

  let lastIdx = -1;
  captionBox.addEventListener('input', function() {
    const t = currentFrame / fps;
    const idx = activeSceneIdx(t);
    sceneCaptions[idx].text = captionBox.textContent.trim();
  });

  function updateFrame(f) {
    currentFrame = Math.max(0, Math.min(totalFrames - 1, f));
    scrubber.value = currentFrame;
    const t = currentFrame / fps;
    timeLabel.textContent = t.toFixed(1) + 's / 10.0s';
    if (typeof window.setFrame === 'function') {
      window.setFrame(currentFrame, fps);
    }
    const idx = activeSceneIdx(t);
    if (idx !== lastIdx && document.activeElement !== captionBox) {
      captionBox.textContent = sceneCaptions[idx].text;
      lastIdx = idx;
    }
  }

  // Fit 1080p canvas nicely inside browser window for interactive editing
  function fitViewport() {
    const w = document.body.offsetWidth || 1080;
    const h = document.body.offsetHeight || 1920;
    const scale = Math.min((window.innerWidth - 60) / w, (window.innerHeight - 160) / h, 1);
    document.body.style.transformOrigin = 'top center';
    document.body.style.transform = `scale(${scale})`;
    document.body.style.margin = '64px auto 0 auto';
    document.documentElement.style.background = '#121215';
    document.documentElement.style.overflow = 'auto';
  }
  window.addEventListener('resize', fitViewport);
  setTimeout(fitViewport, 50);
  updateFrame(30);

  scrubber.addEventListener('input', function(e) {
    playing = false;
    playBtn.textContent = '▶️ 再生プレビュー';
    playBtn.classList.remove('active');
    updateFrame(parseInt(e.target.value, 10));
  });

  playBtn.addEventListener('click', function() {
    playing = !playing;
    this.textContent = playing ? '⏸ 一時停止 (編集)' : '▶️ 再生プレビュー';
    this.classList.toggle('active', playing);
  });

  document.querySelectorAll('[data-jump-sec]').forEach(btn => {
    btn.addEventListener('click', function() {
      playing = false;
      playBtn.textContent = '▶️ 再生プレビュー';
      playBtn.classList.remove('active');
      const sec = parseFloat(this.getAttribute('data-jump-sec'));
      updateFrame(Math.floor(sec * fps));
    });
  });

  setInterval(function() {
    if (playing) {
      updateFrame((currentFrame + 1) % totalFrames);
    }
  }, 1000 / fps);

  function fmtSrtTime(sec) {
    const ms = Math.round((sec % 1) * 1000);
    const s = Math.floor(sec) % 60;
    const m = Math.floor(sec / 60) % 60;
    const h = Math.floor(sec / 3600);
    const pad = (n, l=2) => String(n).padStart(l, '0');
    return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
  }

  document.getElementById('omniExportSrtBtn').addEventListener('click', function() {
    const lines = sceneCaptions.map((c, i) =>
      `${i + 1}\n${fmtSrtTime(c.start)} --> ${fmtSrtTime(c.end)}\n${c.text}\n`
    ).join('\n');
    const blob = new Blob([lines], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'promo_captions_edited.srt';
    a.click();
  });
})();
</script>
<!-- ==================== /OMNI VIDEO & CAPTION TIMELINE STUDIO ==================== -->
"""


def inject_video_studio_cms(html_str: str) -> str:
    """Injects both the WordPress-like visual editor and the Video Timeline & Caption Studio."""
    with_wp = inject_wordpress_like_cms(html_str)
    if "id=\"omni-video-timeline-bar\"" in with_wp:
        return with_wp
    if "</body>" in with_wp:
        return with_wp.replace("</body>", f"{VIDEO_STUDIO_SNIPPET}\n</body>", 1)
    return with_wp + "\n" + VIDEO_STUDIO_SNIPPET


def generate_subtitle_files(
    brand: str,
    headline: str,
    subcopy: str,
    narration_text: str = "",
) -> tuple[str, str]:
    """
    Generates industry-standard .srt and .vtt subtitle files so the promotional video's
    captions can be effortlessly edited in Premiere Pro, CapCut, DaVinci Resolve, Final Cut, or YouTube.
    """
    c1 = f"{headline} — 光と静寂を纏う、手仕事の造形美。"
    c2 = subcopy or "素材の持つ温もりと、妥協のないクラフトマンシップ。"
    c3 = "箱を開ける瞬間から始まる、特別な余韻をお届けします。"
    c4 = f"{brand} — 公式コレクション公開中"
    if narration_text and len(narration_text) > 10:
        parts = [p.strip() for p in narration_text.replace("。", "。\n").splitlines() if p.strip()]
        if len(parts) >= 2:
            c1 = parts[0]
            c2 = parts[1]

    srt_content = (
        f"1\n00:00:00,000 --> 00:00:02,600\n{c1}\n\n"
        f"2\n00:00:02,600 --> 00:00:05,400\n{c2}\n\n"
        f"3\n00:00:05,400 --> 00:00:08,000\n{c3}\n\n"
        f"4\n00:00:08,000 --> 00:00:10,000\n{c4}\n"
    )
    vtt_content = (
        "WEBVTT\n\n"
        f"00:00:00.000 --> 00:00:02.600\n{c1}\n\n"
        f"00:00:02.600 --> 00:00:05.400\n{c2}\n\n"
        f"00:00:05.400 --> 00:00:08.000\n{c3}\n\n"
        f"00:00:08.000 --> 00:00:10.000\n{c4}\n"
    )
    return srt_content, vtt_content


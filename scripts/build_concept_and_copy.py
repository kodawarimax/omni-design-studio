#!/usr/bin/env python3
"""
Omni-Design Studio: Concept & Copywriting Question Sheet Engine
Based on Google Doc Concept Sheet (1aNnm-xMt-8qyEi5lerjKd4M38845VQ7oF4wPchaIgWE).
Features:
  1. Generates interactive/structured questions for the Agent to ask the user when copy/concept is not yet defined.
  2. Parses a filled or partially filled CONCEPT_QUESTION_SHEET.md (or JSON) and diagnoses missing core elements.
  3. Synthesizes Website / Poster / Packaging / Promo Video headlines, subcopies, and 4-scene narration scripts deterministically (0 JPY).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


ESSENTIAL_QUESTIONS: List[Dict[str, str]] = [
    {
        "id": "target_persona",
        "section": "1. 見込み客（ターゲット）像",
        "question": "見込み客は現在どんな状況の人ですか？（一言で言うとどんな人で、どんな現実の悩み・問題があり、究極的にどうなりたいですか？）",
        "maps_to": "見込み客の概要 / 見込み客の現実 / 見込み客の究極の理想の状態",
    },
    {
        "id": "product_and_benefits",
        "section": "2 & 3. フロントエンド＆バックエンド商品・ベネフィット",
        "question": "商品名（ブランド名）と概要、および手に入れることで得られる3つのベネフィット（①機能面、②感情面、③自己実現）と他社との決定的な違い（強み）は何ですか？",
        "maps_to": "バックエンド商品名 / 得られるベネフィット / 商品の他との違いや強み",
    },
    {
        "id": "core_concept",
        "section": "4. コンセプト（誰に × 何によって × どうなれる？）",
        "question": "「誰に」「何によって（独自の手法・素材・メソッド）」「どうなれる（得られる変化）」を一言で言うとどうなりますか？",
        "maps_to": "誰に、誰が？ / 何によって / どうなれる？",
    },
    {
        "id": "paradigm_shift",
        "section": "4. コンセプトを補足するロジック（旧前提の破壊 ➔ 真の解決策）",
        "question": "見込み客が今まで信じていた「間違った思い込み・旧来の解決策」は何で、なぜそれでは解決しなかったのですか？そして、あなたの「真の解決策」が機能する理由は何ですか？",
        "maps_to": "見込み客が信じている旧前提 / 上記が機能しないメカニズム / 真の解決策",
    },
    {
        "id": "story_and_proof",
        "section": "5 & 6. 発信者の想い・実績・お客様の声（ビフォー ➔ きっかけ ➔ アフター）",
        "question": "なぜこの商品・サービスを提供しているのか（想い・実績数字）、また購入者（またはあなた自身）の「ビフォー（過去の痛み）➔ きっかけ ➔ アフター（得られた変化）」を教えてください。",
        "maps_to": "サービスを提供する理由 / 実績数字 / 購入者のビフォー・きっかけ・アフター",
    },
]


def parse_concept_markdown(md_text: str) -> Dict[str, str]:
    """
    Extracts key-value pairs from a filled CONCEPT_QUESTION_SHEET.md file.
    """
    extracted: Dict[str, str] = {}
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        # Match `- **Key**: Value` or `- Key: Value`
        m = re.match(r"^-\s*(?:\*\*(.+?)\*\*|([^:：]+))\s*[:：]\s*(.*)$", line)
        if m:
            key = (m.group(1) or m.group(2) or "").strip()
            val = (m.group(3) or "").strip()
            if key and val:
                extracted[key] = val
    return extracted


def _find_val(data: Dict[str, str], keywords: List[str], default: str = "") -> str:
    for k, v in data.items():
        if any(kw in k for kw in keywords) and v.strip():
            return v.strip()
    return default


def synthesize_copy_from_concept(data: Dict[str, str]) -> Dict[str, Any]:
    """
    Deterministically synthesizes high-converting headlines, subcopies, and video narration
    from the parsed Concept Sheet fields.
    """
    brand = _find_val(data, ["バックエンド商品名", "名前 / ブランド名", "フロントエンド商品名", "名前"], "")
    target = _find_val(data, ["誰に、誰が", "見込み客の概要"], "")
    method = _find_val(data, ["何によって", "真の解決策（", "商品の他との違いや強み"], "")
    outcome = _find_val(data, ["どうなれる", "究極の理想の状態", "購入者のアフター"], "")
    daily_ideal = _find_val(data, ["日々の理想", "感情面"], "")
    pain = _find_val(data, ["見込み客の現実", "購入者のビフォー"], "")
    old_belief = _find_val(data, ["信じている旧前提", "実行している解決策"], "")
    true_solution = _find_val(data, ["真の解決策（", "商品の他との違いや強み"], method)
    proof = _find_val(data, ["実績・エビデンス", "実績数字", "メディア"], "")
    frontend = _find_val(data, ["フロントエンド商品名", "フロントエンド商品概要"], "")

    # 1. Headline generation (Prioritize Outcome + Method/Paradigm Shift)
    if outcome and method:
        headline = f"{outcome}"
    elif outcome:
        headline = outcome
    elif true_solution:
        headline = true_solution
    else:
        headline = "理想の未来を形にする、本質のアプローチ。"

    # 2. Subcopy generation (Target x Method x Benefit)
    sub_parts = []
    if old_belief:
        sub_parts.append(f"「{old_belief}」という常識を超え、")
    if target and method:
        sub_parts.append(f"{target}へ、{method}によって")
    elif method:
        sub_parts.append(f"{method}によって")
    if daily_ideal:
        sub_parts.append(f"{daily_ideal}を実現する。")
    elif outcome:
        sub_parts.append(f"{outcome}へ導きます。")
    subcopy = "".join(sub_parts).strip() or "機能・感情・自己実現のすべてを満たすシグネチャーコレクション。"

    # 3. 4-Scene Promotional Video Narration
    s1_hook = f"まだ「{old_belief}」で悩んでいませんか？" if old_belief else (f"{pain}を感じているあなたへ。" if pain else f"{headline}。")
    s2_solution = f"私たちがたどり着いた真の答えは、{true_solution}。" if true_solution else f"{subcopy}"
    s3_benefit = f"{daily_ideal or outcome}。" if (daily_ideal or outcome) else "日常のすべてが特別な体験へと変わります。"
    s4_cta = f"{brand}。{frontend}から、新しい物語を始めましょう。" if (brand and frontend) else f"{brand or 'コレクション'}の全貌を、ぜひご体感ください。"
    narration = f"{s1_hook} {s2_solution} {s3_benefit} {s4_cta}".strip()

    # Check missing essential questions
    missing_questions: List[Dict[str, str]] = []
    if not (target or pain or outcome):
        missing_questions.append(ESSENTIAL_QUESTIONS[0])
    if not (brand and (method or true_solution)):
        missing_questions.append(ESSENTIAL_QUESTIONS[1])
    if not (target and method and outcome):
        missing_questions.append(ESSENTIAL_QUESTIONS[2])
    if not (old_belief and true_solution):
        missing_questions.append(ESSENTIAL_QUESTIONS[3])
    if not proof:
        missing_questions.append(ESSENTIAL_QUESTIONS[4])

    return {
        "brand": brand,
        "headline": headline,
        "subcopy": subcopy,
        "narration": narration,
        "concept_core": {
            "who_target": target,
            "by_what_method": method,
            "what_outcome": outcome,
            "old_premise_broken": old_belief,
            "true_solution": true_solution,
            "daily_emotional_benefit": daily_ideal,
            "credibility_proof": proof,
            "frontend_offer": frontend,
        },
        "missing_questions_for_user": missing_questions,
        "raw_extracted": data,
    }


def print_agent_questionnaire(missing: List[Dict[str, str]]) -> None:
    print("================================================================================")
    print("📝 【コンセプト＆キャッチコピー設計 ヒアリングシート（エージェントからの質問）】")
    print("Webサイト・ポスター・パッケージ・プロモ動画の心に刺さるキャッチコピーと")
    print("コンセプトを作るため、以下の項目（わかる範囲でOK）を教えてください：")
    print("================================================================================")
    for idx, q in enumerate(missing, 1):
        print(f"\nQ{idx}. 【{q['section']}】")
        print(f"   {q['question']}")
        print(f"   （対象項目: {q['maps_to']}）")
    print("\n💡 詳細記入用テンプレート: templates/CONCEPT_QUESTION_SHEET.md")
    print("================================================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="Concept Sheet Parser & Copywriting Question Engine")
    parser.add_argument("--concept-sheet", default="", help="Path to filled CONCEPT_QUESTION_SHEET.md or JSON")
    parser.add_argument("--print-questions", action="store_true", help="Print the 5-part Concept Question Sheet for the user")
    parser.add_argument("--out-json", default="/tmp/CONCEPT_COPY_DNA.json", help="Output synthesized copy JSON")
    args = parser.parse_args()

    if args.print_questions or not args.concept_sheet:
        print_agent_questionnaire(ESSENTIAL_QUESTIONS)
        if not args.concept_sheet:
            return

    sheet_path = Path(args.concept_sheet).expanduser().resolve()
    if not sheet_path.exists():
        print_agent_questionnaire(ESSENTIAL_QUESTIONS)
        return

    text = sheet_path.read_text(encoding="utf-8")
    if sheet_path.suffix.lower() == ".json":
        parsed = json.loads(text)
    else:
        parsed = parse_concept_markdown(text)

    result = synthesize_copy_from_concept(parsed)
    out_path = Path(args.out_json).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== ✨ [Concept & Copywriting DNA Synthesized] ===")
    print(f"・ブランド/商品名 : {result['brand'] or '(未指定)'}")
    print(f"・メインコピー    : {result['headline']}")
    print(f"・サブコピー      : {result['subcopy']}")
    print(f"・動画ナレーション: {result['narration']}")
    print(f"・保存先JSON      : {out_path}")

    if result["missing_questions_for_user"]:
        print("\n⚠️ さらに強いコンセプト・コピーに磨くため、以下の未入力項目もぜひ教えてください：")
        print_agent_questionnaire(result["missing_questions_for_user"])


if __name__ == "__main__":
    main()

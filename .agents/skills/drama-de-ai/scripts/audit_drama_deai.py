#!/usr/bin/env python3
"""Universal short-drama compliance & de-AI regression auditor.

Automatically discovers `.drama-deai-config.json` in the current working
directory (or via `--config`), or falls back cleanly to universal Chinese
short-drama de-AI rules when no project config exists yet.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from typing import Any

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent

# 通用中文短剧 AI 味信号（跨项目复用，不写死任何具体剧本设定）
ACT_ADVERBS = ["猛地", "死死", "骤然", "陡然", "瞬间", "齐刷刷", "缓缓", "微微", "淡淡"]
HEAVY_ADVERBS = {"猛地", "死死", "骤然", "陡然", "瞬间", "齐刷刷"}
PAREN_CLICHES = ["沉声", "高声", "一字一顿", "冷笑", "厉声", "颤声"]
BINARY_CONTRAST = re.compile(
    r"(?:不是|并非|不在于|不只是|不止是|不仅是).{0,24}(?:而是|而在于|更是)|与其说.{0,24}不如说"
)
FICTION_FILLER = [
    "不禁", "情不自禁", "不由自主", "话音未落", "说罢", "心中暗道",
    "嘴角微扬", "指节泛白", "深吸一口气", "空气仿佛", "仿佛凝固",
]

DEFAULT_CONFIG: dict[str, Any] = {
    "project_name": "通用短剧项目（无局部配置）",
    "script_glob": "*.md",
    "format_limits": {
        "max_scenes": 2,
        "max_action_chars": 40,
        "max_clause_chars": 25,
        "min_est_seconds": 0,
        "max_est_seconds": 9999,
        "speech_rate_cps": 4.5,
        "action_beat_seconds": 1.5,
        "base_overhead_seconds": 5.0,
    },
    "forbidden_words": [],
    "forbidden_regex": [],
    "max_term_counts": {},
    "deai_thresholds": {
        "max_heavy_adverbs": 2,
        "max_paren_cliches": 5,
        "max_em_dash_dlg": 2,
    },
    "exempt_action_prefixes": ["【"],
}


def load_config(config_path: pathlib.Path | None) -> dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    target = config_path or pathlib.Path.cwd() / ".drama-deai-config.json"
    if target.exists():
        user_cfg = json.loads(target.read_text(encoding="utf-8"))
        for key in ("project_name", "script_glob", "forbidden_words", "forbidden_regex", "max_term_counts", "exempt_action_prefixes"):
            if key in user_cfg:
                cfg[key] = user_cfg[key]
        for nested in ("format_limits", "deai_thresholds"):
            if nested in user_cfg and isinstance(user_cfg[nested], dict):
                cfg[nested].update(user_cfg[nested])
    return cfg


def init_workspace() -> int:
    cwd = pathlib.Path.cwd()
    cfg_dst = cwd / ".drama-deai-config.json"
    prof_dst = cwd / ".drama-deai-profile.md"
    cfg_src = SKILL_DIR / "resources" / "config.template.json"
    prof_src = SKILL_DIR / "resources" / "profile.template.md"

    created = []
    if not cfg_dst.exists():
        shutil.copy2(cfg_src, cfg_dst)
        created.append(str(cfg_dst))
    if not prof_dst.exists():
        shutil.copy2(prof_src, prof_dst)
        created.append(str(prof_dst))

    if created:
        print("已生成项目级动态模板：", ", ".join(created))
    else:
        print("项目根已存在 .drama-deai-config.json 与 .drama-deai-profile.md，未覆盖。")
    return 0


def audit_episode(
    path: pathlib.Path, cfg: dict[str, Any], strict_deai: bool = False
) -> tuple[bool, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    fmt = cfg["format_limits"]
    thresh = cfg["deai_thresholds"]
    exempt_prefixes = tuple(cfg.get("exempt_action_prefixes", ["【"]))

    forbidden_words: list[str] = cfg.get("forbidden_words", [])
    forbidden_regex = [
        (item["name"], re.compile(item["pattern"]))
        for item in cfg.get("forbidden_regex", [])
    ]
    max_term_counts: dict[str, int] = cfg.get("max_term_counts", {})

    hard_errs: list[str] = []
    deai_warns: list[str] = []

    scenes = sum(1 for l in lines if l.startswith("[场景]"))
    if scenes > fmt["max_scenes"]:
        hard_errs.append(f"场景数超限: {scenes} > {fmt['max_scenes']}")

    for term, limit in max_term_counts.items():
        cnt = sum(l.count(term) for l in lines)
        if cnt > limit:
            hard_errs.append(f"限频词「{term}」超限: {cnt} > {limit}")

    dlg_chars = 0
    acts = 0
    adv_hits: list[tuple[int, str]] = []
    paren_hits: list[tuple[int, str]] = []
    em_dash_dlg = 0
    filler_hits: list[tuple[int, str]] = []
    binary_hits: list[tuple[int, str]] = []

    for idx, l in enumerate(lines, 1):
        if l.startswith("△ "):
            acts += 1
            body = l[2:].strip()
            if len(body) > fmt["max_action_chars"]:
                hard_errs.append(f"L{idx} △超{fmt['max_action_chars']}字({len(body)}): {body}")
            for w in ACT_ADVERBS:
                if w in body:
                    adv_hits.append((idx, w))
            for w in FICTION_FILLER:
                if w in body:
                    filler_hits.append((idx, w))
        elif "：" in l and not l.startswith(exempt_prefixes) and not l.startswith("["):
            acts_part, dlg = l.split("：", 1)
            if "（" in acts_part:
                pure = re.sub(r"[，。！？、——……“”「」\s]", "", dlg)
                dlg_chars += len(pure)
                clauses = [c for c in re.split(r"[，。！？、——……]", dlg) if c.strip()]
                for c in clauses:
                    if len(c.strip()) > fmt["max_clause_chars"]:
                        hard_errs.append(f"L{idx} 对白分句超{fmt['max_clause_chars']}字({len(c.strip())}): {c}")
                for w in PAREN_CLICHES:
                    if w in acts_part:
                        paren_hits.append((idx, w))
                em_dash_dlg += dlg.count("——")
                m = BINARY_CONTRAST.search(dlg)
                if m:
                    binary_hits.append((idx, m.group(0)))

        if not l.startswith(exempt_prefixes):
            for bw in forbidden_words:
                if bw in l:
                    hard_errs.append(f"L{idx} 禁用词({bw}): {l}")
            for label, pat in forbidden_regex:
                if pat.search(l):
                    hard_errs.append(f"L{idx} 禁用正则({label}): {l}")

    est = dlg_chars / fmt["speech_rate_cps"] + acts * fmt["action_beat_seconds"] + fmt["base_overhead_seconds"]
    if not (fmt["min_est_seconds"] <= est <= fmt["max_est_seconds"]):
        hard_errs.append(
            f"预估时长越界: {est:.1f}s (目标 {fmt['min_est_seconds']}~{fmt['max_est_seconds']}s)"
        )

    heavy_adv = [h for h in adv_hits if h[1] in HEAVY_ADVERBS]
    if len(heavy_adv) > thresh["max_heavy_adverbs"]:
        deai_warns.append(f"强渲染副词偏多({len(heavy_adv)}处>{thresh['max_heavy_adverbs']}): {heavy_adv}")
    if len(paren_hits) > thresh["max_paren_cliches"]:
        deai_warns.append(
            f"万金油括号标签偏密({len(paren_hits)}处>{thresh['max_paren_cliches']}): "
            f"{[f'L{i}:{w}' for i, w in paren_hits]}"
        )
    if em_dash_dlg > thresh["max_em_dash_dlg"]:
        deai_warns.append(f"对白破折号「——」偏密({em_dash_dlg}处>{thresh['max_em_dash_dlg']})")
    if filler_hits:
        deai_warns.append(f"小说套话/不可拍词({len(filler_hits)}处): {filler_hits}")
    if binary_hits:
        deai_warns.append(f"二元对照句式({len(binary_hits)}处): {binary_hits}")

    passed = (len(hard_errs) == 0) and (not strict_deai or len(deai_warns) == 0)
    status = "FAIL" if hard_errs else ("DEAI_REVIEW" if deai_warns else "PASS")
    summary_line = (
        f"{path.stem}: {status} "
        f"| est={est:.1f}s scenes={scenes} acts={acts} dlg={dlg_chars} "
        f"| heavy_adv={len(heavy_adv)} paren_cliche={len(paren_hits)} em_dash={em_dash_dlg} filler={len(filler_hits)}"
    )
    details = [summary_line]
    for e in hard_errs:
        details.append(f"  [HARD] {e}")
    for w in deai_warns:
        details.append(f"  [DEAI] {w}")
    return passed, details


def natural_ep_key(p: pathlib.Path) -> tuple[int, str]:
    m = re.search(r"(\d+)", p.stem)
    return (int(m.group(1)) if m else 999999, p.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Chinese short-drama de-AI & canon auditor.")
    parser.add_argument("files", nargs="*", help="Script markdown files or folders to audit.")
    parser.add_argument("--config", type=pathlib.Path, help="Explicit path to .drama-deai-config.json")
    parser.add_argument("--init", action="store_true", help="Initialize starter profile & config in CWD.")
    parser.add_argument("--strict-deai", action="store_true", help="Exit non-zero on DEAI warnings.")
    args = parser.parse_args()

    if args.init:
        return init_workspace()

    cfg = load_config(args.config)
    targets: list[pathlib.Path] = []
    if args.files:
        for f in args.files:
            p = pathlib.Path(f)
            if p.is_dir():
                targets.extend(sorted(p.glob("*.md"), key=natural_ep_key))
            else:
                targets.append(p)
    else:
        targets = sorted(pathlib.Path.cwd().glob(cfg["script_glob"]), key=natural_ep_key)

    if not targets:
        print("未找到待审计的剧本文件，请传入文件路径或检查 .drama-deai-config.json 的 script_glob。")
        return 1

    any_fail = False
    for t in targets:
        if not t.exists():
            print(f"[MISS] {t}")
            any_fail = True
            continue
        ok, lines = audit_episode(t, cfg, strict_deai=args.strict_deai)
        for line in lines:
            print(line)
        if not ok:
            any_fail = True
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())

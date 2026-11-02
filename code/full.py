#!/usr/bin/env python3
"""Full run: 50 Gorilla File System episodes x 3 arms x 2 budgets.

Reuses the step-0.5 pilot samples via --resume (identical configuration).
Configs run in parallel with modest per-config workers; the harness's own
tenacity retry layer absorbs transient gateway errors.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INEP_DIR = os.path.join(HERE, "repo", "In-Episode-Execution", "INEP-EXEC")
RUNS_ROOT = os.path.join(INEP_DIR, "in_episode_results", "runs")
CONFIGS = [
    ("a0", 16000), ("a0", 128000),
    ("bm25", 16000), ("bm25", 128000),
    ("ace", 16000), ("ace", 128000),
]


def all_ids() -> str:
    path = os.path.join(INEP_DIR, "bfcl_eval", "scripts", "in_episode", "ids", "ids_gorilla_fs.json")
    return ",".join(json.load(open(path))["multi_turn_ours"])


def main() -> int:
    ids = all_ids()
    procs = {}
    for arm, budget in CONFIGS:
        out_dir = os.path.join(RUNS_ROOT, f"{arm}_{budget // 1000}k")
        log_path = os.path.join(HERE, f"full_{arm}_{budget // 1000}k.log")
        log = open(log_path, "w")
        cmd = [
            sys.executable, os.path.join(HERE, "run_one.py"),
            "--arm", arm, "--budget", str(budget), "--ids", ids,
            "--output-dir", out_dir, "--workers", "3", "--resume",
        ]
        procs[(arm, budget)] = (subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log_path)
        print(f"launched {arm} @ {budget} -> {log_path}", flush=True)
    rc_all = 0
    for (arm, budget), (proc, log_path) in procs.items():
        rc = proc.wait()
        print(f"finished {arm} @ {budget}: exit={rc} (log {log_path})", flush=True)
        rc_all = rc_all or rc
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())

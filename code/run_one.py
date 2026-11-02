#!/usr/bin/env python3
"""Run one EvoMemBench InEp-Exec arm/budget config against an
OpenAI-compatible gateway.

Configuration comes from the environment: EVOMEM_BASE_URL (the gateway's
OpenAI-compatible base URL), OPENAI_API_KEY (the gateway credential) and
EVOMEM_INEP_DIR (path to the pinned INEP-EXEC suite). The credential is
placed only in the child process environment. Protocol flags mirror the
authors' official run scripts exactly (FC mode, long-context noise on,
per-sample memory scope).
"""
import argparse
import os
import subprocess
import sys

INEP_DIR = os.environ.get("EVOMEM_INEP_DIR", "./INEP-EXEC")
VENV_PY = os.path.join(INEP_DIR, ".venv", "bin", "python")
BASE_URL = os.environ.get("EVOMEM_BASE_URL", "")
MODEL = "gpt-6-luna"


def build_env(arm: str, api_key: str) -> dict:
    env = dict(os.environ)
    pairs = [
        ("OPENAI_BASE_URL", BASE_URL),
        ("BATCH_MODEL", MODEL),
        ("PYTHONUNBUFFERED", "1"),
    ]
    if arm == "a0":
        pairs += [
            ("BATCH_BACKEND", "gpt5mini"),
            ("OPENAI_API_KEY", api_key),
            ("GPT5MINI_API_KEY", api_key),
            ("GPT5MINI_BASE_URL", BASE_URL),
            ("BATCH_MODEL_GPT5MINI", MODEL),
        ]
    else:
        pairs += [
            ("EVOMEM_TRANSPORT", "openai"),
            ("DEEPSEEK_API_KEY", api_key),
        ]
    env.update(pairs)
    return env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["a0", "bm25", "ace"], required=True)
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--run-name", default="gorilla_fs")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    api_key = os.environ["OPENAI_API_KEY"]
    env = build_env(args.arm, api_key)

    cmd = [
        VENV_PY, "-m", "bfcl_eval.scripts.in_episode.run_batch_eval",
        "--num-workers", str(args.workers),
        "--output-dir", args.output_dir,
        "--run-name", args.run_name,
        "--context-budget", str(args.budget),
        "--mode", "FC",
        "--ids", args.ids,
        "--long-context",
    ]
    if args.arm == "bm25":
        cmd += ["--memory-type", "bm25", "--memory-scope", "sample", "--memory-top-k", "3"]
    elif args.arm == "ace":
        cmd += ["--memory-type", "ace", "--memory-scope", "sample"]
    if args.resume:
        cmd += ["--resume"]

    print(f"[run_one] arm={args.arm} budget={args.budget} ids={args.ids.count(',') + 1} "
          f"out={args.output_dir}/{args.run_name} resume={args.resume}", flush=True)
    proc = subprocess.run(cmd, cwd=INEP_DIR, env=env)
    print(f"[run_one] exit={proc.returncode}", flush=True)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

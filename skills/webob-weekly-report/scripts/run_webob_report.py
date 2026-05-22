#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


WORKSPACE = Path("/Users/zhoumeng/Documents/Codex/2026-04-24/new-chat")
OUTPUT = WORKSPACE / "output"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(WORKSPACE / script), *args], cwd=WORKSPACE, check=True)


def run_skill_script(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / script), *args], cwd=WORKSPACE, check=True)


def qiwei_markdown(funnel: Path, business: Path) -> str:
    load_dotenv(WORKSPACE / ".env")
    feishu_url = os.environ.get("FEISHU_BITABLE_URL", "https://bqwrbbbbtoc.feishu.cn/wiki/BEN0weeYJiKs01kIkHnc4DNtnvd")
    pull_time = os.environ.get("WEBOB_REPORT_TODAY") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return "\n".join(
        [
            "# WebOB 周报数据已更新",
            f"> 拉取时间：{pull_time}",
            f"> 飞书多维表格：{feishu_url}",
        ]
    )


def send_qiwei(funnel: Path, business: Path) -> None:
    load_dotenv(WORKSPACE / ".env")
    webhook = os.environ.get("QIWEI_WEBHOOK_URL")
    if not webhook:
        raise SystemExit("Missing QIWEI_WEBHOOK_URL in .env")
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": qiwei_markdown(funnel, business)},
    }
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    if data.get("errcode") != 0:
        raise SystemExit(f"Qiwei webhook failed: {body}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate WebOB weekly report TSVs")
    parser.add_argument("--sync-feishu", action="store_true", help="Sync generated data to Feishu Bitable")
    parser.add_argument("--cleanup-empty", action="store_true", help="Delete empty Feishu records created before fields existed")
    parser.add_argument("--send-qiwei", action="store_true", help="Send a short summary and Feishu link to the configured Qiwei webhook")
    parser.add_argument("--today", help="Simulated run date, YYYY-MM-DD. Defaults to actual today.")
    parser.add_argument("--auth", choices=("openapi",), default="openapi", help="Sensors auth mode. Only OpenAPI/API Key is supported.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.today:
        os.environ["WEBOB_REPORT_TODAY"] = args.today
    if args.auth:
        os.environ["SENSORS_AUTH_MODE"] = args.auth
    timestamp_prefix = args.today.replace("-", "") if args.today else datetime.now().strftime("%Y%m%d")
    timestamp = f"{timestamp_prefix}_{datetime.now().strftime('%H%M%S')}"

    generator_args = ["--today", args.today] if args.today else []
    run("generate_webob_weekly_summary.py", *generator_args)
    run("generate_webob_business_summary.py", *generator_args)

    funnel = OUTPUT / "webob_summary.tsv"
    business = OUTPUT / "webob_business_summary.tsv"
    funnel_named = OUTPUT / f"funnel指标_{timestamp}.tsv"
    business_named = OUTPUT / f"业务指标_{timestamp}.tsv"

    shutil.copyfile(funnel, funnel_named)
    shutil.copyfile(business, business_named)

    print(f"funnel={funnel_named}")
    print(f"business={business_named}")
    if args.sync_feishu:
        feishu_args = ["--funnel", str(funnel_named), "--business", str(business_named)]
        if args.cleanup_empty:
            feishu_args.append("--cleanup-empty")
        run_skill_script("feishu_bitable_sync.py", *feishu_args)
        print("feishu=synced")
    if args.send_qiwei:
        send_qiwei(funnel_named, business_named)
        print("qiwei=sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

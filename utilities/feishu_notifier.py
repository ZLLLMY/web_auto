"""
飞书通知模块
- 测试结束后发送汇总消息卡片到飞书群
"""

import requests


# ---------------------------------------------------------------------------
# 消息卡片构建
# ---------------------------------------------------------------------------

def _build_stat_columns(total, passed, failed, skipped, duration_str):
    """构建统计数字的四列布局。"""
    return [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**总计**\n{total}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"✅ **通过**\n{passed}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"❌ **失败**\n{failed}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"⏱ **耗时**\n{duration_str}"}},
    ]


def _build_failed_section(failed_cases):
    """构建失败用例详情段落。"""
    lines = []
    for i, case in enumerate(failed_cases, 1):
        error_msg = case.get("error_message", "未知错误")
        if len(error_msg) > 150:
            error_msg = error_msg[:150] + "..."
        lines.append(
            f"**{i}. {case['name']}**\n"
            f"失败原因：{error_msg}\n"
            f"阶段：{case.get('stage', 'call')}"
        )
    return "\n\n".join(lines)


def _build_passed_section(passed_names):
    """构建通过用例简略列表。"""
    if not passed_names:
        return "无"
    if len(passed_names) <= 10:
        return " / ".join(passed_names)
    return " / ".join(passed_names[:10]) + f" ...等共{len(passed_names)}条"


def build_card_payload(
    total, passed, failed, skipped, duration_str,
    failed_cases, passed_names,
    env_name, browser_name, timestamp_str,
):
    """构建飞书消息卡片 JSON payload。"""
    has_failure = failed > 0

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": (
                    f"{'❌' if has_failure else '✅'} Web自动化测试报告  "
                    f"{passed}通过{' / ' + str(failed) + '失败' if has_failure else ''}"
                ),
            },
            "template": "red" if has_failure else "green",
        },
        "elements": [
            {
                "tag": "column_set",
                "flex_mode": "bisect",
                "background_style": "default",
                "columns": _build_stat_columns(total, passed, failed, skipped, duration_str),
            },
            {"tag": "hr"},
        ],
    }

    # --- 失败用例详情 ---
    if failed_cases:
        card["elements"].append({
            "tag": "markdown",
            "content": (
                f"**❌ 失败用例（{len(failed_cases)}条）：**\n"
                f"{_build_failed_section(failed_cases)}"
            ),
        })

    # --- 通过用例 ---
    if passed_names:
        card["elements"].append({
            "tag": "markdown",
            "content": (
                f"**✅ 通过用例（{len(passed_names)}条）：**\n"
                f"{_build_passed_section(passed_names)}"
            ),
        })

    # --- 跳过用例 ---
    if skipped > 0:
        card["elements"].append({
            "tag": "markdown",
            "content": f"**⏭ 跳过用例：** {skipped}条",
        })

    # --- 页脚 ---
    card["elements"].append({"tag": "hr"})
    card["elements"].append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": (
                    f"环境: {env_name.upper()} | "
                    f"浏览器: {browser_name.title()} | "
                    f"{timestamp_str}"
                ),
            }
        ],
    })

    return {"msg_type": "interactive", "card": card}


def send_card(webhook_url, payload):
    """发送消息卡片到飞书群机器人。"""
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        data = resp.json()
        if data.get("code") == 0:
            print("[飞书] 消息卡片发送成功")
            return True
        else:
            print(f"[飞书] 消息卡片发送失败: {data}")
            return False
    except Exception as e:
        print(f"[飞书] 消息卡片发送异常: {e}")
        return False


# ---------------------------------------------------------------------------
# 顶层入口
# ---------------------------------------------------------------------------

def notify_test_result(feishu_config, test_summary):
    """根据配置发送测试结果汇总卡片到飞书群。

    Parameters
    ----------
    feishu_config : dict
        enabled, webhook_url, send_mode
    test_summary : dict
        total, passed, failed, skipped, duration_str,
        failed_cases, passed_names,
        env_name, browser_name, timestamp_str
    """
    if not feishu_config.get("enabled", False):
        print("[飞书] 通知功能未启用，跳过")
        return

    send_mode = feishu_config.get("send_mode", "on_failure")
    failed = test_summary.get("failed", 0)

    if send_mode == "never":
        print("[飞书] send_mode=never，跳过发送")
        return
    if send_mode == "on_failure" and failed == 0:
        print("[飞书] send_mode=on_failure 且无失败用例，跳过发送")
        return

    webhook_url = feishu_config.get("webhook_url", "")
    if not webhook_url:
        print("[飞书] webhook_url 为空，无法发送")
        return

    payload = build_card_payload(
        total=test_summary.get("total", 0),
        passed=test_summary.get("passed", 0),
        failed=failed,
        skipped=test_summary.get("skipped", 0),
        duration_str=test_summary.get("duration_str", "N/A"),
        failed_cases=test_summary.get("failed_cases", []),
        passed_names=test_summary.get("passed_names", []),
        env_name=test_summary.get("env_name", ""),
        browser_name=test_summary.get("browser_name", ""),
        timestamp_str=test_summary.get("timestamp_str", ""),
    )
    send_card(webhook_url, payload)

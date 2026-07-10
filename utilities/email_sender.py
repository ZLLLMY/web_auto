"""
邮件发送模块
- 失败用例截图打包通过 SMTP 发送到指定邮箱
"""

import os
import smtplib
import zipfile
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def _zip_screenshots(screenshot_dir, failed_cases):
    """把失败截图打包成 ZIP，返回 ZIP 文件路径。"""
    os.makedirs("temp", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join("temp", f"failed_screenshots_{timestamp}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        all_files = os.listdir(screenshot_dir)
        added = 0
        for case in failed_cases:
            case_name = case["name"]
            matched = sorted(
                [f for f in all_files if f.startswith(f"{case_name}_failure") and f.endswith(".png")],
                reverse=True,
            )
            for filename in matched:
                file_path = os.path.join(screenshot_dir, filename)
                zf.write(file_path, filename)
                added += 1
                print(f"[邮件] 打包截图: {filename}")

    if added == 0:
        os.remove(zip_path)
        return None

    print(f"[邮件] ZIP 打包完成: {zip_path} ({added}张截图)")
    return zip_path


def _build_email_body(test_summary):
    """构建 HTML 邮件正文。"""
    total = test_summary.get("total", 0)
    passed = test_summary.get("passed", 0)
    failed = test_summary.get("failed", 0)
    skipped = test_summary.get("skipped", 0)
    duration = test_summary.get("duration_str", "N/A")
    env_name = test_summary.get("env_name", "").upper()
    browser = test_summary.get("browser_name", "").title()
    timestamp = test_summary.get("timestamp_str", "")
    failed_cases = test_summary.get("failed_cases", [])

    # 失败用例表格行
    failed_rows = ""
    if failed_cases:
        for i, case in enumerate(failed_cases, 1):
            error = case.get("error_message", "未知错误")
            if len(error) > 200:
                error = error[:200] + "..."
            failed_rows += f"""
                <tr>
                    <td style="color:#e74c3c; font-weight:bold;">❌ {case['name']}</td>
                    <td>{error}</td>
                    <td>{case.get('stage', 'call')}</td>
                </tr>"""

    color = "#e74c3c" if failed > 0 else "#27ae60"
    emoji = "❌" if failed > 0 else "✅"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: 'Microsoft YaHei', Arial, sans-serif; background:#f5f6fa; padding:30px;">
<div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08);">

  <div style="background:{color}; padding:24px; text-align:center;">
    <h1 style="color:#fff; margin:0; font-size:20px;">{emoji} Web自动化测试报告</h1>
    <p style="color:rgba(255,255,255,0.85); margin:8px 0 0; font-size:14px;">
      {passed}通过{' / ' + str(failed) + '失败' if failed > 0 else ''}
    </p>
  </div>

  <div style="padding:24px;">
    <table style="width:100%; border-collapse:collapse; margin-bottom:24px;">
      <tr>
        <td style="text-align:center; padding:12px; background:#f0f9ff; border-radius:6px;">
          <div style="font-size:24px; font-weight:bold; color:#2c3e50;">{total}</div>
          <div style="font-size:12px; color:#7f8c8d;">总计</div>
        </td>
        <td style="text-align:center; padding:12px; background:#f0fff4; border-radius:6px;">
          <div style="font-size:24px; font-weight:bold; color:#27ae60;">{passed}</div>
          <div style="font-size:12px; color:#7f8c8d;">✅ 通过</div>
        </td>
        <td style="text-align:center; padding:12px; background:#fff5f5; border-radius:6px;">
          <div style="font-size:24px; font-weight:bold; color:#e74c3c;">{failed}</div>
          <div style="font-size:12px; color:#7f8c8d;">❌ 失败</div>
        </td>
        <td style="text-align:center; padding:12px; background:#f8f9fa; border-radius:6px;">
          <div style="font-size:24px; font-weight:bold; color:#2c3e50;">{duration}</div>
          <div style="font-size:12px; color:#7f8c8d;">⏱ 耗时</div>
        </td>
      </tr>
    </table>
"""

    + (f"""
    <h3 style="color:#e74c3c; margin-top:20px;">❌ 失败用例（{len(failed_cases)}条）</h3>
    <table style="width:100%; border-collapse:collapse; font-size:13px;">
      <tr style="background:#fff5f5;">
        <th style="padding:10px; text-align:left; border-bottom:2px solid #e74c3c;">用例名</th>
        <th style="padding:10px; text-align:left; border-bottom:2px solid #e74c3c;">失败原因</th>
        <th style="padding:10px; text-align:left; border-bottom:2px solid #e74c3c;">阶段</th>
      </tr>
      {failed_rows}
    </table>
    """ if failed_cases else """<p style="color:#27ae60; font-weight:bold;">✅ 所有用例全部通过！</p>""")

    + f"""
    <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
    <p style="font-size:12px; color:#95a5a6; text-align:center;">
      环境: {env_name} | 浏览器: {browser} | {timestamp}<br>
      失败截图见附件 ZIP
    </p>
  </div>
</div>
</body></html>"""


def send_screenshots_email(email_config, test_summary):
    """将失败截图打包发送到邮箱。

    Parameters
    ----------
    email_config : dict
        smtp_server, smtp_port, sender, password, receivers, enabled, send_mode
    test_summary : dict
        同 feishu_notifier 的 test_summary 结构。
    """
    if not email_config.get("enabled", False):
        print("[邮件] 邮箱通知未启用，跳过")
        return

    send_mode = email_config.get("send_mode", "on_failure")
    failed = test_summary.get("failed", 0)

    if send_mode == "never":
        print("[邮件] send_mode=never，跳过发送")
        return
    if send_mode == "on_failure" and failed == 0:
        print("[邮件] send_mode=on_failure 且无失败用例，跳过发送")
        return

    screenshot_dir = test_summary.get("screenshot_dir", "")
    failed_cases = test_summary.get("failed_cases", [])

    # ---- 打包截图（仅失败时） ----
    zip_path = None
    if failed > 0 and screenshot_dir and os.path.isdir(screenshot_dir):
        zip_path = _zip_screenshots(screenshot_dir, failed_cases)

    # ---- 构建邮件 ----
    smtp_server = email_config.get("smtp_server", "")
    smtp_port = email_config.get("smtp_port", 465)
    sender = email_config.get("sender", "")
    password = email_config.get("password", "")
    receivers = email_config.get("receivers", [])

    if not all([smtp_server, sender, password, receivers]):
        print("[邮件] 邮箱配置不完整，跳过发送")
        if zip_path:
            os.remove(zip_path)
        return

    has_failure = failed > 0
    env = test_summary.get("env_name", "").upper()
    total = test_summary.get("total", 0)
    passed = test_summary.get("passed", 0)
    subject = (
        f"{'❌' if has_failure else '✅'} Web自动化测试报告 - {env} "
        f"({passed}通过{' / ' + str(failed) + '失败' if has_failure else ' 全部通过'}/{total}总)"
    )

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject

    # HTML 正文
    html_body = _build_email_body(test_summary)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # ZIP 附件
    if zip_path:
        zip_filename = os.path.basename(zip_path)
        with open(zip_path, "rb") as f:
            attachment = MIMEBase("application", "zip")
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=("utf-8", "", zip_filename),
            )
            msg.attach(attachment)

    # ---- 发送 ----
    try:
        print(f"[邮件] 正在发送到 {', '.join(receivers)} ...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        print("[邮件] 发送成功！")
    except Exception as e:
        print(f"[邮件] 发送失败: {e}")
    finally:
        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"[邮件] 清理临时文件: {zip_path}")

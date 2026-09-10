import email.utils
import requests
import json
import urllib.parse
import hmac
import hashlib
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime, timezone
import pytz
from typing import List


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 0:
        return "0秒"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if secs > 0 or not parts:
        parts.append(f"{secs}秒")
    return "".join(parts)


def send_test_report_email(
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_addr: str,
        to_addrs: List[str],
        report_url: str,
        project_name: str,
        env_name: str,
        case_rate: float,
        case_all: int,
        case_pass: int,
        case_fail: int,
        report_title: str,
        start_time: datetime,
        end_time: datetime,
        subject_prefix: str = "测试报告"
):
    """
    发送测试报告邮件（HTML格式，样式清晰，支持外部浏览器打开链接）
    """
    try:
        # 时区转换
        beijing_tz = pytz.timezone('Asia/Shanghai')
        if start_time.tzinfo is None:
            start_utc = start_time.replace(tzinfo=timezone.utc)
            end_utc = end_time.replace(tzinfo=timezone.utc)
        else:
            start_utc = start_time.astimezone(timezone.utc)
            end_utc = end_time.astimezone(timezone.utc)
        start_local = start_utc.astimezone(beijing_tz)
        end_local = end_utc.astimezone(beijing_tz)

        duration_seconds = (end_local - start_local).total_seconds()
        duration_str = format_duration(duration_seconds)
        percent = case_rate * 100
        start_str = start_local.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_local.strftime("%Y-%m-%d %H:%M:%S")

        if percent == 100.0:
            pass_rate_display = "100% 🎉"
        else:
            pass_rate_display = f"{percent:.1f}%"

        # 构建 HTML 正文
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #1f2d3d;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f5f7fa;
                    border-radius: 8px;
                    padding: 24px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                h1 {{
                    color: #1e6f3f;
                    border-left: 4px solid #1e6f3f;
                    padding-left: 16px;
                    margin-top: 0;
                }}
                h2 {{
                    color: #2c3e50;
                    margin: 24px 0 12px 0;
                    padding-bottom: 6px;
                    border-bottom: 2px solid #e2e8f0;
                }}
                .info-block {{
                    background-color: #ffffff;
                    border-radius: 6px;
                    padding: 16px;
                    margin: 16px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .info-item {{
                    margin: 8px 0;
                }}
                .info-label {{
                    font-weight: 600;
                    display: inline-block;
                    width: 100px;
                }}
                .stat-grid {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                    margin: 16px 0;
                }}
                .stat-card {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 12px 20px;
                    flex: 1;
                    min-width: 120px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #1e6f3f;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #5a6e7c;
                }}
                .pass-rate {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1e6f3f;
                }}
                .button {{
                    display: inline-block;
                    background-color: #1e6f3f;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 16px 0;
                }}
                .footer {{
                    margin-top: 32px;
                    font-size: 12px;
                    color: #8a9aa8;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 16px;
                }}
                hr {{
                    margin: 24px 0;
                    border: none;
                    border-top: 1px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 {report_title}</h1>

                <h2>📋 基础信息</h2>
                <div class="info-block">
                    <div class="info-item"><span class="info-label">📦 所属项目：</span>{project_name}</div>
                    <div class="info-item"><span class="info-label">🌍 执行环境：</span>{env_name}</div>
                    <div class="info-item"><span class="info-label">🕘 开始时间：</span>{start_str}</div>
                    <div class="info-item"><span class="info-label">🕔 结束时间：</span>{end_str}</div>
                    <div class="info-item"><span class="info-label">⌛ 执行耗时：</span>{duration_str}</div>
                </div>

                <h2>📊 执行结果</h2>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-number">{case_all}</div>
                        <div class="stat-label">📋 总用例数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{case_pass}</div>
                        <div class="stat-label">✅ 成功用例数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{case_fail}</div>
                        <div class="stat-label">❌ 失败用例数</div>
                    </div>
                </div>
                <div style="text-align: center; margin: 16px 0;">
                    <span class="pass-rate">📈 通过率：{pass_rate_display}</span>
                </div>

                <hr>
                <div style="text-align: center;">
                    <a href="{report_url}" class="button" target="_blank">📄 查看详细报告</a>
                </div>

                <div class="footer">
                    自动化测试机器人 · {datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")}
                </div>
            </div>
        </body>
        </html>
        """

        # 构建邮件
        subject = f"{subject_prefix} - {report_title}"
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = from_addr
        msg['To'] = ','.join(to_addrs)
        msg['Date'] = email.utils.formatdate()

        # 附上 HTML 内容
        part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part)

        # 发送邮件
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, to_addrs, msg.as_string())

        print("✅ 邮件发送成功")
        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False


def sign_dingtalk_webhook(webhook_url: str, secret: str) -> str:
    """对钉钉 webhook 进行签名"""
    timestamp = str(round(datetime.now().timestamp() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return f"{webhook_url}&timestamp={timestamp}&sign={sign}"


def send_dingtalk_message(webhook_url: str, report_url: str, project_name: str, env_name: str,
                          case_rate: float, case_all: int, case_pass: int, case_fail: int,
                          report_title: str, start_time: datetime, end_time: datetime, secret: str = None):
    try:
        # 时区转换
        beijing_tz = pytz.timezone('Asia/Shanghai')
        if start_time.tzinfo is None:
            start_utc = start_time.replace(tzinfo=timezone.utc)
            end_utc = end_time.replace(tzinfo=timezone.utc)
        else:
            start_utc = start_time.astimezone(timezone.utc)
            end_utc = end_time.astimezone(timezone.utc)
        start_local = start_utc.astimezone(beijing_tz)
        end_local = end_utc.astimezone(beijing_tz)

        duration_seconds = (end_local - start_local).total_seconds()
        duration_str = format_duration(duration_seconds)
        percent = case_rate * 100
        start_str = start_local.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_local.strftime("%Y-%m-%d %H:%M:%S")

        # 通过率显示
        if percent == 100.0:
            pass_rate_display = "100% 🎉"
        else:
            pass_rate_display = f"{percent:.1f}%"

        # 构建 actionCard 文本内容
        card_text = f"""# 🚀 {report_title}

---

## 📋 基础信息

&nbsp;

-  📦  **所属项目**：{project_name}
-  🌍  **执行环境**：{env_name}
-  🕘  **开始时间**：{start_str}
-  🕔  **结束时间**：{end_str}
-  ⌛  **执行耗时**：{duration_str}

&nbsp;

---

## 📊 执行结果

&nbsp;

-  📋  **总用例数**：{case_all} 个
-  ✅  **成功用例数**：{case_pass} 个
-  ❌  **失败用例数**：{case_fail} 个
-  📈  **通过率**：{pass_rate_display}
"""

        # 关键修复：使用钉钉统一跳转协议，强制在外部浏览器打开
        # 对原始 URL 进行编码
        encoded_url = urllib.parse.quote(report_url, safe='')
        # 构建协议链接
        browser_url = f"dingtalk://dingtalkclient/page/link?url={encoded_url}&pc_slide=false"

        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": f"测试报告 - {report_title}",
                "text": card_text,
                "hideAvatar": "0",
                "btnOrientation": "0",
                "singleTitle": "📄 查看详细报告",
                "singleURL": browser_url,   # 使用协议链接
                "pc_slide": False           # 同时保留此参数作为兼容
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'QM-TestPlatform/1.0'
        }

        final_url = webhook_url
        if secret is not None:
            final_url = sign_dingtalk_webhook(webhook_url, secret)

        response = requests.post(
            final_url,
            headers=headers,
            data=json.dumps(data),
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 发送超时")
        return False
    except Exception as e:
        print(f"❌ 发送异常: {str(e)}")
        return False


def sign_feishu_webhook(webhook_url: str, secret: str) -> str:
    """对飞书 webhook 进行签名"""
    timestamp = str(int(datetime.now().timestamp()))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return f"{webhook_url}&timestamp={timestamp}&sign={sign}"


def send_feishu_message(webhook_url: str, report_url: str, project_name: str, env_name: str,
                        case_rate: float, case_all: int, case_pass: int, case_fail: int,
                        report_title: str, start_time: datetime, end_time: datetime, secret: str = None):
    """
    推送飞书测试报告（卡片消息，支持外部浏览器打开）
    """
    try:
        # 时区转换
        beijing_tz = pytz.timezone('Asia/Shanghai')
        if start_time.tzinfo is None:
            start_utc = start_time.replace(tzinfo=timezone.utc)
            end_utc = end_time.replace(tzinfo=timezone.utc)
        else:
            start_utc = start_time.astimezone(timezone.utc)
            end_utc = end_time.astimezone(timezone.utc)
        start_local = start_utc.astimezone(beijing_tz)
        end_local = end_utc.astimezone(beijing_tz)

        duration_seconds = (end_local - start_local).total_seconds()
        duration_str = format_duration(duration_seconds)
        percent = case_rate * 100
        start_str = start_local.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_local.strftime("%Y-%m-%d %H:%M:%S")

        if percent == 100.0:
            pass_rate_display = "100% 🎉"
        else:
            pass_rate_display = f"{percent:.1f}%"

        # 构建飞书卡片内容（JSON格式）
        card = {
            "config": {
                "wide_screen_mode": True,   # 使用宽屏模式
                "enable_forward": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🚀 {report_title}"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "📋 基础信息\n"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📦 所属项目**：{project_name}\n"
                                   f"**🌍 执行环境**：{env_name}\n"
                                   f"**🕘 开始时间**：{start_str}\n"
                                   f"**🕔 结束时间**：{end_str}\n"
                                   f"**⌛ 执行耗时**：{duration_str}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "📊 执行结果\n"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📋 总用例数**：{case_all} 个\n"
                                   f"**✅ 成功用例数**：{case_pass} 个\n"
                                   f"**❌ 失败用例数**：{case_fail} 个\n"
                                   f"**📈 通过率**：{pass_rate_display}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "📄 查看详细报告"
                            },
                            "type": "default",
                            "multi_url": {
                                "url": report_url,                # 移动端/钉钉内置打开
                                "pc_url": report_url,             # PC端外部浏览器打开
                                "android_url": report_url,
                                "ios_url": report_url
                            }
                        }
                    ]
                }
            ]
        }

        data = {
            "msg_type": "interactive",
            "card": card
        }

        headers = {
            'Content-Type': 'application/json'
        }

        final_url = webhook_url
        if secret is not None:
            final_url = sign_feishu_webhook(webhook_url, secret)

        response = requests.post(
            final_url,
            headers=headers,
            data=json.dumps(data),
            timeout=10,
            verify=False
        )

        if response.status_code == 200:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 发送失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 发送异常: {str(e)}")
        return False


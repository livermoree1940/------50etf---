import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_email_if_signal(message, image_path=None):
    sender = os.getenv("QQ_EMAIL")
    password = os.getenv("AUTH_CODE")
    receiver = os.getenv("RECEIVER")

    logger.info(f"邮件配置检查 - 发件人: {sender}, 收件人: {receiver}")

    if not sender or not password or not receiver:
        logger.error("❌ 缺少邮件环境变量（QQ_EMAIL / AUTH_CODE / RECEIVER）")
        return False

    try:
        # 创建邮件内容
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "【股票买入信号提醒】"
        msg.attach(MIMEText(message, "plain", "utf-8"))

        # 添加图片附件
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    img = MIMEApplication(f.read())
                    img.add_header("Content-Disposition", "attachment", filename=os.path.basename(image_path))
                    msg.attach(img)
                logger.info(f"✅ 成功添加图片附件: {os.path.basename(image_path)}")
            except Exception as e:
                logger.error(f"❌ 添加图片附件失败: {e}")

        # 使用SMTP_SSL发送邮件
        logger.info("尝试使用 SMTP_SSL 连接...")
        with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30) as server:
            server.login(sender, password)
            server.send_message(msg)
            logger.info("📩 邮件发送成功！(SMTP_SSL)")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP认证失败: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        logger.error(f"❌ SMTP连接失败: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"❌ SMTP服务器断开连接: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 邮件发送过程中发生异常: {e}")
        return False
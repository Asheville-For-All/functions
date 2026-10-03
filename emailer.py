import smtplib
from email.message import EmailMessage

def send_email(usr, pw, sender, recipients, subject, html_content, smtpAddress, bcc=None, cc=None):

    wrapper_front = """<!doctype html><html lang="en"><body style="background-color:white; color:#505050;"><div style="background-color:white; color:#505050; font-family: -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, Adwaita Sans, Cantarell, Ubuntu, roboto, noto, helvetica, arial, sans-serif;font-size: 14px;line-height: 150%;max-width:42em;left-margin:auto;right-margin:auto;">"""

    wrapper_back = """</div></body></html>"""

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients

    if bcc != None and bcc != "" and len(bcc) > 0:
        msg['Bcc'] = bcc
    if cc != None and cc != "" and len(cc) > 0:
        msg['Cc'] = cc

    msg.set_content(wrapper_front + html_content + wrapper_back, subtype="html")

    with smtplib.SMTP_SSL(smtpAddress, 465) as smtp:
        smtp.login(usr, pw) 
        smtp.send_message(msg)
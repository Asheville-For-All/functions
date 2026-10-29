import smtplib
from email.message import EmailMessage
import pytz
from cal_links import get_calendar_links

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

        try:
            smtp.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            print("ERROR: Server unexpectedly disconnected. Try increasing the timeout or checking the connection details.")
        except smtplib.SMTPException as e:
            print(f"ERROR: An SMTP error occurred: {e}")
        except Exception as e:
            print(f"A general error occurred: {e}")
        else:
            if type(recipients) == list:
                print(f"Email to {', '.join(recipients)} sent successfully.")
            else:
                print(f"Email to f{recipients} sent successfully.")

def send_event_rsvp_confirmation(event_info: dict, usr, pw, sender, recipients, smtpAddress, bcc=None, cc=None):

    content = "<p>Thank for your RSVP! We look forward to seeing you.</p><p>Here is the event information:</p>"

    content += build_event_info_html(event_info)

    content += build_cal_links_html(event_info)

    send_email(usr, pw, sender, recipients, "Thank you for your RSVP", content, smtpAddress)

def send_event_reminder_email(event_info: dict, usr, pw, sender, recipients, smtpAddress, bcc=None, cc=None, topper=False):

    subject = "Your Event Is Coming Up"
    
    content = "<p>We look forward to seeing you! Here is the event information:</p>"
    content += build_event_info_html(event_info)

    if topper:
        content += "<p><b>How will you know how to find us?</b> Look for the small “table topper” that says “Asheville For All”!</p>"

    content += build_cal_links_html(event_info)

    send_email(usr, pw, sender, recipients, subject, content, smtpAddress)

def build_cal_links_html(event_info: dict) -> str:

    cal_links = get_calendar_links({
        "title": event_info.get("title"),
        "start_time": event_info.get("start"),
        "end_time": event_info.get("end"),
        "location": event_info.get("location"),
        "timezone": "America/New_York"    
    })

    content = "<h2>Add to Calendar:</h2><p>"

    for key, val in cal_links.items():
        if key != "ics" and key != "apple":
            content += f"<span style='background-color:gray;color:white;border-radius:4px;padding:4px;'><a href='{val}' style='color:white;'>{key.upper()}</a></span> "

    content += "</p>"

    return content

def build_event_info_html(event_info: dict) -> str:
    
    tz = pytz.timezone('America/New_York')

    adjusted_start = event_info.get("start").astimezone(tz)
    adjusted_end = event_info.get("end").astimezone(tz)

    content = f"<p><em>{event_info.get("title")}<br/>{event_info.get("location")}<br/>{adjusted_start.strftime("%a, %b %-d, %Y")}<br/>{adjusted_start.strftime("%I:%M %p")}-{adjusted_end.strftime("%I:%M %p")}</em></p>"

    return content
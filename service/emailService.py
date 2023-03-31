import cgi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from PIL import Image
import numpy as np
import os
import smtplib

# from_user = "anil.kumar.ait09@gmail.com"
# from_pwd = "pw"
# final_path_current = "path/to/folder/with/images"
# receive_mail = "anil.kumar.ait09@gmail.com"

from customLogging.customLogging import get_logger

logger = get_logger("Motion Detection")


def attach_image(image_path):
    logger.info("image dict: {0}".format(image_path))
    with open(image_path, 'rb') as file:
        msg_image = MIMEImage(file.read())
    return msg_image


def generate_email(from_user, to_list, numpy_image):
    msg = MIMEMultipart('related')
    msg['Subject'] = Header(u'Subject', 'utf-8')
    msg['From'] = from_user
    msg['To'] = ','.join(to_list)
    msg_alternative = MIMEMultipart('alternative')
    msg_text = MIMEText(u'Image not working', 'plain', 'utf-8')
    msg_alternative.attach(msg_text)
    msg.attach(msg_alternative)
    msg_html = u'<h1>Below are the images</h1>'
    msg_html = MIMEText(msg_html, 'html', 'utf-8')
    msg_alternative.attach(msg_html)
    # msg.attach(attach_image(image_path))
    msg.attach(MIMEImage(Image.fromarray(np.uint8(numpy_image)).convert('RGB')))
    return msg


def send_email(msg, from_user, from_pwd, to_list):
    mail_server = smtplib.SMTP('smtp-relay.sendinblue.com', 587)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(from_user, from_pwd)
    mail_server.sendmail(from_user, to_list, msg.as_string())
    mail_server.quit()

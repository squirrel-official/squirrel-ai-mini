import cgi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import os
import smtplib

# from_user = "anil.kumar.ait09@gmail.com"
# from_pwd = "pw"
# final_path_current = "path/to/folder/with/images"
# receive_mail = "anil.kumar.ait09@gmail.com"


def attach_image(img_dict):
    with open(img_dict['path'], 'rb') as file:
        msg_image = MIMEImage(file.read(), name=os.path.basename(img_dict['path']))
    msg_image.add_header('Content-ID', '<{}>'.format(img_dict['cid']))
    return msg_image


def generate_email(from_user, to_list, img_dict):
    msg = MIMEMultipart('related')
    msg['Subject'] = Header(u'Subject', 'utf-8')
    msg['From'] = from_user
    msg['To'] = ','.join(to_list)
    msg_alternative = MIMEMultipart('alternative')
    msg_text = MIMEText(u'Image not working', 'plain', 'utf-8')
    msg_alternative.attach(msg_text)
    msg.attach(msg_alternative)
    msg_html = u'<h1>Below are the images</h1>'
    for img in img_dict:
        msg_html += u'<h3>' + img["title"][
                              :-4] + '</h3><div dir="ltr">''<img src="cid:{cid}" alt="{alt}"><br></div>'.format(
            alt=cgi.escape(img['title'], quote=True), **img)
    msg_html = MIMEText(msg_html, 'html', 'utf-8')
    msg_alternative.attach(msg_html)
    for img in img_dict:
        msg.attach(attach_image(img))

    return msg


def send_email(msg, from_user, from_pwd, to_list):
    mail_server = smtplib.SMTP('smtp-relay.sendinblue.com', 587)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(from_user, from_pwd)
    mail_server.sendmail(from_user, to_list, msg.as_string())
    mail_server.quit()

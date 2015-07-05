import re
import time
import smtplib
from random import randint
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from django.utils import timezone
from panel.models import Configuration, Logging

word_template = '''
<html>
<head>
<LINK REL="stylesheet" HREF="[[word_bug]]">
</head>
<body>

[[word_design]]

</body>
</html>
'''

def log_submit(log_type=False, log_ip=False, log_user=False, log_entry=False):
    logging = Logging()
    logging.log_date = timezone.now()
    logging.log_type = log_type
    logging.log_ip = log_ip
    logging.log_user = log_user
    logging.log_line = log_entry
    logging.save()

def random_number(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(randint(range_start, range_end))
    
def create_email(recipient_list, template_details):
    try:
        # SMTP Server Details
        smtp_details = template_details.smtpServer
        # Get Sender Address
        sender_string = '{0} <{1}>'.format(template_details.display_name, template_details.email_address)

        # Get Subject Line
        subject_line = template_details.subject_line
        
        # Get the Email Design
        email_template = template_details.email_design
        
        # get the portal URI
        portal_uri = template_details.portal_uri
        
        if template_details.document_enable:
            word_doc = True
            document_name = template_details.document_name
            document_design = template_details.document_design
        else:
            word_doc = False
        
        
        message_list = []
        
        for recipient in recipient_list:
            # format the unique Links
            '''
            First 8 Chars are the Recipient UID
            Char 9 = type - 0 = webbug, 1 = portal, 2 = document
            Char 10 = plugin detect 0 = disabled 1 = enabled
            Char 11 = Template ID
            '''
            webbug_link = '{0}{1}{2}{3}'.format(recipient.uid, '0', template_details.portal_plugins, template_details.id)
            portal_link = '{0}{1}{2}{3}'.format(recipient.uid, '1', template_details.portal_plugins, template_details.id)
            wordbug_link = '{0}{1}{2}{3}'.format(recipient.uid, '2', template_details.portal_plugins, template_details.id)
            
            # get a fresh template
            email_content = email_template
            
            # Add Name
            email_content = email_content.replace('[[name]]', recipient.real_name)
            subject_line = subject_line.replace('[[name]]', recipient.real_name)
            
            # Add Email
            email_content = email_content.replace('[[email]]', recipient.email_address)
            
            # Add Random Numbers

            # Random Number Generator
            length_fields = re.findall(r'\[\[number(.+?)\]\]', email_content)
            for length in length_fields:
                random_int = random_number(int(length))
                email_content = email_content.replace('[[number{0}]]'.format(length), random_int)
                subject_line = subject_line.replace('[[number{0}]]'.format(length), random_int)

            # Add Click Tracker
            click_link = '{0}/{1}/{2}'.format(portal_uri,'p', portal_link)
            email_content = email_content.replace('[[click]]', click_link)
            
            # Add the web bugs
            if '[[webbug]]' in email_content:
                web_bug = '<img src="http://{0}/{1}/{2}" width=1 height=1 border=0>'.format(portal_uri, 'p', webbug_link)
                email_content = email_content.replace('[[webbug]]', web_bug)
        
            msg = MIMEMultipart()
            msg['From'] = sender_string
            msg['To'] = recipient.email_address
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject_line
            
            html = email_content
            part1 = MIMEText(html, 'html')
            
            msg.attach(part1)
            
            if word_doc:
            
                # insert the document bug
                word_bug = 'http://{0}/{1}/{2}'.format(portal_uri, 'p', wordbug_link)
                doc_file = word_template.replace('[[word_bug]]', word_bug)
                
                # Insert the design
                doc_file = doc_file.replace('[[word_design]]', document_design)

                # Add to the email
                part_doc = MIMEBase('application', "octet-stream")
                part_doc.set_payload( doc_file )
                Encoders.encode_base64(part_doc)
                part_doc.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(document_name))
                msg.attach(part_doc)
            
            # This will return the first generated email as a text string. This will bypass the sending
            #return msg.as_string()
            
            # append each recipient and message to list
            message_list.append([recipient.email_address, msg.as_string()])
            recipient.sent_date = timezone.now()
            recipient.save()
    except Exception as e:
        log_submit(log_type='email', log_ip=False, log_user=False, log_entry='Error Creating Email - {0}'.format(e))
    
    # pass message_list to send function
    send_email(template_details.email_address, message_list, smtp_details)

    
def send_one(s_dict):
    # Create Message
    message_list = []
    msg = MIMEMultipart()
    msg['From'] = s_dict['email_address']
    msg['To'] = s_dict['recipient_email']
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = s_dict['subject_line']
    
    html = s_dict['email_design']
    part1 = MIMEText(html, 'html')
    
    msg.attach(part1)
    

    if s_dict['document_enable']:
        # insert the document bug
        doc_file = word_template.replace('<LINK REL="stylesheet" HREF="[[word_bug]]">', '')
        
        # Insert the design
        doc_file = doc_file.replace('[[word_design]]', s_dict['document_design'])
        # Add to the email
        part_doc = MIMEBase('application', "octet-stream")
        part_doc.set_payload( doc_file )
        Encoders.encode_base64(part_doc)
        part_doc.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(s_dict['document_name']))
        msg.attach(part_doc)
    
    
    # This will return the first generated email as a text string. This will bypass the sending
    #return msg.as_string()
    
    message_list.append([s_dict['recipient_email'], msg.as_string()])
    send_email(s_dict['email_address'], message_list, s_dict['smtp_details'])
    return "Email Sent to {0}".format(s_dict['recipient_email'])
    
def send_email(sender, message_list, smtp_details):
    
    # Gmail smtp will rewrite your smtp headers.
    try:
        smtp_server = smtp_details.smtp_server
        smtp_port = smtp_details.smtp_port
        smtp_user = smtp_details.smtp_user
        smtp_pass = smtp_details.smtp_pass
        smtp_tls = smtp_details.smtp_tls
        smtp_ssl = smtp_details.smtp_ssl
        
        # start the connection
        if smtp_ssl:
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.ehlo()
        if smtp_tls:
            smtp.starttls()
        if smtp_user and smtp_pass:
            smtp.login(smtp_user, smtp_pass)
    except Exception as e:
        log_submit(log_type='smtp', log_ip=False, log_user=False, log_entry='Error Connection to SMTP - {0}'.format(e))
        return
        
    for message in message_list:
        try:
            smtp.sendmail(sender, [message[0]], message[1] )
            log_submit(log_type='email', log_ip=False, log_user=False, log_entry='Email Sent to - {0}'.format(message[0]))
            print "mail sent to: {0}".format(message[0])
        except Exception as e:
            log_submit(log_type=False, log_ip=False, log_user=False, log_entry='Error Sending Email - {0}'.format(e))
        
        time.sleep(4)
    smtp.close()
        
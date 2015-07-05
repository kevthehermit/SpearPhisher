import django
from django.db import models
from django.utils import timezone

# Create your models here.

class Configuration(models.Model):
    portal_domain = models.CharField(max_length=200)
    portal_port = models.CharField(max_length=200)
    #admin_email = models.CharField(max_length=200)
    
class Logging(models.Model):
    log_date = models.DateTimeField('log date', default=django.utils.timezone.now)
    log_type = models.CharField(max_length=20)
    log_ip = models.CharField(max_length=15, null=True, blank=True)
    log_user = models.CharField(max_length=50, null=True, blank=True)
    log_line = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return '{0} - {1}'.format(self.log_type, self.log_line)

class SMTPServer(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    smtp_server = models.CharField(max_length=50)
    smtp_port = models.IntegerField()
    smtp_user = models.CharField(max_length=50, null=True, blank=True)
    smtp_pass = models.CharField(max_length=50, null=True, blank=True)
    smtp_tls = models.BooleanField(default=False)
    smtp_ssl = models.BooleanField(default=False)

    def __str__(self):
        return self.name
        
    def single_server(self, id):
        return SMTPServer.objects.get(pk=int(id))

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created = models.DateTimeField('date created', default=django.utils.timezone.now)
    state = models.CharField(max_length=20, default='Pending')
    start_date = models.DateTimeField('Start Date', null=True, blank=True)
    end_date = models.DateTimeField('End Date', null=True, blank=True)
    template_id = models.IntegerField('Template ID', null=True, blank=True)
    
    def __str__(self):
        return self.name
        
    def single_campaign(self, id):
        return Campaign.objects.get(pk=int(id))
    
class Recipient(models.Model):
    # Recipient Data
    campaign = models.ForeignKey(Campaign)
    email_address = models.CharField(max_length=200)
    real_name = models.CharField(max_length=200)
    uid = models.CharField(max_length=15)
    ip_address = models.CharField(max_length=15, null=True, blank=True)
    counter = models.IntegerField(default=0)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    # Portal Data
    email_open = models.DateTimeField(null=True, blank=True)
    portal_open = models.DateTimeField(null=True, blank=True)
    document_open = models.DateTimeField(null=True, blank=True)
    email_client = models.CharField(max_length=30, null=True, blank=True)
    document_client = models.CharField(max_length=30, null=True, blank=True)
    web_client = models.CharField(max_length=30, null=True, blank=True)
    os_system = models.CharField(max_length=30, null=True, blank=True)
    
    # Plugin Data
    reader_version = models.CharField(max_length=15, null=True, blank=True)
    flash_version = models.CharField(max_length=15, null=True, blank=True)
    java_version = models.CharField(max_length=15, null=True, blank=True)
    silverlight_version = models.CharField(max_length=15, null=True, blank=True)
    shockwave_version = models.CharField(max_length=15, null=True, blank=True)

    # Post Data
    post_data = models.CharField(max_length=200, null=True, blank=True)
    
    
    def __str__(self):
        return self.email_address
        
    def single_recipient(self, id):
        return Recipient.objects.get(pk=int(id))
        
    def delete_recipient(self, uid):
        try:
            Recipient.objects.filter(uid=uid).delete()
            return True
        except Exception as e:
            return False
        
class Template(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    
    display_name = models.CharField(max_length=200)
    email_address = models.CharField(max_length=200)
    subject_line = models.CharField(max_length=100)
    email_design = models.CharField(max_length=8000, null=True, blank=True)
    smtpServer = models.ForeignKey(SMTPServer)
    
    portal_uri = models.CharField(max_length=100)
    portal_plugins = models.IntegerField()
    portal_design = models.CharField(max_length=8000, null=True, blank=True)
    portal_redirect = models.CharField(max_length=200, null=True, blank=True, default='None')
    
    document_enable = models.IntegerField()
    document_name = models.CharField(max_length=100, null=True, blank=True)
    document_design = models.CharField(max_length=8000, null=True, blank=True)
       
    def __str__(self):
        return self.title
        
    def single_template(self, id):
        return Template.objects.get(pk=int(id)) 
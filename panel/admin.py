from django.contrib import admin
from panel.models import Recipient, Campaign, Template, SMTPServer, Configuration, Logging

# Register your models here.

# Admin Recipients
class RecipientAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Recipient Data', {'fields': ['campaign', 'email_address', 'real_name', 'uid', 'ip_address', 'sent_date', 'counter', 'os_system']}),
        ('Portal Data', {'fields': ['email_open', 'portal_open', 'document_open', 'email_client', 'document_client', 'web_client'], 'classes': ['collapse']}),
        ('Plugin_Data', {'fields': ['reader_version', 'flash_version', 'java_version', 'silverlight_version', 'shockwave_version'], 'classes': ['collapse']}),
    ]

    
admin.site.register(Recipient, RecipientAdmin)


    
admin.site.register(Campaign)
admin.site.register(Template)
admin.site.register(SMTPServer)
admin.site.register(Configuration)
admin.site.register(Logging)
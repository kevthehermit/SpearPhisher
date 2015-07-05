import json
from collections import defaultdict

def calc_stats(recipient_list):
    # Prep the dicts
    counters = defaultdict(int)
    
    os_sys = defaultdict(int)
    browsers = defaultdict(int)
    email_client_dict = defaultdict(int)
    doc_client_dict = defaultdict(int)
    
    pdf_dict = defaultdict(int)
    flash_dict = defaultdict(int)
    shock_dict = defaultdict(int)
    silver_dict = defaultdict(int)
    java_dict = defaultdict(int)
    
    counters['total'] = len(recipient_list)
    for recipient in recipient_list:
        # Web Bug
        if recipient.email_open:
            counters['webbug'] += 1
            email_client_dict[recipient.email_client] += 1
        # Click Through
        if recipient.portal_open:
            # Increment the counter
            counters['click'] += 1
            # OS
            os_sys[recipient.os_system] += 1
            # Browser
            browsers[recipient.web_client] += 1            
            # Adobe Reader
            pdf_dict[recipient.reader_version] += 1           
            # Flash
            flash_dict[recipient.flash_version] += 1
            # Shockwave
            shock_dict[recipient.shockwave_version] += 1
            # SilverLight
            silver_dict[recipient.silverlight_version] += 1
            # Java
            java_dict[recipient.java_version] += 1

        if recipient.document_open:
            counters['document'] += 1
            doc_client_dict[recipient.document_client] += 1
            
    return {'os_sys':os_sys, 
            'browsers':browsers,
            'email_client_dict': email_client_dict,
            'doc_client_dict': doc_client_dict,
            'pdf_dict':pdf_dict, 
            'flash_dict':flash_dict, 
            'shock_dict':shock_dict, 
            'silver_dict':silver_dict, 
            'java_dict':java_dict,                                
            'counters':counters
            }
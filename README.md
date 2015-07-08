# SpearPhisher
A Web Application to Send and Track Spear Phishing Campaigns.

You can view screenshots and a quick demo video at http://spearphisher.co.uk

SpearPhisher is made up of 3 components. 
* Django Web Application for Creation and Management.
* SMTP Server for sending Emails.
* Bottle Web Application for Tracking Responses.

SpearPhisher makes use of the following 3rd-Party components:

* jQuery - https://code.jquery.com/
* BootStrap - http://getbootstrap.com/
* BootStrap Tables - http://bootstrap-table.wenzhixin.net.cn/
* SummerNote - http://summernote.org/
* FontAwsome - https://fortawesome.github.io/Font-Awesome/
* HighCharts - http://www.highcharts.com/

ToDo:

* Report Summary
* Edit Campaign
* Pre Defined Templates.
* Safely handle JavaScript in Templates to block them in template view mode. 
* Complete the Form Handler.
* Account Management / Password Reset

For best performance the Web server should **NOT** be run on the default single threaded SQlite DB and web server. In this installation example I will use Apache with MOD WSGI and MySQL.  


# Installation

This installation has been tested with a clean install of Ubuntu Server 14.04 using Python 2.7.

During installation the following optional elements were selected for installation 

* OpenSSH server
* LAMP Server
* Mail server - Postfix set to Internet Site

These can also be installed with:
```sudo apt-get install apache2 mysql-server php5 postfix```

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install python-dev python-pip git libmysqlclient-dev libapache2-mod-wsgi
$ sudo pip install --upgrade bottle django mysql-python ua-parser
```


#### Optional

The following additions are optional but can be used to enhance the functionality or asthetics of the application

* Admin Bootstrap - sudo pip install admin-bootstraped
* SSLServer - sudo pip install django-sslserver
* Fake Factory - sudo pip install 
* 


## Configuration

#### File Paths

```
$ cd path/to/spearphisher
$ git clone https://github.com/kevthehermit/SpearPhisher
$ cd SpearPhisher
$ sudo cp -r install/var/www/html/* /var/www/html/
$ sudo cp install/vhost/portal.conf /etc/apache2/sites-available/
$ sudo chown -R www-data:www-data /var/www/html/
$ chmod -R 775 /var/www/html/
```

#### Apache

Disable the default site and enable our portal

```
$ sudo a2dissite 000-default.conf
$ sudo a2ensite portal.conf
$ sudo service apache2 restart
$sudo a2enmod wsgi
```


#### MySql

It is advised to secure your new MySQL install with

```$ sudo mysql_secure_installation```

Create a user and a database

```
$ mysql -u root -p 
enter password: <The one you set at install>
mysql> create database spearphisher;
mysql> create user 'spearphisher'@'localhost' identified by 'spearphisher';
mysql> grant all on spearphisher.* to 'spearphisher'@'localhost';
mysql> FLUSH PRIVILEGES;
mysql> quit
```

Edit spearphisher/settings.py

- Set the DATABASES Settings to match your setup
- Set Your TIME_ZONE
- Set DEBUG = False
- Set TEMPLATE_DEBUG = False
- Set ALLOWED_HOSTS = ['*'] # https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts

```
$ python manage.py makemigrations
$ python manage.py migrate
```
#### Super User

```$ python manage.py createsuperuser```

Follow the on screen instructions. The username must be in the form of an email address.

## First Run

With all the steps in place you should be able to run the Django web server and access the control panel. 

```$ python manage.py runserver 0.0.0.0:8080```

then point a browser at your IP on port 8080

#### SMTP Configuration

After logging in access the admin panel from the Nav Bar.
Under SMTP Servers add a new smtp server. 

If your using the local smtp server you can leave the username, password and tls values blank. For those in the UK. Most ISP's will block port 25 so running a local smtp server will likley fail to send any mails. 

If your using Gmail or some other SMTP relay instaed of a local one fill in all the required values.

You can test the functionality of the SMTP by using the Create --> Single Email from the Nav Bar

##Usage

#### Create your first template

You can Create, Create from Exisitng and modify templates from the Templates page on the Nav Bar. 

The First template you are presented with is a blank template that can be saved as a new template. All other templates can be updated or saved as new. 

The template is split in to 4 sections. 

* Details
* Email Template
* Document Template
* Portal Template

Complete all the required sections. Most should be self explanatory. 

***Each of the design elements will allow you to enter raw HTML and JavaScript. It is important to note that these will be rendered in your template view as well. ***


###### Email 
Display Name and Email address are your Spoofed Sender. If using Gmail or some other webservices your headers may not be spoofed properly. 

The following modifiers can be used in the subject line and email body.

- [[name]] This Enters the Full Name of the recipient. 
- [[email]] This enters the recipeints email address
- [[click]] This enters the recipients unique link to the portal. 
- [[numberx]] This enters a random number where x is the lenght of the number. 
e.g. [[number5]] Would enter a number like 52381

###### Document

If enabled the Document name must include a valid MSWord Extension i.e. doc, docx.
The document can be created jsut like any other web page. 

###### Portal

The portal URI is the domain / ip that the portal is hosted on. e.g. spearphisher.co.uk 

The Redirect to is used to redirect to any other domain. 
If plugin detection has been enabled there is a 3 second delay in order to complete the plugin detection. If you are redirecting from plugin detection it may be worth adding a 'Please Wait or eqivilent line as the portal page will be visible.'


**ToDo**
In the portal design elements you can create an HTML form to cpature Post Data. Just set the form action to ```action="/f"```.

You must also include the following form field in order to correctly track. 
```<input type='hidden' name='uid' value='[[uid]]' />```

All key value pairs from your form will be recorded in the DataBase. 


#### Create Your First Campaign

From the nav bar select Create --> Campaign. Enter all the details and select the template you created in the previous section.

Once you have created your campaign you need to add recipients. Open your campaing and select the tracking tab. On the tab bar you shoudl see an option to 'Add Reciepients'. 

You can add individualy via the web interface or upload a csv of Name,Email

Once you have added all your recipients you are ready to go. 


#### Running the Campaing. 

When you click the start button all the emails will start to send. From this point you are no longer able to add new recipients. All responses will be tracked and stored in the database until you click the stop button. 

Once the campaign has been stopped the portal will redirect all users to google without tracking their activites in to the DataBase. 




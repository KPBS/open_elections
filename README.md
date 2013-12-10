open_elections
==============

An application deployed via Python/Django to grab and parse California election results available to news organizations and others.


Details
===============

This application was developed at KBPS Public Broadcasting in San Diego, California, by James Tinksy for feeding election results to [kpbs.org](http://www.kpbs/org) (see also: [kpbs.org election coverage](http://www.kpbs.org/news/election/)). It was originally developed as a Django module and all notes below are germane to setting it up inside a Django environment. Some familiarity with Python-Django will be helpful for setting this up and running it. For more information on Django, [see the official Django documentation](https://docs.djangoproject.com/en/dev/).

Even though this application is available for use by anyone, in order to retrieve election results, you will need to get credentials set-up with one or all of the following orgnizations: 

	*California Secretary of State

	*Associated Press

	*Your local county's registrar of voters

See each organization for more information on accessing election results through them. *Neither this application nor the authors nor maintainers of this application can help you secure credentials to retrieve election results.*


Structure
===============

This application has three main constructs:

     content_fetcher.py (see below)
     content_parser.py (see below)
     Associated Django app architecture (templates, views, urls, etc.)


*content_fetcher.py*: This module is used to fetch content via https from the CA Secretary of State, or via ftp from the Associated Press or the county registrar. 


*content_parser.py*: This module takes retrieved xml content from the above listed sources and parses that content and inserts it into your Django database.


How to Use
===============



1. File Fetching

If you want to use this inside of a Django application, below are the things you will need to do:

   1. Add the Following to INSTALLED_APPS in your settings.py file:
      * 'open_elections'

   2. Run syncdb (or migrate the application if you use South).

   3. Add credentials for your FTP Election Information Repositories:

```python
### From a django shell, you can insert your local county credentials
    $ python ./manage.py shell
    >>> from open_elections.models import FtpCredential
    >>> county_cred = FtpCredential(indentifier="county",
				user="ftp username"
				passphrase="ftp pass")
    >>> county_cred.save()
```

Similarly, your AP credentials can be entered as well:

```python
    >>> from open_elections.models import FtpCredential
    >>> ap_cred = FtpCredential(indentifier="ap",
				user="ftp username"
				passphrase="ftp pass")
    >>> ap_cred.save()
```     

After that, you will need to edit content_fetcher.py to tell it where you'd like to save retrieved files and, if you are using your county's ftp server, to reflect the county server you want to use and the file-path you'd like to retrieve on your county server. 

Find the following section in content_fetcher.py and change it to suit your needs:

```python
class ContentFetcher(object):

    def __init__(self):

        ## Local directory where retrieved files are to be saved ##
        # Change the directory you want to save retrieved files and
	## MAKE SURE THAT DIRECTORY EXISTS!:
        self.FILE_ROOT = '/home/your-username/application/elections_data/xml/'

        ## Change the county server to reflect the server you are accessing 
        self.county_server = '170.213.236.93'

	## Change the county file to include full-path to the file you'd like to retrieve
        self.county_file = 'election.xml'
	
```

After that, you can try to retrieve content in the following way:

```python
    >>> from open_elections.content_fetcher import ContentFetcher
    >>> cf = ContentFetcher()
    >>> cf.fetch_xml_content(server="county")
    '/home/your-username/application/elections_data/xml/county_data.xml'
	
```

You can also retrieve custom data from another server, but you will have to save that server using the FtpCredential model and then you will have to specify the `retr_file_path` when you are retrieving content from that server:

```python
    >>> from open_elections.models import FtpCredential
    >>> custom_cred = FtpCredential(indentifier="customftpserver.com",
				user="ftp username"
				passphrase="ftp pass")
    >>> custom_cred.save()
    >>> from open_elections.content_fetcher import ContentFetcher
    >>> cf = ContentFetcher()
    >>> cf.fetch_xml_content(server="customftpserver.com", retr_file_path="/path/on/server/to/file.xml")
```


2. File Parsing

The file-parsing module is where the majority of work has been done. It takes the AP or state or county xml files and parses them for content. Assuming you have a known path for your saved file, you can call file parsers in the following way:

```python
	$ python ./manage.py shell
	>>> ap_file = "path/to/ap/file.xml"
	>>> from content_parser import parse_ap_xml
	>>> parse_ap_xml(ap_file)
```
It will then add the AP data to your database.

In addition, the Secretary of State has a number of files they offer and we are working on parsing all of them in one go, but have not completed this yet. In the meantime, to call the parse_state_xml function, you will need to pass in your filename in a list, like so:

```python
	$ python ./manage.py shell
	>>> state_file = "path/to/ap/file.xml"
	>>> from content_parser import parse_state_xml
	>>> parse_state_xml([state_file])
	## Note: the file-name has been enclosed in a list.
```

*Note:* For county parsing, there are some values hard-coded into the content_parser file that you are advised to look at and which will be addressed in future versions of this application. These are mostly related to the changing xml from our local county, so you should take caution when running this function and set those values accordingly.

*Another Note:* Sample data has been provided so you can compare your xml files to the xml files this application was built to interpret.


3. Using the custom manager commands 
(An alternative to content_fetcher and content_parser)

Finally, you may also use the enclosed management commands to retrieve and parse files once the credentials have been added to the database and the content_fetcher.py file has been edited to include the relevant information:

```python
	$ python ./manage.py parse_xml_content ap
```


4. Django Views/Templates/Urls, etc
-----------------------------------
The rest of this application is provided for convenience in order to help you get started building templates and views for the content you would like to host on your Django site. 


Other Notes
===============


You may also find it useful to install and use the python-elections application, which is designed for getting data from the AP elections feed. [Python-elections github repo](https://github.com/datadesk/python-elections). Lastly, the [application django-endless-pagination](https://github.com/frankban/django-endless-pagination), may also be useful for setting up your views/templates in order to feed the content. 

Application deployed via Django to grab and parse election results available to news organizations.

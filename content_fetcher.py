import os
import urllib2
import zipfile

from ftplib import FTP
from .models import FtpCredential

class ContentFetcher(object):

    def __init__(self):

        ## Local directory where retrieved files are to be saved ##
        # Change as needed:
        self.FILE_ROOT = '/home/your-username/application/elections_data/xml/'

        #~ AP Elections ~#
        self.ap_server = 'electionsonline.ap.org'
        self.ap_file = '/Pres_Reports/xml/pres_summary_all.xml'

        #~ CA Secretary of State ~#
        self.sos_url = 'http://media.sos.ca.gov/media/'        
        self.sos_files =  ('X12PG',)
        # self.sos_files = ('X12DP', 'X12PP', 'X12PG')

        #~ San Diego County ~#
        self.county_server = '170.213.236.93'
        self.county_file = 'election.xml'

    def fetch_xml_content(self, server = 'ap', **kwargs):
        """Gets the XML file from the FTP server"""

        credential = FtpCredential.objects.get(identifier=server)
        
        if server is 'ap':
            ftp = FTP(self.ap_server)
            retr_file_path = self.ap_file
            file_name = os.path.basename(retr_file_path)
            local_store_path = os.path.join(self.FILE_ROOT, file_name)
            
        elif server is 'county':
            ftp = FTP(self.county_server)
            retr_file_path = self.county_file
            file_name = 'county_data.xml'
            local_store_path = os.path.join(self.FILE_ROOT, file_name)

        else:
            ## GENERIC CASE: server cred must be stored in dbase
            ## Also: retr_file_path must be specified in method call
            ftp = FTP(server)
            try:
                retr_file_path = kwargs['retr_file_path']
                file_name = os.path.basename(retr_file_path)
                local_store_path = os.path.join(self.FILE_ROOT,
                                                file_name)
            except KeyError:
                emsg = "You must specify a file path to retrieve:"
                emsg += " Pass the retr_file_path kwarg into the function"
                raise KeyError(emsg)    
                
        retrieval = 'RETR ' + retr_file_path
        ftp.login(credential.username, credential.password)
        # TODO: Add error handling to this
        ftp.retrbinary(retrieval,
                       open(local_store_path, 'wb').write)
        ftp.quit()
        
        return local_store_path
   
    def fetch_sos(self):
        # These files can only be accessed from an IP address that's been
        # registered with the California Secretary of State
        fetched_files = []

        for url in self.sos_files:
            # print "Opening and parsing %s" % url
            remote_file_path = self.sos_url + url + '.zip'
            local_file_path = os.path.join(self.FILE_ROOT, (url + '.zip'))
            
            response = urllib2.urlopen(remote_file_path)
            zip_file = open(local_file_path, 'wb')
            zip_file.write(response.read())
            zip_file.close()            

            zip_file = open(local_file_path)
            unzip_file = zipfile.ZipFile(zip_file, "r")

            file_name = os.path.join(self.FILE_ROOT, (url + '_510.xml'))
            xml_file = open(os.path.join(FILE_ROOT, file_name), 'w')
            xml_file.write(unzip_file.read(file_name))
            xml_file.close()
            zip_file.close()

            fetched_files.append(file_name)
            
        return fetched_files

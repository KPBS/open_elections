from django.test import TransactionTestCase


### WORK IN PROGRESS ##

class ParserTest(TransactionTestCase):

    def setUp(self):
        import os
        sample_data_dir = os.path.abspath('sample_data')
        sample_files = ['sample_ap.xml', 
                        'sample_county_data.xml', 
                        'sample_state.xml', 
                        'sample_state_pres_results.xml']
        self.sample_files = { filename : 
                              os.path.join(sample_data_dir, filename) 
                              for filename in sample_files}
        
    def test_state_parsing(self):
        from open_elections.content_parser import parse_state_xml
        from open_elections.models import StateContest
        from open_elections.models import StateCandidate 

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ## GOAL:    Argument must be a list, tuple open-able files.
        ## It will raise an assertion error if not, so this code should run fine.
        ## ---- ##
        state_sample = [self.sample_files['sample_state.xml']]
        parse_state_xml(state_sample) 

        ## Goal: Query the database for values we know are in the file.
        ## ---- ##
        ## Let's try a candidate first:
        obama = StateCandidate.objects.get(candidate_name="Barack Obama")
        self.assertEquals(obama.affiliation, 'DEM')
        self.assertEquals(obama.valid_votes, 7854285)
        
        ## How's about a contest next:
        pres = StateContest.objects.get(contest_name='President')
        self.assertEquals(pres.total_precincts, 24491)
        self.assertEquals(pres.total_precincts, 24491)
        self.assertEquals(pres.contest_identifier, '010000000000')
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


    def test_ap_parsing(self):
        from open_elections.content_parser import parse_ap_xml
        from open_elections.models import ApContest
        from open_elections.models import ApCandidate 
        from decimal import Decimal

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ## GOAL: Parse the AP file
        ## Then query the database for values we know are in the file.

        ap_sample = self.sample_files['sample_ap.xml']
        parse_ap_xml(ap_sample) 

        ## Let's try a candidate first:
        obama = ApCandidate.objects.get(name="Obama")
        self.assertEquals(obama.electoral_votes, 277)
        self.assertEquals(obama.party, 'Dem')
        
        ## How's about a contest next:
        pres = ApContest.objects.get(office='President')
        self.assertEquals(pres.precincts_pct, Decimal('100.00'))
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def test_county_parsing(self):
        from open_elections.content_parser import parse_county_xml
        from open_elections.models import CountyElection
        from open_elections.models import CountyContest
        from open_elections.models import CountyCandidate   

        parse_county_xml(self.sample_files['sample_county_data.xml'])
        # We'll just shortcut checking for values and see if these
        # records exist. I am betting they do.
        assert CountyElection.objects.filter(title="CITY OF SAN DIEGO").exists()
        assert CountyContest.objects.filter(contest_id=1).exists()
        assert CountyCandidate.objects.filter(name="NATHAN FLETCHER").exists()
        
# class ViewsTest(TestCase):
#     pass


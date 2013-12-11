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
        self.sample_files = {filename : os.path.join(sample_data_dir, filename) for filename in sample_files}
        
    def test_state_parsing(self):
        from open_elections.content_parser import parse_state_xml
        from open_elections.models import StateContest
        from open_elections.models import StateCandidate 

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ## GOAL:    Argument must be a list, tuple open-able files.
        ## ---- ##
        with self.assertRaises(AssertionError):
            parse_state_xml(self.sample_files['sample_state.xml'])
        # -------------------------------------------#
        
        ## Goal:   parse_state_xml runs fine when passed a list...
        ## ---- ##
        state_sample = [self.sample_files['sample_state.xml']]
        parse_state_xml(state_sample) 

        ## Goal: Query the database for values we know are in the file.
        ## ---- ##
        ## Let's try a candidate first:
        obama = StateCandidate.objects.get(candidate_name="Barack Obama")
        self.assertEquals(obama.affiliation, 'DEM')
        self.assertEquals(valid_votes, 7854285)
        
        ## How's about a contest next:
        pres = StateContest.objects.get(contest_name=='President')
        self.assertEquals(pres.total_precincts, 24491)
        self.assertEquals(pres.total_precincts, 24491)
        # -------------------------------------------#
        self.assertEquals(pres.contest_identifier, '010000000000')
    
    


# class ViewsTest(TestCase):
#     pass


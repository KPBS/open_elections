import os
from datetime import datetime
from StringIO import StringIO as sio
from xml.etree import ElementTree as ET

from django.db.models import Q
from django.utils.encoding import smart_str

from .models import StateContest, StateCandidate
from .models import CountyElection, CountyContest, CountyCandidate
from .models import ApContest, ApCandidate
from .models import Contribution, Candidate


## Models accessed below
# StateContest
# StateCandidate
# CountyElection
# CountyContest
# CountyCandidate
# ApContest
# ApCandidate
# Candidate
# CountyZipCode
# Contribution


def parse_state_xml(state_xml_files):
    # TODO: Make this work for both primary and general elections.
    # Primaries have two files, presidential and district:
    # urls = ('X12DP', 'X12PP')
    """Parse the state XML and insert it into the database"""

    errmsg = "Not all file paths are available. Did you pass in a list?"
    assert all(os.path.exists(path) for path in state_xml_files), errmsg

    affiliations = {'Democratic': 'DEM',
                    'Republican': 'REP',
                    'American Independent': 'AIP',
                    'Green': 'GRN',
                    'Libertarian': 'LIB',
                    'Peace and Freedom': 'P-F',
                    'Independent': 'IND',
                    'Non-Partisan': '',
                    'No Party Preference': ''}
    
    for xml_file in state_xml_files:

        ## ----- -------- ---- #
        ## I was having encoding problems, so I introduced chunk below.
        ## Mileage may vary and this may not be necessary in all cases ##
        with open(xml_file) as f:
            raw_text = f.read()
        xml_file = sio(raw_text.decode('cp1252').encode('utf8'))

        tree = ET.parse(xml_file)
        root = tree.getroot()
        if root is not None:
            contests = root.find('Count').find('Election').find('Contests').getiterator('Contest')
            for contest in contests:
                contest_params = {}
                candidate_params = {}
                # Get the CountMetric data
                cm_list = contest.find('TotalVotes').findall('CountMetric')
                count_metrics = {}
                for cm in cm_list:
                    count_metrics[cm.attrib['Id']] = cm.text
                #See if the contest already exists
                try:
                    c = StateContest.objects.get(
                        contest_identifier=contest.find('ContestIdentifier').attrib['Id'])
                    # print "Updating existing contest %s" % contest.find('ContestIdentifier').attrib['Id']
                    c.name = contest.find('ContestIdentifier').find(
                        'ContestName').text
                    c.precincts_reporting = count_metrics.get('PR', 0)
                    c.total_precincts = count_metrics.get('TP', 0)
                    c.pct_yes_votes = count_metrics.get('PYV', 0)
                    c.pct_no_votes = count_metrics.get('PNV', 0)
                    c.save()
                except StateContest.DoesNotExist:
                    # print "Creating new contest %s" % contest.find('ContestIdentifier').attrib['Id']
                    contest_params['contest_identifier'] = contest.find(
                        'ContestIdentifier').attrib['Id']
                    contest_params['contest_name'] = contest.find(
                        'ContestIdentifier').find('ContestName').text
                    contest_params['precincts_reporting'] = count_metrics.get('PR', 0)
                    contest_params['total_precincts'] = count_metrics.get('TP', 0)
                    contest_params['pct_yes_votes'] = count_metrics.get('PYV', 0)
                    contest_params['pct_no_votes'] = count_metrics.get('PNV', 0)
                    c = StateContest(**contest_params)
                    c.save()
                contest_id = c.id
                candidate_params['state_contest_id'] = contest_id
                for selection in contest.find('TotalVotes').findall('Selection'):
                    sel_count_metrics = {}
                    sel_cm_list = selection.findall('CountMetric')
                    for sel_cm in sel_cm_list:
                        sel_count_metrics[sel_cm.attrib['Id']] = sel_cm.text
                    try:
                        candidate_identifier = selection.find('Candidate').find('CandidateIdentifier').attrib['Id']
                    except:
                        candidate_identifier = 0
                    try:
                        proposal_identifier = selection.find('Candidate').find('ProposalItem').attrib['ProposalIdentifier']
                    except:
                        proposal_identifier = ''
                    try:
                        referendum_option_identifier = selection.find('Candidate').find('ProposalItem').attrib['ReferendumOptionIdentifier']
                    except:
                        referendum_option_identifier = ''
                    try:
                        sel = StateCandidate.objects.get((Q(candidate_identifier=candidate_identifier) & Q(state_contest__contest_identifier=contest.find('ContestIdentifier').attrib['Id'])) | (Q(proposal_identifier=proposal_identifier) & Q(referendum_option_identifier=referendum_option_identifier)))

                        if candidate_identifier != 0:
                            # print "Updating existing candidate %s" % candidate_identifier
                            #This is a candidate
                            sel.candidate_name = selection.find('Candidate').find('CandidateIdentifier').find('CandidateName').text
                            sel.candidate_identifier = selection.find('Candidate').find('CandidateIdentifier').attrib['Id']
                            affiliation = selection.find('Candidate').find('Affiliation').find('Type').text
                            sel.affiliation = affiliations[affiliation]
                            sel.valid_votes = selection.find('ValidVotes').text
                            sel.pct_votes_party = sel_count_metrics.get('PVP', 0)
                            sel.pct_votes_race = sel_count_metrics.get('PVR', 0)
                        elif proposal_identifier != 0:
                            #This is a proposal or judge
                            if selection.find('Candidate').find('ProposalItem').attrib['ReferendumOptionIdentifier'] == 'Yes':
                                sel.referendum_option_identifier = 'Yes'
                                sel.valid_votes = selection.find('ValidVotes').text
                                sel.pct_votes_race = count_metrics.get('PYV', 0)
                            else:
                                sel.referendum_option_identifier = 'No'
                                sel.valid_votes = selection.find('ValidVotes').text
                                sel.pct_votes_race = count_metrics.get('PNV', 0)
                        sel.save()
                    except StateCandidate.DoesNotExist:
                        # print "Adding new candidate %s" % candidate_identifier
                        if candidate_identifier != 0:
                            candidate_params['candidate_name'] = selection.find('Candidate').find('CandidateIdentifier').find('CandidateName').text
                            candidate_params['candidate_identifier'] = selection.find('Candidate').find('CandidateIdentifier').attrib['Id']
                            affiliation = selection.find('Candidate').find('Affiliation').find('Type').text
                            candidate_params['affiliation'] = affiliations[affiliation]
                            candidate_params['valid_votes'] = selection.find('ValidVotes').text
                            candidate_params['pct_votes_party'] = sel_count_metrics.get('PVP', 0)
                            candidate_params['pct_votes_race'] = sel_count_metrics.get('PVR', 0)
                        else:
                            candidate_params['proposal_identifier'] = selection.find('Candidate').find('ProposalItem').attrib['ProposalIdentifier']
                            if selection.find('Candidate').find('ProposalItem').attrib['ReferendumOptionIdentifier'] == 'Yes':
                                candidate_params['referendum_option_identifier'] = 'Yes'
                                candidate_params['valid_votes'] = selection.find('ValidVotes').text
                            else:
                                candidate_params['referendum_option_identifier'] = 'No'
                                candidate_params['valid_votes'] = selection.find('ValidVotes').text
                        sel = StateCandidate(**candidate_params)
                        # sel.StateContest = c
                        sel.save()

def parse_county_xml(county_xml_file):
    """Parse the EML election results for the County of San Diego"""
    
    ## TO DO: Make this more generic so election information can be entered into it. ##
    tree = ET.parse(county_xml_file)
    root = tree.getroot()
    try:
        ## TITLE: receive title from caller
        election = CountyElection.objects.get(title3='Tuesday, November 19, 2013')
        election.time = root.attrib['time']
        if root.attrib['ToBeCnt'] == "":
            election.to_be_cnt = 0
        else:
            election.to_be_cnt = root.attrib['ToBeCnt']
        if root.attrib['Absentee'] == "":
            election.absentee = 0
        else:
            election.absentee = root.attrib['Absentee']

        election.to_be_cnt = root.attrib['ToBeCnt']
        election.absentee = root.attrib['Absentee']
        election.precincts_reported = root[0].attrib['reported']
        election.total_precincts = root[0].attrib['total']
        election.save()
        election_id = election.id
    except:
        election_args = {}
        # receive election date from caller or from xml file
        election_args['election_date'] = '2012-11-06'
        election_args['election_time'] = root.attrib['time']
        election_args['is_major'] = root.attrib['Major']
        election_args['is_minor'] = root.attrib['Minor']
        election_args['title'] = root.attrib['title']
        election_args['title2'] = root.attrib['title2']
        election_args['title3'] = root.attrib['title3']
        election_args['etype'] = root.attrib['etype']
        if root.attrib['ToBeCnt'] == "":
            election_args['to_be_cnt'] = 0
        else:
            election_args['to_be_cnt'] = root.attrib['ToBeCnt']
        if root.attrib['Absentee'] == "":
            election_args['absentee'] = 0
        else:
            election_args['absentee'] = root.attrib['Absentee']
        election_args['precincts_reported'] = root[0].attrib['reported']
        election_args['total_precincts'] = root[0].attrib['total']
        election = CountyElection(**election_args)
        # print "election_args = %s" % election_args
        election.save()
        election_id = election.id
    contest_params = {}
    contest_params['election_id'] = election_id
    candidate_params = {}
    if root is not None:
        for contest in root[0].findall('CONTEST'):
            #See if the contest already exists
            try:
                c = CountyContest.objects.get(contest_key=contest.attrib['key'])
                c.numberof = contest.attrib['numberof']
                if "." in contest.attrib['pctrpt']:
                    num = []
                    num = contest.attrib['pctrpt'].split(".")
                    c.pctrpt = int(num[0])
                else:
                    c.pctrpt = contest.attrib['pctrpt']
                c.votefor = contest.attrib['votefor']
                c.tcounted = contest.attrib['tcounted']
                c.tblank = contest.attrib['tblank']
                c.tover = contest.attrib['tover']
                c.tunder = contest.attrib['tunder']
                c.reporting = contest.attrib['reporting']
                c.numprec = contest.attrib['numprec']
                c.save()
            except CountyContest.DoesNotExist:
                for item in contest.items():
                    if item[0] == 'key':
                        contest_params['contest_key'] = item[1]
                        pass
                    elif item[0] == 'id':
                        contest_params['contest_id'] = item[1]
                        pass
                    elif item[0] == 'pctrpt':
                        if "." in item[1]:
                            num = []
                            num = item[1].split(".")
                            contest_params['pctrpt'] = int(num[0])
                        else:
                            contest_params['pctrpt'] = item[1]
                    else:
                        contest_params[item[0]] = item[1]
                # print "contest_params = %s" % contest_params
                c = CountyContest(**contest_params)
            c.save()
            contest_id = c.id
            candidate_params['contest_id'] = contest_id

            for candidate in contest.findall('CANDIDATE'):
                try:
                    cdt = CountyCandidate.objects.get(cankey=candidate.attrib['cankey'])
                    cdt.vote = candidate.attrib['votes']
                    cdt.pct = candidate.attrib['pct']
                except CountyCandidate.DoesNotExist:
                    for item in candidate.items():
                        if item[0] == 'votes':
                            candidate_params['vote'] = item[1]
                        elif item[0] == 'pct':
                            candidate_params['pct'] = item[1]
                        elif item[0] == 'party':
                            if item[0] == None:
                                candidate_params['party'] = item[1]
                                candidate_params['party'] = 'See Contest'
                            else:
                                pass
                        else:
                            candidate_params[item[0]] = item[1]
                        cdt = CountyCandidate(**candidate_params)
                cdt.save()


def parse_ap_xml(ap_xml_file):
    """Parses the XML pres_summary.xml file from the Associated Press
    Saves to the database."""
    
    tree = ET.parse(ap_xml_file)
    root = tree.getroot()
    if root is not None:
        now = datetime.now()
        contest, con_created = ApContest.objects.get_or_create(office = 'President',
                                                               defaults = {'precincts_pct': '0.00',
                                                                           'timestamp' : now})
        contest.precincts_pct = root.attrib['PrecinctsPct']        
        timestamp = root.attrib['timestamp']
        contest.timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        contest.save()

        for cand in root.findall('Cand'):
            if 'CandID' in cand.attrib:
                candidate, can_created = ApCandidate.objects.get_or_create(contest=contest,
                    candidate_id=cand.attrib['CandID'], party=cand.attrib['party'], name=cand.attrib['name'])

                candidate.popular_vote = cand.attrib['PopVote']
                candidate.popular_pct = cand.attrib['PopPct']
                candidate.states_won = cand.attrib['StatesWon']
                candidate.electoral_votes = cand.attrib['ElectWon']
                candidate.save()

def parse_cal_access_data(file, candidate_id):  # TODO: get the candidate type based on the data
    """Adds CSV data to the database depending on candidate type"""
    import csv
    def format_date(the_date):
        if the_date == '':
            # print the_date
            d = '2000-01-01'
        else:
            d = datetime.datetime.strptime(the_date, '%m/%d/%Y')
        return d

    # Open the file and start looping through it
    contribs = csv.reader(open(file, 'rU'), dialect=csv.excel)
    for row in contribs:
        if row[0] != 'Filer_ID':  # ignore header row
            contrib = Contribution(
                kpbs_candidate=Candidate.objects.get(id=candidate_id),
                filer_id=row[0],
                filer_naml=row[1],
                report_num=row[2],
                committee_type=row[3],
                rpt_date=format_date(row[4]),
                from_date=format_date(row[5]),
                thru_date=format_date(row[6]),
                elect_date=format_date(row[7]),
                rec_type=row[10],
                form_type=row[11],
                tran_id=row[12],
                entity_cd=row[13],
                tran_naml=row[14],
                tran_namf=row[15],
                tran_namt=row[16],
                tran_nams=row[17],
                tran_adr1=row[18],
                tran_adr2=row[19],
                tran_city=row[20],
                tran_state=row[21],
                tran_zip4=CountyZipCode.objects.get(zip_code=row[22]),
                tran_emp=row[23],
                tran_occ=row[24],
                tran_self=row[25],
                tran_type=row[26],
                tran_date=format_date(row[27]),
                tran_amt1=row[29],
                tran_amt2=row[30],
                tran_dscr=row[31],
                cmte_id=row[32])
            
            contrib.save()

def emit_combined_csv_results():
    """Returns a CSV file to be parsed for use by KPBS.org"""
    import csv
    
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    pres_candidates = ApCandidate.objects.select_related().order_by('-popular_vote').filter(show_on_web=True)
    county_candidates = CountyCandidate.objects.all().order_by('contest__contest_key', '-pct').filter(contest__show_on_web=True)
    state_candidates = StateCandidate.objects.select_related().order_by('state_contest', '-valid_votes').filter(state_contest__show_on_web=True)

    outfile = os.path.join(results_dir, 'results.csv')
    with open(outfile, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(['contest_identifier', 'contest_name', 'precincts_pct', 'candidate_name', 'party', 'total_votes', 'percent_votes', 'referendum_option_identifier', 'last_updated', 'electoral_votes'])

        for c in pres_candidates:
            writer.writerow([1, 'President of the United States', c.contest.precincts_pct,
                c.name, c.party, c.popular_vote, c.popular_pct, '', c.contest.timestamp.strftime("%-m/%-d/%y - %I:%M %p"), c.electoral_votes])

        props = {'190000000030': 'Prop 30', '190000000031': 'Prop 31', '190000000032': 'Prop 32', '190000000033': 'Prop 33', '190000000034': 'Prop 34', '190000000035': 'Prop 35', '190000000036': 'Prop 36', '190000000037': 'Prop 37', '190000000038': 'Prop 38', '190000000039': 'Prop 39', '190000000040': 'Prop 40'}
        for c in state_candidates:
            if c.candidate_name:
                candidate_name = c.candidate_name
                contest_name = c.state_contest.contest_name
            elif c.proposal_identifier:
                candidate_name = c.referendum_option_identifier
                contest_name = "%s - %s" % (props[c.state_contest.contest_identifier], c.state_contest.contest_name)
            precincts_pct = ((c.state_contest.precincts_reporting / c.state_contest.total_precincts) * 100)
            writer.writerow([c.state_contest.contest_identifier, contest_name,
                             precincts_pct,
                             smart_str(candidate_name), c.affiliation, c.valid_votes, c.pct_votes_race,
                             c.referendum_option_identifier, c.last_update.strftime("%-m/%-d/%y - %I:%M %p"), ''])

        for c in county_candidates:
            if c.name in ('YES', 'NO'):
                writer.writerow([c.contest.contest_id, c.contest.title, c.contest.pctrpt,
                    '', c.party, c.vote, c.pct, c.name, c.last_update.strftime("%-m/%-d/%y - %I:%M %p"), ''])
            else:
                writer.writerow([c.contest.contest_id, c.contest.title, c.contest.pctrpt,
                    c.name, c.party, c.vote, c.pct, '', c.last_update.strftime("%-m/%-d/%y - %I:%M %p"), ''])

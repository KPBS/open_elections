from django.db import models


class CountyElection(models.Model):
    """Describes the ELECTION element of the XML file
        <ELECTION date="05-30-10" time="08:08:20" Major="1" Minor="1"
           title="COUNTY OF SAN DIEGO" title2="GUBERNATORIAL PRIMARY ELECTION" title3="Tuesday, June 8, 2010"
           etype="UNOFFICIAL" ToBeCnt="" Absentee="">
        <SUMMARY reported="0" total="1671" >
    """
    election_date = models.DateField()
    election_time = models.TimeField(blank=True, null=True)
    is_major = models.BooleanField(default=True)
    is_minor = models.BooleanField(default=True)
    title = models.CharField(blank=True, max_length=100)
    title2 = models.CharField(blank=True, max_length=100)
    title3 = models.CharField(blank=True, max_length=100)
    etype = models.CharField(blank=True, max_length=100)
    to_be_cnt = models.IntegerField(blank=True, null=True)
    absentee = models.IntegerField(blank=True, null=True)
    precincts_reported = models.IntegerField(blank=True, null=True)
    total_precincts = models.IntegerField(blank=True, null=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s %s %s" % (self.title, self.title2, self.title3)


class CountyContestManager(models.Manager):
    def contest_results(self):
        """Gets the results of each contest instead of using manytomany field cuz this project needs to be done NOW"""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
            ctst.contest_id, ctst.title,
            ctst.reporting, ctst.numprec, ctst.pctrpt,
            cdt.name, cdt.party, cdt.vote, cdt.pct, cdt.last_update
        FROM
            open_elections_countycandidate cdt,
            open_elections_countycontest ctst
        WHERE
            cdt.contest_id = ctst.id
            AND cdt.show_on_web = True
            AND ctst.show_on_web = True
        ORDER BY
            ctst.contest_key ASC, cdt.vote DESC""")
        result_list = []
        for row in cursor.fetchall():
            result_list.append({'contest_id': row[0], 'title': row[1], 'reporting': row[2], 'numprec': row[3],
                'pctrpt': row[4], 'name': row[5], 'party': row[6], 'vote': row[7], 'pct': row[8], 'last_update': row[9]})
        return result_list

    # def old_contest_results(self):
    #     """Gets the results of each contest instead of using manytomany field cuz this project needs to be done NOW"""
    #     from django.db import connection
    #     cursor = connection.cursor()
    #     cursor.execute("""
    #     SELECT
    #         ctst.contest_key, ctst.title,
    #         ctst.reporting, ctst.numprec, ctst.pctrpt,
    #         cdt.name, cdt.party, cdt.vote, cdt.pct
    #     FROM
    #         elections_candidate cdt,
    #         elections_contest ctst
    #     WHERE
    #         cdt.contest_id = ctst.id
    #     ORDER BY
    #         ctst.contest_key ASC, cdt.vote DESC""")
    #     result_list = []
    #     for row in cursor.fetchall():
    #         result_list.append({'contest_key': row[0], 'title': row[1], 'reporting': row[2], 'numprec': row[3],
    #                             'pctrpt': row[4], 'name': row[5], 'party': row[6], 'vote': row[7], 'pct': row[8]})
    #     return result_list


class CountyContest(models.Model):
    """Describes the CONTEST element of the election.xml file
        <CONTEST key="6 " id="20" title="GOVERNOR - DEMOCRATIC" numberof="8" votefor="1"
           tcounted="0" tblank="0" tover="0" tunder="0" reporting="AV" numprec="1671" pctrpt="00.0" >
    """
    contest_key = models.IntegerField(blank=True, null=True)
    contest_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(blank=True, max_length=255)
    election = models.ForeignKey(CountyElection)
    numberof = models.IntegerField(blank=True, null=True)
    votefor = models.IntegerField(blank=True, null=True)
    tcounted = models.IntegerField(blank=True, null=True)
    tblank = models.IntegerField(blank=True, null=True)
    tover = models.IntegerField(blank=True, null=True)
    tunder = models.IntegerField(blank=True, null=True)
    reporting = models.CharField(blank=True, max_length=100)
    numprec = models.IntegerField(blank=True, null=True)
    pctrpt = models.IntegerField(blank=True, null=True)
    show_on_web = models.BooleanField(default=False)
    is_prop = models.BooleanField(default=False)
    chyron_name = models.CharField(blank=True, null=True, max_length=255)

    objects = CountyContestManager()

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.title


class StateContest(models.Model):
    """Describes the CONTEST element of the election.xml file"""
    #IF ContestIdentifier->Id[:4] == 1900
    #Prepend "Prop " + the last 2 digits of the ContestIdentifier to the Contest name
    contest_identifier = models.CharField(blank=True, null=True, max_length=12)
    contest_name = models.CharField(blank=False, null=False, max_length=255)
    precincts_reporting = models.IntegerField(blank=False, default=0)
    total_precincts = models.IntegerField(blank=False, default=0)
    pct_yes_votes = models.DecimalField(max_digits=4, decimal_places=1, blank=False, default=0)
    pct_no_votes = models.DecimalField(max_digits=4, decimal_places=1, blank=False, default=0)
    show_on_web = models.BooleanField(default=False)
    chyron_name = models.CharField(blank=True, null=True, max_length=255)
    #objects = StateContestManager()

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.contest_name


class StateCandidate(models.Model):
    """Holds the data for a state candidate record"""
    state_contest = models.ForeignKey(StateContest)
    candidate_identifier = models.IntegerField(blank=True, null=True)
    proposal_identifier = models.CharField(blank=True, null=True, max_length=255)
    candidate_name = models.CharField(blank=False, null=False, max_length=255)
    affiliation = models.CharField(blank=True, max_length=255)
    valid_votes = models.IntegerField(blank=False, default=0)
    pct_votes_party = models.DecimalField(max_digits=4, decimal_places=1, blank=False, default=0)
    pct_votes_race = models.DecimalField(max_digits=4, decimal_places=1, blank=False, default=0)
    referendum_option_identifier = models.CharField(blank=True, null=True, max_length=255)
    last_update = models.DateTimeField(blank=True, null=True, auto_now=True, auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.candidate_name


class CountyCandidate(models.Model):
    """Describes the CANDIDATE element of the election.xml file
        <CANDIDATE cankey="15" canid = "1" name = "EDMUND BROWN" party = " - DEM"
            cantype = "0" votes="0" pct="0.00" />
    """
    contest = models.ForeignKey(CountyContest)
    cankey = models.IntegerField(blank=True, null=True)
    conkey = models.IntegerField(blank=True, null=True)
    canid = models.IntegerField(blank=True, null=True)
    name = models.CharField(blank=True, max_length=100)
    party = models.CharField(blank=True, max_length=100)
    cantype = models.IntegerField(blank=True, null=True)
    vote = models.IntegerField(blank=True, null=True)
    pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True, auto_now=True, auto_now_add=True)
    show_on_web = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.name


class CountyContestResults(models.Model):
    """Holds the results for a contest for each county or 'Reporting Unit'"""

    class Meta:
        pass

    def __unicode__(self):
        pass


class Contest(models.Model):
    name = models.CharField(max_length=255)
    election_event = models.ForeignKey('ElectionEvent')
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    district = models.ForeignKey('District', blank=True, null=True)
    contest_type = models.ForeignKey('ContestType', blank=True, null=True)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"%s" % self.name


class ContestType(models.Model):
    contest_type = models.CharField(max_length=255, blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.contest_type

"""
class GuideManager(models.Manager):
    def get_guide_data(self):
        from django.db import connection
        cursor = connection.cursor()
        sql =
        SELECT
    can.*, con.*, mc.url,
    mc.short_description,
    mc.long_description
    FROM
        open_elections_candidate can
    LEFT JOIN open_elections_contest con ON(can.contest_id = con.id)
    LEFT JOIN open_elections_mediacoverage mc ON(can.id = mc.candidate_id)
    WHERE
    con.contest_type_id = (SELECT id FROM open_elections_contesttype WHERE contest_type = 'Mayoral')
    AND con.district_id = (SELECT id FROM open_elections_district WHERE district_type = 'city of san diego')
        cursor.execute('SELECT p.id, p.question, p.poll_date, COUNT(*) FROM polls_opinionpoll p, polls_response r WHERE p.id = r.poll_id GROUP BY 1, 2, 3 ORDER BY 3 DESC')
        result_list = []
        for row in cursor.fetchall():
            p = self.model(id=row[0], question=row[1], poll_date=row[2])
            p.num_responses = row[3]
            result_list.append(p)
        return result_list
"""


class Candidate(models.Model):
    PARTY_CHOICES = (
        (u'I', u'American Independent'),
        (u'A', u'Americans Elect'),
        (u'D', u'Democratic'),
        (u'G', u'Green'),
        (u'N', u'Independent'),
        (u'L', u'Libertarian'),
        (u'P', u'Peace and Freadom'),
        (u'R', u'Republican'),
    )
    PRO_CON_CHOICES = (
        (u'Y', u'Yes'),
        (u'N', u'No'),
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    pro_con = models.CharField(max_length=1, choices=PRO_CON_CHOICES, blank=True)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    URL = models.URLField(verify_exists=True, max_length=200, blank=True)
    headshot = models.FileField(upload_to='headshots/%Y/%m/%d', blank=True,
            null=True)
    contest = models.ForeignKey('Contest', blank=True, null=True)
    party = models.CharField(max_length=1, choices=PARTY_CHOICES, blank=True)
    current_position = models.CharField(max_length=255, blank=True)
    kpbs_profile = models.URLField("KPBS Profile URL", verify_exists=True, max_length=255, blank=True)
    kpbs_search = models.TextField("KPBS.org search strings (comma separated)", blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    is_proposition = models.BooleanField(default=False, blank=True)

    objects = models.Manager()  # The default manager
    # guide_manager = GuideManager()

    class Meta:
        pass

    def __unicode__(self):
        if self.is_proposition:
            return u"%s" % self.pro_con
        elif self.first_name and self.last_name:
            return u"%s %s" % (self.first_name, self.last_name)


class MediaCoverage(models.Model):
    url = models.URLField(verify_exists=True, blank=True, max_length=255)
    short_description = models.CharField(max_length=255, blank=True)
    long_description = models.TextField(blank=True)
    candidate = models.ForeignKey(Candidate, blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now_add=True, auto_now=True)
    media_coverage_type = models.ForeignKey('MediaCoverageType', blank=True)
    media_coverage_source = models.ForeignKey('MediaCoverageSource',
            blank=True, null=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s %s - %s %s pub_date:%s" % (self.candidate.first_name,
                self.candidate.last_name, self.media_coverage_type,
                self.short_description, self.pub_date)


class MediaCoverageType(models.Model):
    coverage_type = models.CharField(max_length=255)
    last_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % (self.coverage_type)


class MediaCoverageSource(models.Model):
    source_name = models.CharField(max_length=255, blank=True)
    source_organization = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(verify_exists=True, blank=True, max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        pass

    def __unicode__(self):
        return "%s, %s" % (self.source_name, self.source_organization)


class ContributionManager(models.Manager):
    def contribs_by_state(self, candidate_id):
            from django.db import connection
            cursor = connection.cursor()
            sql = """
            SELECT
                tran_state,
                count(*),
                sum(tran_amt1)
            FROM
                open_elections_contribution
            WHERE candidate_id = %s
            GROUP BY
                tran_state
            ORDER BY
                sum DESC""" % candidate_id
            cursor.execute(sql)
            result_list = []
            for row in cursor.fetchall():
                r = self.model()
                r.state = row[0]
                r.count = row[1]
                r.amount = row[2]
                result_list.append(r)
            return result_list

    def contribs_by_ca_county(self, candidate_id):
            from django.db import connection
            cursor = connection.cursor()
            sql = """
            SELECT
                z.county,
                count(c.*),
                sum(c.tran_amt1)
            FROM
                open_elections_contribution c,
                open_elections_californiazipcodes z
            WHERE
                c.tran_zip = z.zip_code
                AND c.candidate_id = %s
            GROUP BY
                z.county
            ORDER BY
                sum DESC""" % candidate_id
            cursor.execute(sql)
            result_list = []
            for row in cursor.fetchall():
                r = self.model()
                r.county = row[0]
                r.count = row[1]
                r.amount = row[2]
                result_list.append(r)
            return result_list

    def contribs_by_zip(self, candidate_id):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                z.zip_code,
                count(c.*),
                sum(c.tran_amt1)
            FROM
                open_elections_contribution c,
                open_elections_californiazipcodes z
            WHERE
                c.tran_zip = z.zip_code
            AND c.candidate_id = %s
            GROUP BY
                z.zip_code
            ORDER BY
                sum DESC
            LIMIT 10""", [candidate_id])
        result_list = []
        for row in cursor.fetchall():
            r = self.model()
            r.zip_code = row[0]
            r.count = row[1]
            r.amount = row[2]
            result_list.append(r)
        return result_list


class Contribution(models.Model):
    """Stores campaign contributions from candidates in the state of California"""
    COMMITTEE_TYPE_CHOICES = (
            (u'BMC', u'Ballot Measure Committee'),
            (u'CAO', u'Candidate/Office-holder'),
            (u'CTL', u'Controlled Committee'),
            (u'MDI', u'Major Donor/Ind Expenditure'),
            (u'RCP', u'Recipient Committee'),
            (u'SMO', u'Slate Mailer Organization'),
        )
    FORM_TYPE_CHOICES = (
            (u'A', u'Sched A / Monetary'),
            (u'C', u'Non-monetary'),
            (u'I', u'Misc. to Cash'),
            (u'F401A', u'Payments Received'),
            (u'F496P3', u'Contributions of $100 or More Received'),
        )
    TRANSACTION_TYPE_CHOICES = (
            (u'F', u'Forgiven Loan'),
            (u'I', u'Intermediary'),
            (u'R', u'Returned (Negative Amount?)'),
            (u'T', u'Third Party Repayment'),
            (u'X', u'Transfer'),
        )
    candidate = models.ForeignKey(Candidate)
    filer_id = models.IntegerField(blank=True)
    filer_naml = models.CharField("Filer name", max_length=200, blank=True)
    report_num = models.IntegerField(max_length=3, blank=True)
    committee_type = models.CharField(max_length=3, choices=COMMITTEE_TYPE_CHOICES, blank=True)
    rpt_date = models.DateField("Date report was filed", blank=True)
    from_date = models.DateField("Reporting period from date", blank=True)
    thru_date = models.DateField("Reporting period to date", blank=True)
    elect_date = models.DateField("Date of election", blank=True, null=True)
    rec_type = models.CharField("Record type", max_length=4, blank=True)
    form_type = models.CharField(max_length=6, choices=FORM_TYPE_CHOICES, blank=True)
    tran_id = models.CharField(max_length=20, blank=True)
    entity_cd = models.CharField(max_length=3, choices=COMMITTEE_TYPE_CHOICES, blank=True)
    tran_naml = models.CharField("Last name", max_length=200)
    tran_namf = models.CharField("First name", max_length=45)
    tran_namt = models.CharField(max_length=10)
    tran_nams = models.CharField(max_length=10, blank=True)
    tran_adr1 = models.CharField("Address 1", max_length=55)
    tran_adr2 = models.CharField("Address 2", max_length=55, blank=True)
    tran_city = models.CharField("City", max_length=30)
    tran_state = models.CharField("State", max_length=2)
    tran_zip = models.CharField("Zip code", max_length=5)
    tran_emp = models.CharField("Employer", max_length=200)
    tran_occ = models.CharField("Occupation", max_length=60)
    tran_self = models.BooleanField("Is self-employed", blank=True)
    tran_type = models.CharField("Transaction type", choices=TRANSACTION_TYPE_CHOICES, max_length=1, blank=True)
    tran_date = models.DateField("Transaction Date")
    tran_date1 = models.DateField("Transction Date 1", blank=True, null=True)
    tran_amt1 = models.DecimalField("Transaction amount", max_digits=12,
            decimal_places=2)
    tran_amt2 = models.DecimalField("Transaction amount 1", max_digits=12,
            decimal_places=2, blank=True)
    tran_dscr = models.CharField(max_length=255, blank=True)
    cmte_id = models.CharField(max_length=9, blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s - Form type: %s" % (self.tran_amt1, self.form_type)

    objects = ContributionManager()


class ContributionZipCode(models.Model):
    """Stores the latitude and longitude for zip codes of the contributions"""
    zip_code = models.CharField(max_length=5)
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s %s, %s" % (self.zip_code, self.latitude, self.longitude)


class District(models.Model):
    name = models.CharField(max_length=255)
    district_type = models.CharField(blank=True, null=True, max_length=50)  # TODO: add district types
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.district_type)


class ElectionEvent(models.Model):
    name = models.CharField(max_length=255)
    event_date = models.DateField(null=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.event_date)


class Endorsement(models.Model):
    candidate = models.ForeignKey('Candidate')
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=100, null=True)
    organization = models.CharField(max_length=255, null=True)
    endorsement_date = models.DateField()
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        pass

    def __unicode__(self):
        endorser = ''
        if self.first_name:
            endorser = u"%s " % self.first_name
        if self.last_name:
            endorser += u"%s " % self.last_name
        if self.organization:
            endorser += u"%s" % self.organization
        if endorser != '':
            return endorser
        else:
            return u"No endorser name or organization entered yet"


class CaliforniaZipCodes(models.Model):
    zip_code = models.IntegerField(max_length=5)
    city = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class ApContest(models.Model):
    office = models.CharField(max_length=255)
    precincts_pct = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return u"%s" % self.office


class ApCandidate(models.Model):
    name = models.CharField(max_length=255)
    candidate_id = models.IntegerField(max_length=6, null=True)
    party = models.CharField(max_length=20)
    popular_vote = models.IntegerField(max_length=10, default=0)
    popular_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    states_won = models.IntegerField(max_length=3, default=0)
    electoral_votes = models.IntegerField(max_length=3, default=0)
    contest = models.ForeignKey(ApContest)
    show_on_web = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s" % self.name


class FtpCredential(models.Model):
    identifier = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

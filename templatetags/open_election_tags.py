from django import template
import re

register = template.Library()


def do_get_contest(parser, token):
    """
    Gets the data for the election guide using the contest type to pull
    contest_types include: 'proposition', 'local',
    'congressional', 'presidential'
    """
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    contest_type, district_type, var_name = m.groups()
    if not (contest_type[0] == contest_type[-1] and contest_type[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    if not (district_type[0] == district_type[-1] and district_type[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return GetContestNode(contest_type[1:-1], district_type[1:-1], var_name)


class GetContestNode(template.Node):
    def __init__(self, contest_type, district_type, var_name):
        self.contest_type = contest_type
        self.district_type = district_type
        self.var_name = var_name

    def render(self, context):

        from open_elections.models import Candidate
        context[self.var_name] = Candidate.objects.select_related().filter(contest__contest_type__contest_type=self.contest_type).filter(contest__district__district_type=self.district_type).order_by('contest', 'last_name', 'pro_con')
        return ''

register.tag('get_contest', do_get_contest)


def do_get_contributions(parser, token):
    """
        Gets the contributions for a mayoral candidate filtered by state or
        California county based on the candidate ID
        Usage: <% get_contributions {county||state} [candidate_id} as [var_name] %>
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    locale, candidate_id, var_name = m.groups()
    if not (locale[0] == locale[-1] and locale[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    #if not (candidate_id[0] == candidate_id[-1] and candidate_id[0] in ('"', "'")):
        #raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return GetContributionsNode(locale[1:-1], candidate_id, var_name)


class GetContributionsNode(template.Node):
    def __init__(self, locale, candidate_id, var_name):
        self.locale = locale
        self.candidate_id = candidate_id
        self.var_name = var_name

    def render(self, context):

        from open_elections.models import Contribution
        if self.locale == 'county':
            context[self.var_name] = Contribution.objects.contribs_by_ca_county(self.candidate_id)
        elif self.locale == 'state':
            context[self.var_name] = Contribution.objects.contribs_by_state(self.candidate_id)
        elif self.locale == 'zip':
            context[self.var_name] = Contribution.objects.contribs_by_zip(self.candidate_id)
        return ''

register.tag('get_contributions', do_get_contributions)

from __future__ import division
import csv

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from open_elections.models import *


def emit_county_csv_results(request):
    """Returns a CSV file to be parsed for use by KPBS.org"""
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=county_election_results.csv'
    csv.register_dialect('county_csv', delimiter=',', quoting=csv.QUOTE_ALL)
    writer = csv.writer(response, 'county_csv')
    writer.writerow(['contest_id', 'title', 'reporting', 'numprec', 'pctrpt', 'name', 'party', 'vote', 'pct', 'last_update'])

    contests = CountyContest.objects.values_list('contest_id', 'title', 'reporting',
        'numprec', 'pctrpt', 'countycandidate__name', 'countycandidate__party',
        'countycandidate__vote', 'countycandidate__pct', 'countycandidate__last_update').order_by('contest_key',
        '-countycandidate__vote')
    for c in contests:
        writer.writerow([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9].strftime("%A %B %e, %Y %I:%M %p")])

    return response

def emit_state_csv_results(request):
    """Returns a CSV file to be parsed for use by KPBS.org"""
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=state_election_results.csv'
    writer = csv.writer(response)
    writer.writerow(['contest_identifier', 'contest_name', 'precincts_reporting', 'total_precincts', 'candidate_name', 'affiliation', 'total_votes', 'percent_votes', 'referendum_option_identifier'])
    candidates = StateCandidate.objects.select_related().order_by('state_contest', '-valid_votes').filter(state_contest__show_on_web=True)
    candidate_name = ''
    for c in candidates:
        if c.candidate_name:
            candidate_name = c.candidate_name
        elif c.proposal_identifier:
            candidate_name = c.referendum_option_identifier
        writer.writerow([c.state_contest.contest_identifier,
                         c.state_contest.contest_name,
                         c.state_contest.precincts_reporting,
                         c.state_contest.total_precincts,
                         smart_str(candidate_name),
                         c.affiliation,
                         c.valid_votes,
                         c.pct_votes_race,
                         c.referendum_option_identifier,
                         c.last_update.strftime("%A %B %e, %Y %I:%M %p")])
    return response


def emit_jason_results(request):
    """docstring for emit_jason_results"""
    pass

def get_candidate_json(request):
    """Returns a the information about each candidate (person or prop) as JSON"""
    candidate_json = serializers.serialize('json', Candidate.objects.all())
    return HttpResponse(candidate_json, mimetype="application/json")

def get_candidates(request):
    """Returns a the information about each candidate (person or prop)"""
    candidates = Candidate.objects.all()
    return render_to_response('election_guide.html',
            {'candidates': candidates},
                          context_instance=RequestContext(request))

def get_candidate_contributions(request):
    """Returns a the information about each candidate (person or prop)"""
    contributions = Contribution.objects.select_related().order_by('candidate',
            'tran_naml', 'tran_namf')
    return render_to_response('contributions.html',
            {'contributions': contributions},
                          context_instance=RequestContext(request))

def emit_contribution_csv(request, filer_id=''):
    """Returns a CSV file to be parsed for use by KPBS.org"""
    if filer_id == '':
        pass
    else:
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % filer
        csv.register_dialect('contrib_csv', delimiter=',', quoting=csv.QUOTE_ALL)
        writer = csv.writer(response, 'contrib_csv')
        writer.writerow(['tran_amt', 'zip_code'])

        contribs = Contribution.objects.filter()
        for c in contribs:
            writer.writerow([c['tran_amt'], c['zip_code']])

        return response

def get_contests_for_voter_guide(request):
    """Returns contest and candidate data. Can be called using a number of
    different identifiers including contest ID, contest name, contest type or
    district"""
    # from  open_elections.models import Contest

    # if request.GET:
    #     if request.GET.get('contest_id'):
    #         identifier = request.GET['contest_id']
    #     elif request.GET.get('contest_name'):
    #         identifier = request.GET['contest_name']
    #     elif request.GET.get('contest_type'):
    #         identifier = request.GET['contest_type']
    #     elif request.GET.get('contest_district'):
    #         identifier = request.GET['contest_district']
    #     key = request.GET.items()[0][0]
    #     value = request.GET.items()[0][1]
    # else:
    #     identifier = 'nada' #TODO: return a 404 here get_object_or_404

    return render_to_response('election_guide.html',
            {}, context_instance=RequestContext(request))


def get_contests_for_voter_guide_dev(request):
    """Returns contest and candidate data. Can be called using a number of
    different identifiers including contest ID, contest name, contest type or
    district"""
    # from  open_elections.models import Contest

    # if request.GET:
    #     if request.GET.get('contest_id'):
    #         identifier = request.GET['contest_id']
    #     elif request.GET.get('contest_name'):
    #         identifier = request.GET['contest_name']
    #     elif request.GET.get('contest_type'):
    #         identifier = request.GET['contest_type']
    #     elif request.GET.get('contest_district'):
    #         identifier = request.GET['contest_district']
    #     key = request.GET.items()[0][0]
    #     value = request.GET.items()[0][1]
    # else:
    #     identifier = 'nada' #TODO: return a 404 here get_object_or_404

    return render_to_response('election_guide_dev.html',
            {}, context_instance=RequestContext(request))


def get_county_pres_results_for_chart(request):
    results = CountyCandidate.objects.filter(cankey__in=[7, 10])
    pct_rpt = results[0].contest.pctrpt
    return render_to_response('chart_data.html', {'results': results, 'pct_rpt': pct_rpt}, context_instance=RequestContext(request))



def get_map(request):
    return render_to_response('map.html',
                              {},
                              context_instance=RequestContext(request))



### IT shouldn't need to be dependent on this other application
### I figure people can install it if they want to...
# from endless_pagination.decorators import page_template

@csrf_exempt
# @page_template("demaio_contributors.html")
# @page_template("filner_contributors.html", key="filner_contributors")
def searchable_map(request, template="searchable_map.html",
    extra_context=None):
    from django.db.models import Sum

    if request.REQUEST.get('d_search_submit'):
        params = {}
        form = ContributionForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            if form.cleaned_data['tran_namf']:
                params['tran_namf__icontains'] = form.cleaned_data['tran_namf']
            if form.cleaned_data['tran_naml']:
                params['tran_naml__icontains'] = form.cleaned_data['tran_naml']
            if form.cleaned_data['tran_emp']:
                params['tran_emp__icontains'] = form.cleaned_data['tran_emp']
            if form.cleaned_data['tran_zip']:
                params['tran_zip'] = form.cleaned_data['tran_zip']
            params['candidate'] = 2
        elif request.method == 'GET' and request.GET['d_search_submit']:
            if request.GET.get('tran_namf', ''):
                params['tran_namf__icontains'] = request.GET.get('tran_namf', '')
            if request.GET.get('tran_naml', ''):
                params['tran_naml__icontains'] = request.GET.get('tran_naml', '')
            if request.GET.get('tran_emp', ''):
                params['tran_emp__icontains'] = request.GET.get('tran_emp', '')
            if request.GET.get('tran_zip', ''):
                params['tran_zip'] = request.GET.get('tran_zip', '')
            params['candidate'] = 2
        demaio_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(**params).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        filner_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(candidate_id=3).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        context = {'demaio_contribs': demaio_contribs, 'filner_contribs': filner_contribs, 'form': form, 'search_submit': 'd_search_submit'}
    elif request.REQUEST.get('f_search_submit'):
        params = {}
        params['candidate'] = 3
        form = ContributionForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            if form.cleaned_data['tran_namf']:
                params['tran_namf__icontains'] = form.cleaned_data['tran_namf']
            if form.cleaned_data['tran_naml']:
                params['tran_naml__icontains'] = form.cleaned_data['tran_naml']
            if form.cleaned_data['tran_emp']:
                params['tran_emp__icontains'] = form.cleaned_data['tran_emp']
            if form.cleaned_data['tran_zip']:
                params['tran_zip'] = form.cleaned_data['tran_zip']
        elif request.method == 'GET' and request.GET['f_search_submit']:
            if request.GET.get('tran_namf', ''):
                params['tran_namf__icontains'] = request.GET.get('tran_namf', '')
            if request.GET.get('tran_naml', ''):
                params['tran_naml__icontains'] = request.GET.get('tran_naml', '')
            if request.GET.get('tran_emp', ''):
                params['tran_emp__icontains'] = request.GET.get('tran_emp', '')
            if request.GET.get('tran_zip', ''):
                params['tran_zip'] = request.GET.get('tran_zip', '')
        filner_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(**params).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        demaio_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(candidate_id=2).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        context = {'demaio_contribs': demaio_contribs, 'filner_contribs': filner_contribs, 'form': form, 'search_submit': 'f_search_submit'}
    else:
        demaio_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(candidate_id=2).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        filner_contribs = Contribution.objects.values('tran_namf', 'tran_naml', 'tran_emp', 'tran_zip').filter(candidate_id=3).annotate(amount=Sum('tran_amt1')).order_by('-amount', 'tran_naml')
        form = ContributionForm()
        context = {
            'demaio_contribs': demaio_contribs,
            'demaio_grid_title': 'All Contributors',
            'filner_contribs': filner_contribs,
            'filner_grid_title': 'All Contributors',
            'form': form
        }
        if extra_context is not None:
            context.update(extra_context)
    return render_to_response(template, context, context_instance=RequestContext(request))



## --- Our Chyron may not be so useful for others...
def emit_chyron_xml_results(request):
    """Returns an XML file to be parsed for use by KPBS TV"""
    # Excluded values are kpbs_elections_countycontest.contest_id includes presidential & congress
    county_excluded = [5, 10, 15, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75,
    139, 375, 380, 395, 400, 445, 450, 455, 460, 465, 470, 475, 480, 485, 490,
    495, 500, 505, 510, 515, 520, 525, 530, 545, 550, 555, 560, 565, 570, 575,
    580, 585, 590, 595, 600, 605, 610, 615, 620, 625, 630, 635, 640, 645, 650,
    655, 660, 665, 670, 675, 680]
    county_candidates = CountyCandidate.objects.all().order_by('contest__contest_key', '-pct').exclude(contest__contest_id__in=county_excluded)
    state_candidates = StateCandidate.objects.select_related().order_by('state_contest', '-valid_votes').filter(state_contest__show_on_web=True)
    pres_candidates = ApCandidate.objects.select_related().filter(show_on_web=True).order_by('-popular_vote')
    return render_to_response('chyron.xml', {'county_candidates': county_candidates, 'state_candidates': state_candidates, 'pres_candidates': pres_candidates}, context_instance=RequestContext(request), mimetype="text/xml")


def emit_chyron_county_html_table(request):
    """Returns an HTML table to be parsed for use by KPBS TV"""
    county_candidates = CountyCandidate.objects.all().filter(show_on_web=True).order_by('contest__contest_key', '-pct')
    state_candidates = StateCandidate.objects.select_related().order_by('state_contest', '-valid_votes').filter(state_contest__show_on_web=True)
    pres_candidates = ApCandidate.objects.select_related().filter(show_on_web=True).order_by('-popular_vote')
    return render_to_response('chyron_table.html', {'county_candidates': county_candidates, 'state_candidates': state_candidates, 'pres_candidates': pres_candidates}, context_instance=RequestContext(request))



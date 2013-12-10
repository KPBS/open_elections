from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Election results
    # (r'^$', 'open_elections.views.main_template'), ## set primary template here
    (r'^fetch-county-results$', 'open_elections.views.emit_county_csv_results'),
    (r'^fetch-state-results$', 'open_elections.views.emit_state_csv_results'),

    # Candidate info Examples
    (r'^get-candidate-json$', 'open_elections.views.get_candidate_json'),
    (r'^get-candidates/?$', 'open_elections.views.get_candidates'),

    # Contest ID, contest name, contest type or district
    (r'^get-contests/$', 'open_elections.views.get_contests_for_voter_guide'),

    # Contributions Guide Examples
    (r'^emit-contributions/(?P<filer_id>.*)/?$', 'open_elections.views.emit_contribution_csv'),
    (r'^get-contributions/?$', 'open_elections.views.get_candidate_contributions'),

    # Voter Guide examples
    (r'^voter-guide$', 'open_elections.views.get_contests_for_voter_guide'),
    (r'^voter-guide-dev$',
        'open_elections.views.get_contests_for_voter_guide_dev'),

                       
    # Charts Example
    (r'^county-pres-chart$', 'open_elections.views.get_county_pres_results_for_chart'),

    # Maps Example
    (r'^map$', 'open_elections.views.get_map'),
    (r'^searchable-map$', 'open_elections.views.searchable_map'),

    # Chyron formatted results Examples
    (r'^fetch-chyron-result$', 'kpbs_elections.views.emit_chyron_xml_results'),
    (r'^fetch-chyron-county-html-table$', 'open_elections.views.emit_chyron_county_html_table'),
)

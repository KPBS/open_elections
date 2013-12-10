from django.contrib import admin
from .models import *


class MediaCoverageInline(admin.StackedInline):
    model = MediaCoverage
    extra = 3


class CandidateAdmin(admin.ModelAdmin):
    list_filter = ('contest__election_event',)
    list_display = ('first_name', 'last_name',  'contest', 'party', 'pro_con',)
    list_display_links = ('last_name',)
    ordering = ('contest',)
    inlines = [MediaCoverageInline]
    search_fields = ['first_name', 'last_name', 'contest__name']
admin.site.register(Candidate, CandidateAdmin)


class ContestAdmin(admin.ModelAdmin):
    list_display = ('name', 'election_event',)
    search_fields = ['name', 'election_event__name',]
admin.site.register(Contest, ContestAdmin)


class ContestTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContestType, ContestTypeAdmin)


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('filer_naml', 'tran_naml', 'tran_namf', 'tran_city',
      'tran_amt1', 'tran_date', 'tran_amt2', 'tran_emp',)
    search_fields = ['filer_naml', 'tran_naml', 'tran_namf', 'tran_city',
        'tran_amt1', 'tran_amt2', 'tran_emp', 'tran_date']
    list_filter = ('candidate', 'filer_naml')
admin.site.register(Contribution, ContributionAdmin)


class DistrictAdmin(admin.ModelAdmin):
    pass
admin.site.register(District, DistrictAdmin)


class ElectionEventAdmin(admin.ModelAdmin):
    pass
admin.site.register(ElectionEvent, ElectionEventAdmin)


class EndorsementAdmin(admin.ModelAdmin):
    pass
admin.site.register(Endorsement, EndorsementAdmin)


def remove_candidates_from_web_display(modeladmin, request, queryset):
    queryset.update(show_on_web=False)
remove_candidates_from_web_display.short_description = "Don't show selected candidates on web"


class CountyCandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'contest', 'party', 'show_on_web')
    search_fields = ['name', 'contest__title', 'party']
    actions = [remove_candidates_from_web_display]
admin.site.register(CountyCandidate, CountyCandidateAdmin)


class CountyContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_on_web', 'is_prop')
admin.site.register(CountyContest, CountyContestAdmin)


class CountyElectionAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(CountyElection, CountyElectionAdmin)


class StateCandidateAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'affiliation')
admin.site.register(StateCandidate, StateCandidateAdmin)


class StateContestAdmin(admin.ModelAdmin):
    list_display = ('contest_name', 'show_on_web')
admin.site.register(StateContest, StateContestAdmin)


class ContributionZipCodeAdmin(admin.ModelAdmin):
    list_display = ('zip_code', 'latitude', 'longitude',)
admin.site.register(ContributionZipCode, ContributionZipCodeAdmin)


class MediaCoverageAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'short_description', 'pub_date')
admin.site.register(MediaCoverage, MediaCoverageAdmin)


class MediaCoverageTypeAdmin(admin.ModelAdmin):
    list_display = ('coverage_type',)
admin.site.register(MediaCoverageType, MediaCoverageTypeAdmin)

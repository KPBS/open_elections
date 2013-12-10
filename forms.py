from django import forms
from .models import Contribution

class ContributionForm(forms.Form):
    tran_naml = forms.CharField(max_length=200, required=False)
    tran_namf = forms.CharField(max_length=45, required=False)
    tran_emp = forms.CharField(max_length=200, required=False)    
    tran_zip = forms.CharField(required=False)
    candidate_id = forms.CharField(max_length=5, required=False)

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.conf import settings



FILE_CHOICES = (
    ('application/xml+tei', 'tei'),
    ('application/xml+tcf', 'tcf'),
    ('text/plain', 'plain text')
)

ZIP_CHOICES = (
    ('zip', 'zip'),
    ('rar', 'rar'),
)

OUTPUT_CHOICES = ( 
    ('application/xml+tei', 'tei'),
    ('application/xml+tcf', 'tcf'),
    ('application/json+acdhlang', 'Json')
)


class GenericFilterFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(GenericFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.add_input(Submit('Filter', 'search'))


class NLPPipeForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=FILE_CHOICES
    )
    zip_type = forms.ChoiceField(
        choices=ZIP_CHOICES,
        hidden=True
    )
    out_format = forms.ChoiceField(choices=OUTPUT_CHOICES, label="Output format")
    profile = forms.ChoiceField(required=False)
    nlp_pipeline = forms.CharField(required=False, help_text="""e.g. [["acdh-tokenizer", {"profile": "default"}], ["spacy", {"language": "de"}]]""")
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(NLPPipeForm, self).__init__(*args, **kwargs)
        print(self.fields)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        pr = getattr(settings, 'SPACYAPP_PROFILES', [])
        ch2 = [('---', '----'), ]
        for p in pr:
            print(p)
            ch2.append((p['title'], p['verbose'] ))
        self.fields['profile'].choices = tuple(ch2)
        # self.helper.add_input(Submit('submit', 'submit'),)


class TokenForm(forms.Form):
    token = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(TokenForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'submit'),)


class LongTextForm(forms.Form):
    longtext = forms.CharField(required=False, widget=forms.Textarea)
    # dont_split = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(LongTextForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'submit'),)

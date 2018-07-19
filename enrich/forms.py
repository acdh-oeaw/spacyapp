from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

FILE_CHOICES = (
    ('tei', 'tei'),
    ('tcf', 'tcf'),
)

ZIP_CHOICES = (
    ('zip', 'zip'),
    ('rar', 'rar'),
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
        choices=ZIP_CHOICES
    )
    nlp_pipeline = forms.CharField(
        initial='acdh-tokenizer,spacy-tagger,spacy-parser,spacy-ner'
    )
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(NLPPipeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
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

    def __init__(self, *args, **kwargs):
        super(LongTextForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'submit'),)

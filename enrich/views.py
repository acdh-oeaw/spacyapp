import spacy
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import TokenForm, LongTextForm
from django.shortcuts import render_to_response

nlp = spacy.load('de_core_news_sm')


class TextParser(FormView):
    template_name = 'enrich/textparser.html'
    form_class = LongTextForm
    success_url = '.'

    def form_valid(self, form, **kwargs):
        context = super(TextParser, self).get_context_data(**kwargs)
        cd = form.cleaned_data
        longtext = cd['longtext']
        context['longtext'] = None
        if longtext:
            doc = nlp("{}".format(longtext))
            context['longtext'] = longtext
            sents = [x for x in doc.sents]
            result = []
            for x in sents:
                chunk = {}
                chunk['sent'] = x
                chunk['tokens'] = []
                for y in x:
                    parts = {}
                    parts['text'] = y.text
                    parts['lemma'] = y.lemma_
                    parts['pos'] = y.pos_
                    parts['tag'] = y.tag_
                    parts['dep'] = y.dep_
                    parts['shape'] = y.shape_
                    parts['is_alpha'] = y.is_alpha
                    chunk['tokens'].append(parts)
                result.append(chunk)
            context['result'] = result
        return render(self.request, self.template_name, context)


class Lemmatize(FormView):
    template_name = 'enrich/lemmatize.html'
    form_class = TokenForm
    success_url = '.'

    def form_valid(self, form, **kwargs):
        context = super(Lemmatize, self).get_context_data(**kwargs)
        cd = form.cleaned_data
        token = cd['token']
        context['token'] = None
        if token:
            doc = nlp("{}".format(token))[0]
            context['token'] = doc
            context['lemma'] = doc.lemma_
            context['pos'] = doc.pos_
            context['tag'] = doc.tag_
        return render(self.request, self.template_name, context)


def NLPPipelineView(request):
    return render_to_response('enrich/nlppipeline.html')

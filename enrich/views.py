import spacy
import json
from spacy import displacy
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from .forms import TokenForm, LongTextForm, NLPPipeForm
from django.shortcuts import render_to_response
from django_celery_results.models import TaskResult

nlp = spacy.load(r"C:\Users\pandorfer\Documents\Redmine\prodigy\work\vfbr\vfbr-fam-model")


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
            context['vis'] = displacy.render(doc, style='ent')
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


class NLPPipeView(FormView):
    template_name = 'enrich/nlppipeline.html'
    form_class = NLPPipeForm
    success_url = '.'


class DownloadView(TemplateView):
    template_name = 'enrich/download.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tt = TaskResult.objects.get(task_id=context['proc_id'])
        t = False
        if tt.status == 'SUCCESS':
            try:
                t = TaskResult.objects.get(task_id=json.loads(tt.result)['id_docs'])
            except TaskResult.DoesNotExist:
                t = False
        if t:
            if t.status == 'SUCCESS':
                p = json.loads(t.result)['path']
                context['finished'] = True
                context['path'] = p
            else:
                context['finished'] = False
        else:
            context['finished'] = False
        return context

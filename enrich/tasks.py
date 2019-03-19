import datetime
import shutil
import zipfile
import os
from os import listdir, makedirs, path
import json
from lxml import etree

import lxml.etree as et
import requests
from celery import chord, current_task, shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User

from .custom_parsers import JsonToDocParser, process_tokenlist
from spacytei.tei import TeiReader
from spacytei.pipeline import SpacyProcess, XtxProcess
from spacytei.conversion import Converter


PROCESS_MAPPING = {
    'acdh-tokenizer': XtxProcess,
    'spacy': SpacyProcess,
}


@shared_task(time_limit=500)
def pipe_zip_files(
        results,
        fld_out,
        dwld_dir,
        fn,
        user_id=None
):  # TODO: use the results for zip creation
    zipf = zipfile.ZipFile(
        '{}_output.zip'.format(fn, ),
        'w',
        zipfile.ZIP_DEFLATED,
    )
    for filename in listdir(fld_out):
        zipf.write(path.join(fld_out, filename), filename)
    zipf.close()
    shutil.copy('{}_output.zip'.format(fn, ), '{}{}_output.zip'.format(
        dwld_dir,
        os.path.split(fn)[1],
    ))
    path_2 = '{}{}_output.zip'.format(dwld_dir, os.path.split(fn)[1])
    user_1 = False
    if user_id is not None:
        user_1 = User.objects.get(id=int(user_id))
        if user_1.email is None:
            user_1 = False
    if user_1:
        message = """Your job has finished.
        Please download the file under:
            https://spacyapp.eos.arz.oeaw.ac.at/{}""".format(path_2)
        html_message = """<p>Your job has finished.<br/>
        <b>Please download the file under:</b>
            <a href="https://spacyapp.eos.arz.oeaw.ac.at/{0}">{0}</a></p>""".format(path_2)
        send_mail(
            'spacyTEI job finished',
            message,
            'acdh-tech@oeaw.ac.at',
            [user_1.email, ],
            fail_silently=True,
            html_message=html_message
        )  # TODO: Make the base url not hard coded
    return {
        'success': True,
        'path': path_2
    }


@shared_task(time_limit=6000)
def process_file_new(file, pipeline, file_type, fld_out, out_format="application/json+acdhlang"):
    with open(file, 'r') as res:
        res = res.read()
        out_format_file = None
        orig_process = None
        context = None
        for p in pipeline:
            proc = PROCESS_MAPPING[p[0]](mime=file_type, payload=res, context=context, options=p[1])
            context = proc.context
            res = proc.process()
            out_format_file = proc.returns
#            if orig_process is None:
            orig_process = proc
        if out_format != out_format_file:
           res = Converter(data=res, data_type=out_format_file, original_process=orig_process).convert(out_format) 
        with open(path.join(fld_out, file.split('/')[-1]), 'w') as outfile:
            if type(res) == str:
                outfile.write(res)
            elif type(res) == list:
                json.dump(res, outfile)
            else:
                outfile.write(etree.tostring(res, pretty_print=True, encoding='unicode')) # TODO: need a better check for lxml etree here

        return {
            'success': True,
            'path': path.join(
                fld_out,
                file.split('/', )[-1],
            )
        }


@shared_task(time_limit=1800)
def pipe_process_files(pipeline, file, fn, options, user, zip_type, file_type, user_id=None, out_format="application/json+acdhlang"):
    dwld_dir = getattr(settings, "SPACYAPP_DOWNLOAD_DIR", 'download/')
    #print(file_type)
    if zip_type is not None:
        makedirs('{}_folder'.format(fn))
        makedirs('{}_output'.format(fn))
        zip_ref = zipfile.ZipFile(file, 'r')
        fld_proc = '{}_folder'.format(fn)
        fld_out = '{}_output'.format(fn)
        zip_ref.extractall(fld_proc)
        zip_ref.close()
        lst_dir = listdir(fld_proc)
        #print(lst_dir)
        res_group = chord(
            process_file_new.s(
                path.join(fld_proc, fn), pipeline, file_type, fld_out, out_format)
            for fn in lst_dir)(pipe_zip_files.s(fld_out, dwld_dir, fn, user_id))
        return {
            'success': True,
            'id_docs': res_group.id,
            'path': '{}{}_output.zip'.format(
                dwld_dir,
                os.path.split(fn)[1],
            )
        }

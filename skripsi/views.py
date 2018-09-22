from django.shortcuts import render, redirect

import json
import ast
import math
from skripsi.models import CrawlNews, Kelas
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
# Create your views here.

def masukkan(request):
    return render(request, 'beranda/index.html')


def simpan(request):
    json_data = open('assets/detik.json')
    baca_file = json.load(json_data)
    # baca_file = json.dumps(json_data) // json formatted string

    # json.dumps(json_data)

    for p in baca_file:
        headline = p['headline']
        main_headline = p['main_headline']
        date = p['date']
        url = p['url']
        content = p['content']

        # save if not exist data
        CrawlNews.objects.get_or_create(
            headline=headline,
            main_headline=main_headline,
            date=date,
            url=url,
            content=content
        )

    json_data.close()
    # baca_db = CrawlNews.objects.all().order_by('-id')

    crawls = CrawlNews.objects.all().order_by('-id')
    paginator = Paginator(crawls, 5)
    page = request.GET.get('page')
    try:
        crawls = paginator.page(page)
    except PageNotAnInteger:
        crawls = paginator.page(1)
    except EmptyPage:
        crawls = paginator.page(paginator.num_pages)
    return render(request, 'beranda/simpan.html', {'crawl': crawls})

    # return render(request, 'beranda/simpan.html', {"baca_json": baca_db})


def preproses(request):
    baca_db = CrawlNews.objects.all()
    kounter = 0
    for baca in baca_db:
        kounter += 1
        if kounter > 1 and kounter <= 3:
            # create stemmer
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            # stemming process
            sentence = baca.headline + " " + baca.content
            output = stemmer.stem(sentence)
            baca.stemming = output

            # ------------------- Stopword Removal
            fa = StopWordRemoverFactory()
            stopword = fa.create_stop_word_remover()
            kalimat = output
            stop = stopword.remove(kalimat)
            stop = stop.replace(' - ', ' ')
            output = stop
            baca.stopword = output

            baca.save()

    return render(request, 'beranda/preprocessing.html', {"rootword": output, "ori": sentence})


def hitung_term(request):
    baca_db = CrawlNews.objects.all()
    kounter = 0
    for baca in baca_db:
        kounter += 1
        if kounter > 1 and kounter <= 2:
            counts = dict()
            # get from db >> stopword
            str_db = baca.stopword
            words = str_db.split()
            for word in words:
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1
            baca.count_term = ast.literal_eval(json.dumps(counts))
            baca.sum_all_word = len(counts)
            baca.save()
    return render(request, 'beranda/term.html', {'priview': ast.literal_eval(json.dumps(counts))})

def tf_idf(request):
    baca_db = CrawlNews.objects.all()
    # count_doc = baca_db.count() #jumlah dokumen
    count_doc = 3

    # document frequency (df)
    df = dict()
    for i, iterasi_df in enumerate(baca_db, start=0):
        if i<3:
            ct = ast.literal_eval(iterasi_df.count_term)
            for k,v in ct.items():
                if k in df:
                    df[k] += v
                else:
                    df[k] = v
    # print(ast.literal_eval(json.dumps(df)))
    # print('---------------^df------------------')

    # term frequency (tf)
    tf = dict()
    for i, iter_df in enumerate(baca_db, start=0):
        if i<3:
            tf_i = df.fromkeys(df, 0)
            ct = ast.literal_eval(iter_df.count_term)
            for ke,va in ct.items():
                if ke in df:
                    tf_i[ke] = va
            tf[iter_df.id] = tf_i
    print(ast.literal_eval(json.dumps(tf)))
    print('----------------^tf-----------------')

    # inverse document frequency (idf)
    idf = df.fromkeys(df, 0)
    for key,val in idf.items():
        idf[key] = math.log10(count_doc/df[key])
    print(ast.literal_eval(json.dumps(idf)))
    print('---------------^idf------------------')

    # bobot tf-idf term (w)
    w = tf
    for ky, vl in tf.items():
        for kkey, vval in vl.items():
            w[ky][kkey] = vval*idf[kkey]
    print(ast.literal_eval(json.dumps(w)))
    print('---------------^w------------------')

    return redirect(request.META.get('HTTP_REFERER'))

def manual_class(request):
    if request.method == 'POST':
        form_data = request.POST

        kelas_id = '1'
        if form_data['data_baru'] != '':
            kelas = Kelas(
                nama=form_data['data_baru'],
            )
            kelas.save()
            print('simpan baru')
            kelas_id = kelas.pk
        else:
            print('data lama')
            kelas_id = form_data['data_lama']

        index_crawl_news = CrawlNews.objects.get(id=form_data['data_id'])
        index_crawl_news.kelas_id = kelas_id
        index_crawl_news.save()
        return redirect(request.META.get('HTTP_REFERER'))

    kelas = Kelas.objects.all().order_by('nama')

    crawls = CrawlNews.objects.all().order_by('-id')
    paginator = Paginator(crawls, 5)
    page = request.GET.get('page')
    try:
        crawls = paginator.page(page)
    except PageNotAnInteger:
        crawls = paginator.page(1)
    except EmptyPage:
        crawls = paginator.page(paginator.num_pages)
    return render(request, 'beranda/manual.html', {'combo': kelas, 'crawl': crawls})

from django.shortcuts import render, redirect

import json, ast, math, random
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
        if kounter > 0 and kounter <= 10:
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
        if kounter > 2 and kounter <= 4:
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
    # baca_db = CrawlNews.objects.all()
    baca_db = CrawlNews.objects.exclude(sum_all_word__isnull=True).exclude(sum_all_word__exact='') #get db with sum_all_word not null or ''
    count_doc = baca_db.count() #jumlah dokumen
    print('\nJumlah dokumen = ',count_doc)
    print('******************')
    # count_doc = 4
    kluster = 2
    laju_pembelajaran = 0.5

    # document frequency (df)
    df = dict()
    for i, iterasi_df in enumerate(baca_db, start=0):
        if i < count_doc:
            ct = ast.literal_eval(iterasi_df.count_term)
            for k,v in ct.items():
                if k in df:
                    df[k] += v
                else:
                    df[k] = v
    # print(df)
    # print('---------------^df------------------')

    # term frequency (tf)
    tf = dict()
    for i, iter_df in enumerate(baca_db, start=0):
        if i < count_doc:
            tf_i = df.fromkeys(df, 0)
            ct = ast.literal_eval(iter_df.count_term)
            for ke,va in ct.items():
                if ke in df:
                    tf_i[ke] = va
            tf[iter_df.id] = tf_i
    # print(tf)
    # print('----------------^tf-----------------')

    # inverse document frequency (idf)
    idf = df.fromkeys(df, 0)
    for key,val in idf.items():
        idf[key] = math.log10(1+(count_doc/df[key]))
    # print(idf)
    # print('---------------^idf------------------')

    # bobot tf-idf term (w)
    w = tf
    for ky, vl in tf.items():
        for kkey, vval in vl.items():
            w[ky][kkey] = vval*idf[kkey]
    # print(w)
    # print('---------------^w------------------')

    # find min-max and normalisasi
    min_max = dict()
    for key_a, val_a in w.items():
        for key_b, val_b in val_a.items():
            if key_b not in min_max:
                min_max[key_b] = []
            min_max[key_b].append(val_b)

    maksimal = dict()
    minimal = dict()
    for k_minmax, val_minmax in min_max.items():
        maksimal[k_minmax] = max(val_minmax)
        minimal[k_minmax] = min(val_minmax)

    normalisasi = w
    for k_n, v_n in w.items():
        for k_ns, v_ns in v_n.items():
            if maksimal[k_ns]!=minimal[k_ns]:
                normalisasi[k_n][k_ns] = ((w[k_n][k_ns]-minimal[k_ns])/(maksimal[k_ns]-minimal[k_ns]))*((1-0)+0)
            else:
                normalisasi[k_n][k_ns] = 0
    # print(normalisasi)
    # print('---------------^normalisasi min max------------------')

    # inisialisasi bobot klustering som range 0 s/d 1
    w_som = dict()
    ##### Start #####
    for w_i in range(kluster):
        for w_is in range(len(idf)):
            if w_i not in w_som:
                w_som[w_i] = []
            w_som[w_i].append(random.uniform(0,1))

    # w_som = {0: [0.7,0.8,0,0.5,0.2,1,0,0.4,0.6,0.3,0.4,0.6,0,0.2,0.3],1: [0.1,1,0.1,0.4,0.6,0.2,0.7,0.4,0.4,1,0,0,0.7,0,0.7]}
    ##### End #####

    # print(w_som)
    # print('===========')
    
    # print(normalisasi)
    # print('-----------')
    w_d = dict()

    ##### Start #####
    for k_wd, v_wd in normalisasi.items():
        w_d[k_wd] = list(v_wd.values())

    # w_d = {1: [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 2: [1.0, 0.0, 0.5,0.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0],3:[0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,1.0,1.0,1.0,0.0,0.0,0.0],4:[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,1.0,1.0,1.0]}
    ##### End #####
    # print('=======================')
    d_som = dict()
    index_update_new = []
    index_update_old = []
    status_konvergen = 0
    kluster_update = dict()
    
    jml_iterasi = 0
    while status_konvergen == 0:
        jml_iterasi += 1
        del index_update_new[:] #to empty list
        kluster_update = kluster_update.fromkeys(kluster_update, 0)  # resete dict
        
        for k_wd, v_wd in w_d.items(): #4
            w_som_index_update = int()
            for cluster_i in range(kluster): #2
                if k_wd not in d_som:
                    d_som[k_wd] = {'d':{cluster_i:float()},'w':w_som}
                else:
                    d_som[k_wd]['d'].update({cluster_i:float()})
                d_i = float()
                for w_som_i in range(len(w_som[cluster_i])):
                    d_i += (w_som[cluster_i][w_som_i]-w_d[k_wd][w_som_i])**2
                d_som[k_wd]['d'][cluster_i] = d_i
                if cluster_i > 0: #cek d_som terkecil
                    w_som_index_update = cluster_i if (d_i < d_som[k_wd]['d'][cluster_i-1]) else (cluster_i-1)
            for w_s_i in range(len(w_som[cluster_i])): #update bobot w_som yang D terkecil
                w_som[w_som_index_update][w_s_i] = w_som[w_som_index_update][w_s_i]+laju_pembelajaran*(w_d[k_wd][w_s_i]-w_som[w_som_index_update][w_s_i])
            index_update_new.append(w_som_index_update)
            kluster_update[k_wd] = w_som_index_update
            print(k_wd, '=(kluster)=', w_som_index_update)
            # print('w_som index yang diupdate = ',w_som_index_update)
            # print('---------------')
            # print(w_som)
            # print('======================')
        # print(d_som)
        print("\nIterasi ke-",jml_iterasi,' dengan laju pembelajaran ',laju_pembelajaran)
        # print(kluster_update)
        if len(index_update_old) > 0:
            perubahan = 0 #0=tidak ada perubahan, 1=ada perubahan
            for i_index in range(len(index_update_old)):
                if index_update_new[i_index] != index_update_old[i_index]:
                    perubahan = 1
                    print('ada yang tidak sama')
            if perubahan == 0:
                for key_kluster_update, val_kluster_update in kluster_update.items():
                    t = CrawlNews.objects.get(id=key_kluster_update)
                    t.kluster = val_kluster_update
                    t.save()
                status_konvergen = 1
            print("-> Sudah konvergen? ", ("ya" if perubahan==0 else "tidak"))
            print("-> Hasil cluster = ", index_update_new)
            print("----------------------------")
        else:
            index_update_old = index_update_new[:]
            print('-> Inisialisasi')
            print("-> Hasil cluster = ", index_update_new)
            print("----------------------------")
        laju_pembelajaran = laju_pembelajaran * 0.6
    print("=========================")
    print('Jumlah iterasi = ', jml_iterasi)
    print("=========================\n",)
    return redirect(request.META.get('HTTP_REFERER'))

def manual_class(request):
    return redirect(request.META.get('HTTP_REFERER'))
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

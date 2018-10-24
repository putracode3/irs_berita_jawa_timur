from django.shortcuts import render, redirect

import json, ast, math, random
from skripsi.models import CrawlNews, Kelas
from django.http import HttpResponseRedirect
from operator import itemgetter

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
        if kounter > 4 and kounter <= 10:
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

def cluster(request):
    # baca_db = CrawlNews.objects.all()
    baca_db = CrawlNews.objects.exclude(sum_all_word__isnull=True).exclude(sum_all_word__exact='') #get db with sum_all_word not null or ''
    count_doc = baca_db.count() #jumlah dokumen
    print('\nJumlah dokumen = ',count_doc)
    kluster = 3
    lp = 0.5

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
    # tambahan query
    queri = dict()
    queri = {
        "kerek": 1,
        "korban": 1,
        "ambruk": 1,
    }
    if queri:
        count_doc+=1
        for qu_key in queri:
            if qu_key in df:
                df[qu_key] += queri[qu_key]
    print('\nJumlah dokumen + Q = ',count_doc)
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
    # tambahan query
    if queri:
        # count_doc += 1
        tf_q = df.fromkeys(df, 0)
        for q_key in queri:
            if q_key in df:
                tf_q[q_key] += queri[q_key]
        tf[0] = tf_q
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
                normalisasi[k_n][k_ns] = 1.0
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
    ##### End #####

    # print(w_som)
    print('===========')
    
    # print(normalisasi)
    # print('-----------')
    w_d = dict()
    cos_sim = dict()
    ##### Start #####
    for k_wd, v_wd in normalisasi.items():
        w_d[k_wd] = list(v_wd.values())
        # untuk digunakan perhitungan cosinus similarity nanti
        ##### Start #####
        pangkat = float()
        for k_nm in v_wd:
            if k_wd not in cos_sim:
                cos_sim[k_wd] = {'atas': float(), 'akar': pangkat, 'cos_sim':float()}
            if k_wd != 0:
                cos_sim[k_wd]['atas'] += (v_wd[k_nm]*normalisasi[0][k_nm])
            pangkat += (v_wd[k_nm]**2)
        cos_sim[k_wd]['akar'] = math.sqrt(pangkat)
    for cs in cos_sim:
        if cs != 0:
            cos_sim[cs] = cos_sim[cs]['atas']/(cos_sim[0]['akar']*cos_sim[cs]['akar'])
    cos_sim[0] = float()
    ordered = sorted(cos_sim.items(), key=lambda kv: kv[1], reverse=True)    
        ##### End #####
    ##### End #####
    print(ordered)
    # print(w_d) #*********** .:-[ w_d AMAN ]-:. ***********
    print('=======================')
    d_som = dict()
    # untuk pencocokan saja, apakah cluster i sekarang sama dengan sebelumnya
    index_update_new = []
    index_update_old = []
    status_konvergen = 0
    # kluster_update membawa id untuk update pada db field 'kluster'
    ku = dict() 
    
    # print(w_d)
    jml_iterasi = 0
    while status_konvergen == 0:
        jml_iterasi += 1
        del index_update_new[:] #to empty list
        ku = ku.fromkeys(ku, 0)  # resete dict

        # -----------------------------------------------
        for k_wd, v_wd in w_d.items(): #4 bobot dokumen i => mulai dari 1
            print('---------***-------------')
            print('dokumen ke => ',k_wd)
            # wsiu = int() 
            for ci in range(kluster): #3 perulangan sesuai berapa jumlah kluster => mulai dari 0
                if k_wd not in d_som:
                    d_som[k_wd] = {'d':{ci:float()}} #inisialisasi d_i
                else:
                    d_som[k_wd]['d'].update({ci: float()}) #inisialisasi d_i

                d_i = float()
                for w_som_i in range(len(w_som[ci])):
                    d_i += (w_som[ci][w_som_i]-w_d[k_wd][w_som_i])**2
                d_som[k_wd]['d'][ci] = d_i

                print('>>', ci, ' ', d_som[k_wd]['d'][ci])
            #w_som_index_update untuk menampung index w_som mana yang akan diperbarui
            wsiu = min(d_som[k_wd]['d'], key=lambda k: d_som[k_wd]['d'][k])
            # print('cek data: ', d_som[k_wd]['d'], '\n>> index data minimal = ', min(d_som[k_wd]['d'], key=lambda k: d_som[k_wd]['d'][k]))
            for wsi in range(len(w_som[ci])): #update bobot w_som yang D terkecil
                w_som[wsiu][wsi] = w_som[wsiu][wsi]+lp*(w_d[k_wd][wsi]-w_som[wsiu][wsi])
            index_update_new.append(wsiu)
            ku[k_wd] = wsiu
            print('index w yang diupdate => index = ', wsiu)
        print('>> ku =',ku)
        # -----------------------------------------------

        print("\nIterasi ke-",jml_iterasi,' dengan laju pembelajaran ',lp)
        if len(index_update_old) > 0:
            perubahan = 0 #0=tidak ada perubahan, 1=ada perubahan
            for i_index in range(len(index_update_old)):
                if index_update_new[i_index] != index_update_old[i_index]:
                    perubahan = 1
                    print('ada yang tidak sama')
            if perubahan == 0:
                # for key_ku, val_ku in ku.items():
                    # if key_ku != 0:
                    #     t = CrawlNews.objects.get(id=key_ku)
                    #     t.kluster = val_ku
                    #     t.save()
                status_konvergen = 1
            print("-> Sudah konvergen? ", ("ya" if perubahan==0 else "tidak"))
            print("----------------------------\n \n")
        else:
            index_update_old = index_update_new[:]
            print('-> Inisialisasi')
            print("----------------------------")
        lp = lp * 0.6
    
    keluaran = list()
    for ind,ranking in ordered:
        if ind != 0 and ku[0] == ku[ind]:
            keluaran.append(ind)
            # print("ku ",ku[0])
            # print(ind)
    print(keluaran)
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

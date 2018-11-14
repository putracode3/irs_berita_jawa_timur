from django.shortcuts import render, redirect

import json, ast, math, random
from skripsi.models import CrawlNews, Kelas
from django.http import HttpResponseRedirect
from operator import itemgetter
from django.core.exceptions import ObjectDoesNotExist

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# for crawling
import requests, re
from bs4 import BeautifulSoup


# crawling
def crawl_detik(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    
    news_links = soup.find("ul", {'class': 'list_feed'}).find_all("div",{'class':'desc_nhl'})
    for berita  in news_links:
        #judul berta
        judul_berita = berita.find('h2').text
        #tanggal berita
        tanggal_sumber = berita.find('span', {'class': 'labdate f11'}).text
        tanggal_berita = tanggal_sumber.split(" | ")[1]
        #main headline berita
        for hilangi in berita.find_all('span'):
            hilangi.decompose() #menghilangkan tag
        berita.find('h2').decompose() #menghilangkan tag 
        main_headline_berita = berita.get_text(strip=True) #strip untuk menghilangkan whitespace
        #url berita
        url_berita = berita.find('a').get('href')
        #konten berita
        req_konten = requests.get(url_berita)
        soup_konten = BeautifulSoup(req_konten.text, "lxml")
        for delete_linksisip in soup_konten.find_all("table"):
            delete_linksisip.decompose()
        for delete_googletag in soup_konten.find_all("center"):
            delete_googletag.decompose()
        for delete_tagstrong in soup_konten.find_all("strong"):
            delete_tagstrong.decompose()
        for delete_tagp in soup_konten.find_all("p"):
            delete_tagp.decompose()
        konten_berita = " ".join(soup_konten.find('div', {'class': 'detail_text'}).get_text(" ",strip=True).split())
        try:
            check_url = CrawlNews.objects.get(url=url_berita)
            break
        except ObjectDoesNotExist:
            simpan_detik = CrawlNews(
                headline = judul_berita,
                date = tanggal_berita,
                main_headline = main_headline_berita,
                content = konten_berita,
                url = url_berita
            )
            simpan_detik.save()
            print("Berita news.detik.com/jatim = ",url_berita)


def crawl_sindo(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    news_links = soup.find_all("div", {'class': 'indeks-rows'})
    for berita in news_links:
        judul_berita = berita.find('div', {'class': 'indeks-title'}).find('a').text
        tanggal_berita = berita.find('div', {'class': 'mini-info'}).find('p').text
        main_headline_berita = berita.find('div', {'class': 'indeks-caption'}).find('span').text
        url_berita = berita.find('div', {'class': 'indeks-title'}).find('a').get('href')
        
        req_sub = requests.get(url_berita)
        soup_sub = BeautifulSoup(req_sub.text, "lxml")
        konten_berita = " ".join(soup_sub.find('section', {'class': 'article col-md-11'}).find('p').get_text(" ", strip=True).split())

        try:
            check_url = CrawlNews.objects.get(url=url_berita)
            break
        except ObjectDoesNotExist:
            simpan_sindo = CrawlNews(
                headline=judul_berita,
                date=tanggal_berita,
                main_headline=main_headline_berita,
                content=konten_berita,
                url=url_berita
            )
            simpan_sindo.save()
            print("Berita jatim.sindonews.com/index = ", url_berita)

    #pagination
    try:
        last_pagination = int(soup.find('div', {'class': 'pagination'}).find_all('li')[-1].find('a')['data-ci-pagination-page'])
        for lp in range(1,(last_pagination+1)):
            if lp < (last_pagination):
                url_pagination = soup.find('div', {'class': 'pagination'}).find(attrs={'data-ci-pagination-page':str(lp+1)}).get('href')
                # print('>> ', url_pagination, ' <<')
                req_pagination = requests.get(url_pagination)
                soup_pagination = BeautifulSoup(req_pagination.text, "lxml")
                news_links_pagination = soup_pagination.find_all("div", {'class': 'indeks-rows'})
                for berita_pagination in news_links_pagination:
                    judul_berita_pagination = berita_pagination.find('div', {'class': 'indeks-title'}).find('a').text
                    tanggal_berita_pagination = berita_pagination.find('div', {'class': 'mini-info'}).find('p').text
                    main_headline_berita_pagination = berita_pagination.find('div', {'class': 'indeks-caption'}).find('span').text
                    url_berita_pagination = berita_pagination.find('div', {'class': 'indeks-title'}).find('a').get('href')

                    req_sub = requests.get(url_berita_pagination)
                    soup_sub = BeautifulSoup(req_sub.text, "lxml")
                    konten_berita_pagination = " ".join(soup_sub.find('section', {'class': 'article col-md-11'}).find('p').get_text(" ", strip=True).split())
                    
                    try:
                        check_url = CrawlNews.objects.get(url=url_berita_pagination)
                        break
                    except ObjectDoesNotExist:
                        simpan_sindo = CrawlNews(
                            headline=judul_berita_pagination,
                            date=tanggal_berita_pagination,
                            main_headline=main_headline_berita_pagination,
                            content=konten_berita_pagination,
                            url=url_berita_pagination
                        )
                        simpan_sindo.save()
                        print("Berita jatim.sindonews.com/index = ", url_berita_pagination)
    except AttributeError:
        print("- Tidak ada pagination -")

def crawl_okezone(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    judul_1 = soup.find("div", {'class': 'mh-title-wrap'}).find("a").text
    url_1 = soup.find("div", {'class': 'mh-title-wrap'}).find("a").get('href')
    req_1 = requests.get(url_1)
    soup_1 = BeautifulSoup(req_1.text, "lxml")
    tanggal_1 = soup_1.find("div", {'class': 'namerep'}).find("b").text
    sub_1 = soup_1.find("div", {'id': 'contentx'})
    for del_link_eks in sub_1.find_all(attrs={'style': 'padding-left: 30px;'}):
            del_link_eks.decompose()
    konten_1 = ""
    main_headline_1 = ""
    for ix, s_1 in enumerate(sub_1.find_all("p")):
        if ix == 0:
            main_headline_1 = s_1.get_text(" ",strip=True)
        konten_1 += s_1.get_text(" ",strip=True)
        konten_1 += " "

    try:
        check_url = CrawlNews.objects.get(url=url_1)
    except ObjectDoesNotExist:
        simpan_okezone = CrawlNews(
            headline=judul_1,
            date=tanggal_1,
            main_headline=main_headline_1,
            content=konten_1,
            url=url_1
        )
        simpan_okezone.save()
        print("Berita news.okezone.com/jatim = ",url_1)

    # list 1
    for list_1 in soup.find("div", {'class': 'hl-list-berita'}).find_all("a"):
        judul_2 = list_1.text
        url_2 = list_1.get('href')
        req_2 = requests.get(url_2)
        soup_2 = BeautifulSoup(req_2.text, "lxml")
        tanggal_2 = soup_2.find("div", {'class': 'namerep'}).find("b").text
        sub_2 = soup_2.find("div", {'id': 'contentx'})
        for del_link_eks in sub_2.find_all(attrs={'style': 'padding-left: 30px;'}):
            del_link_eks.decompose()
        konten_2 = ""
        main_headline_2 = ""
        for ix_2, s_2 in enumerate(sub_2.find_all("p")):
            if ix_2 == 0:
                main_headline_2 = s_2.get_text(" ", strip=True)
            konten_2 += s_2.get_text(" ", strip=True)
            konten_2 += " "
        try:
            check_url = CrawlNews.objects.get(url=url_2)
            break
        except ObjectDoesNotExist:
            simpan_okezone = CrawlNews(
                headline=judul_2,
                date=tanggal_2,
                main_headline=main_headline_2,
                content=konten_2,
                url=url_2
            )
            simpan_okezone.save()
            print("Berita news.okezone.com/jatim = ", url_2)
    
    # list 2
    list_3 = soup.find("div", {'class': 'list-contentx'})
    for l3 in list_3.find_all("h2"):
        judul_3 = l3.get_text(" ",strip=True)
        url_3 = l3.find("a").get("href")
        req_3 = requests.get(url_3)
        soup_3 = BeautifulSoup(req_3.text, "lxml")
        tanggal_3 = soup_3.find("div", {'class': 'namerep'}).find("b").text
        sub_3 = soup_3.find("div", {'id': 'contentx'})
        for del_link_eks in sub_3.find_all(attrs={'style': 'padding-left: 30px;'}):
            del_link_eks.decompose()
        konten_3 = ""
        main_headline_3 = ""
        for ix_3, s_3 in enumerate(sub_3.find_all("p")):
            if ix_3 == 0:
                main_headline_3 = s_3.get_text(" ", strip=True)
            konten_3 += s_3.get_text(" ", strip=True)
            konten_3 += " "
        try:
            check_url = CrawlNews.objects.get(url=url_3)
            break
        except ObjectDoesNotExist:
            simpan_okezone = CrawlNews(
                headline=judul_3,
                date=tanggal_3,
                main_headline=main_headline_3,
                content=konten_3,
                url=url_3
            )
            simpan_okezone.save()
            print("Berita news.okezone.com/jatim = ", url_3)

def crawl_jawapos(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    news = soup.find("div", {'class': 'row news-thumbnail flex-wrap'}).find_all("div", {'class': 'wrapper-img-caption'})
    for new in news:
        new.find('a').decompose()
        judul_berita = new.find('a').get_text(strip=True)
        url_berita = new.find('a').get('href')
        main_headline_berita = new.find('p').get_text(strip=True)
        req_sub = requests.get(url_berita)
        soup_sub = BeautifulSoup(req_sub.text, "lxml")
        tanggal_berita = soup_sub.find('div', {'class': 'meta-article c-gray txt-12'}).find('span').text
        konten_sub = soup_sub.find('article', {'class': 'col-11 article'}).find_all('p')
        konten_berita = ""
        for ks in konten_sub:
            konten_berita += ks.get_text(" ",strip=True)
        
        try:
            check_url = CrawlNews.objects.get(url=url_berita)
            break
        except ObjectDoesNotExist:
            simpan_jawapos = CrawlNews(
                headline=judul_berita,
                date=tanggal_berita,
                main_headline=main_headline_berita,
                content=konten_berita,
                url=url_berita
            )
            simpan_jawapos.save()
            print("Berita jawapos.com/location/jawa-timur = ",url_berita)

def simpan(request):
    url_detik = 'https://news.detik.com/jawatimur'
    crawl_detik(url_detik)

    url_sindo = 'https://jatim.sindonews.com/index'
    crawl_sindo(url_sindo)

    url_okezone = 'https://news.okezone.com/jatim'
    crawl_okezone(url_okezone)

    url_jawapos = 'https://www.jawapos.com/location/jawa-timur'
    crawl_jawapos(url_jawapos)

    return render(request, 'beranda/index.html')
    # return redirect(request.META.get('HTTP_REFERER'))
# -------------------------------------------

def simpan_old(request):
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
        if kounter > 25 and kounter <= 26:
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
        if kounter > 25 and kounter <= 26:
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

def preproses_kueri(param):
    # create stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    # stemming process
    sentence = param
    output_stemming = stemmer.stem(sentence)
    # stopword removal
    fa = StopWordRemoverFactory()
    stopword = fa.create_stop_word_remover()
    output_stopword = stopword.remove(output_stemming)
    output_stopword = output_stopword.replace(' - ', ' ')
    # hitung term
    counts = dict()
    str_db = output_stopword
    words = str_db.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    output_count_term = ast.literal_eval(json.dumps(counts))
    return output_count_term

def cluster(request):
    # baca_db = CrawlNews.objects.all()
    if request.method != 'POST':
        return render(request, 'beranda/index.html')
    
    form_data = request.POST
    if form_data['kueri'] == '':
        return render(request, 'beranda/index.html')
    masukan = form_data['kueri']
    queri = dict()
    queri = preproses_kueri(masukan)
    if not queri:
        return render(request, 'beranda/index.html',{'not_found':'"Kata kunci kurang pas"','masukan':masukan})
    # ==========================end input user query=======================================

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
    # print('----------------------------===============----------------------------')
    # tambahan query
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
    new_min = 1
    new_max = 9
    for k_n, v_n in w.items():
        for k_ns, v_ns in v_n.items():
            if maksimal[k_ns]!=minimal[k_ns]:
                normalisasi[k_n][k_ns] = ((w[k_n][k_ns]-minimal[k_ns])/(maksimal[k_ns]-minimal[k_ns]))*((new_max-new_min)+new_min)
            else:
                normalisasi[k_n][k_ns] = new_max
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
    # print('===========')
    
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
    # while status_konvergen == 0:
    for ok in range(10):
        jml_iterasi += 1
        del index_update_new[:] #to empty list
        ku = ku.fromkeys(ku, 0)  # resete dict

        # -----------------------------------------------
        for k_wd, v_wd in w_d.items(): #4 bobot dokumen i => mulai dari 1
            # print('---------***-------------') #output penting
            # print('dokumen ke => ',k_wd) #output penting
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

                # print('>>', ci, ' ', d_som[k_wd]['d'][ci]) #output penting
            #w_som_index_update untuk menampung index w_som mana yang akan diperbarui
            wsiu = min(d_som[k_wd]['d'], key=lambda k: d_som[k_wd]['d'][k])
            # print('cek data: ', d_som[k_wd]['d'], '\n>> index data minimal = ', min(d_som[k_wd]['d'], key=lambda k: d_som[k_wd]['d'][k]))
            for wsi in range(len(w_som[ci])): #update bobot w_som yang D terkecil
                w_som[wsiu][wsi] = w_som[wsiu][wsi]+lp*(w_d[k_wd][wsi]-w_som[wsiu][wsi])
            index_update_new.append(wsiu)
            ku[k_wd] = wsiu
            # print('index w yang diupdate => index = ', wsiu) #output penting
        print('>> kluster =',ku)
        # -----------------------------------------------

        print("\nIterasi ke-",jml_iterasi,' dengan laju pembelajaran ',lp)
        if len(index_update_old) > 0:
            perubahan = 0 #0=tidak ada perubahan, 1=ada perubahan
            for i_index in range(len(index_update_old)):
                if index_update_new[i_index] != index_update_old[i_index]:
                    perubahan = 1
                    print('ada yang tidak sama')
            if perubahan == 0:
                # for key_kluster_update, val_kluster_update in ku.items():
                #     if key_kluster_update!=0:
                #         t = CrawlNews.objects.get(id=key_kluster_update)
                #         t.kluster = val_kluster_update
                #         t.save()
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
        if ind != 0 and ku[0] == ku[ind] and ranking != 0.0:
            keluaran.append(ind)
    print('id dokumen = ',keluaran)
    print("=========================")
    print('Jumlah iterasi = ', jml_iterasi)
    print("=========================")
    print('Hasil preprocessing query user =\n', queri)
    print("=========================")
    print("ordered =\n", ordered)
    print("=========================")
    # return redirect(request.META.get('HTTP_REFERER'))
    hasil = list(CrawlNews.objects.filter(pk__in=keluaran))
    hasil.sort(key=lambda t: keluaran.index(t.pk))
    return render(request, 'beranda/index.html', {'hasil': hasil,'masukan':masukan})

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

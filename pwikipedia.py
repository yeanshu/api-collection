import requests
import json
from ratelimit import limits, sleep_and_retry
import datetime
from dateutil.relativedelta import relativedelta

# START = '2022010100/'
# END = '2022020100'
# YDAY = datetime.datetime.today()-datetime.timedelta(days=1)
# NSTART = (YDAY-datetime.timedelta(days=31)).strftime('%Y%m%d') + '/'
# NEND = YDAY.strftime('%Y%m%d')
# END = datetime.datetime.today().replace(day=1)
# START = (END - relativedelta(months=1)).strftime('%Y%m%d') + '/'
# END = END.strftime('%Y%m%d')

TODAY = datetime.datetime.today().date()


headers = {
    'User-Agent': "PageInfoBot, contact = https://github.com/yeanshu/api-collection",
    'Accept-Encoding': 'gzip'
}

#@sleep_and_retry
#@limits(calls=200,period=1)
def check_limit():
    return

def getcategorymembers(site, cat, depth=0):

    article_list = {}
    for c in cat:
    
        category_depth = {}
        category_depth[c] = 0
    
        while len(category_depth) > 0:
            cur_cat = list(category_depth.keys())[0]
            cur_depth = category_depth[cur_cat]
            qry = site + "api.php?action=query&list=categorymembers&cmtitle=Category:" + cur_cat + "&format=json&cmlimit=max"
            #print(qry)
            check_limit()
            response = requests.get(qry, headers=headers)
            response = response.json()
            while True:
                for art in response['query']['categorymembers']:
                    if art['ns'] == 0:
                        article_list[art['title']] = 0
                    if art['ns'] == 14 and cur_depth < depth:
                        if art['title'][9:] not in category_depth:
                            category_depth[art['title'][9:]] = cur_depth+1
                if 'continue' not in response:
                    break
                cm = response['continue']['cmcontinue']
                check_limit()
                response = requests.get(site + "api.php?action=query&list=categorymembers&cmtitle=Category:" + cur_cat + "&cmcontinue="+ cm +"&format=json&cmlimit=max", headers=headers)
                response = response.json()
    
            category_depth.pop(cur_cat)

    return article_list

def getpagelinks(site, page, subsection):

    article_list = {}
    for p in page:

        qry = site + "api.php?action=parse&prop=links&page=" + p + "&format=json&formatversion=2&redirects"

        if subsection is not None:
            qry += "&section=" + subsection

        #print(qry)
        #check_limit()
        response = requests.get(qry, headers=headers)
        response = response.json()
        for art in response['parse']['links']:
            article_list[art['title']] = 0

    return article_list

def getpageviews2(site,articles):

    arts = list(articles.keys())
    cur_arts = []
    for art in arts:
        cur_arts.append(art)
        if len(cur_arts) == 50:
            qrs = '|'.join(cur_arts)
            cur_arts = []

            qry = site + "api.php?action=query&titles=" + qrs + "&prop=pageviews&format=json"
            #print(qry)
            check_limit()
            response = requests.get(qry, headers=headers)
            response = response.json()

            #print(response)
            for v in response['query']['pages'].values():
                if v['ns'] == 0 and 'pageviews' in v:
                    vs = list(v['pageviews'].values())[:-1]
                    vs = [n for n in vs if isinstance(n,int)]
                    try:
                        articles[v['title']] = int(sum(vs)/len(vs)*30)
                    except:
                        pass

        elif art == arts[-1]:
            qrs = '|'.join(cur_arts)

            qry = site + "api.php?action=query&titles=" + qrs + "&prop=pageviews&format=json"
            #print(qry)
            check_limit()
            response = requests.get(qry, headers=headers)
            response = response.json()

            for v in response['query']['pages'].values():
                if v['ns'] == 0 and 'pageviews' in v:
                    vs = list(v['pageviews'].values())[:-1]
                    vs = [n for n in vs if isinstance(n,int)]
                    try:
                        articles[v['title']] = int(sum(vs)/len(vs)*30)
                    except:
                        pass

    articles = dict(sorted(articles.items(), key=lambda item: item[1], reverse=True))
    return articles



def getpageviews3(site, cat, depth=0):

    article_list = {}

    for c in cat:
    
        category_depth = {}
        category_depth[c] = 0
    
        while len(category_depth) > 0:
            cur_cat = list(category_depth.keys())[0]
            cur_depth = category_depth[cur_cat]

            gcmcontinue = ''
            pvipcontinue = ''

            while True:
                qry = site + "api.php?action=query&generator=categorymembers&gcmtitle=Category:" + cur_cat + "&format=json&gcmlimit=max&prop=pageviews&" + gcmcontinue + '&' + pvipcontinue
                #print(qry)
                #check_limit()
                response = requests.get(qry,headers=headers)
                response = response.json()

                for art in response['query']['pages'].values():
                    if art['ns'] == 0 and 'pageviews' in art:
                        vs = list(art['pageviews'].values())[:-1]
                        vs = [n for n in vs if isinstance(n,int)]
                        try:
                            article_list[art['title']] = int(sum(vs)/len(vs)*30)
                        except:
                            pass
                    if art['ns'] == 14 and cur_depth < depth:
                        if art['title'][9:] not in category_depth:
                            category_depth[art['title'][9:]] = cur_depth+1
                #print('blah')
                if 'continue' in response:
                    if 'pvipcontinue' in response['continue']:
                        pvipcontinue = 'pvipcontinue='+response['continue']['pvipcontinue']
                        continue
                    if 'gcmcontinue' in response['continue']:
                        gcmcontinue = 'gcmcontinue='+response['continue']['gcmcontinue']
                        continue

                break

            category_depth.pop(cur_cat)

    article_list = dict(sorted(article_list.items(), key=lambda item: item[1], reverse=True))
    return article_list

def getpagesize(site, articles):

    for article in articles:
        carticle = requests.utils.quote(article)
        qry = site + "api.php?action=query&titles=" + carticle + "&prop=info&format=json&formatversion=2"
        #print(qry)
        #check_limit()
        size = requests.get(qry, headers=headers)
        try:
            size = size.json()['query']['pages'][0]
            if 'missing' not in size:
                size = size['length']
                articles[article] = size
        except Exception:
            pass

    articles = dict(sorted(articles.items(), key=lambda item: item[1], reverse=True))
    print(articles)

def categoryviews(site, query, depth=0, intersect=None, difference=None):
    #articles = getpageviews3(site,query,depth=depth)
    # if intersect:
    #     b = getcategorymembers(site,intersect,depth=1)
    #     remaining = articles.keys() & b.keys()
    #     articles = {x:y for (x,y) in articles.items() if x in remaining}

    #Version 0
    # articles = getcategorymembers(site,query,depth=depth)

    # for a in articles:
    #     qry = site + "api.php?action=query&titles=" + a + "&prop=pageviews&format=json"
    #         #print(qry)
    #     check_limit()
    #     response = requests.get(qry, headers=headers)
    #     response = response.json()

    #     #print(response)
    #     for v in response['query']['pages'].values():
    #         if v['ns'] == 0 and 'pageviews' in v:
    #             vs = list(v['pageviews'].values())[:-1]
    #             vs = [n for n in vs if isinstance(n,int)]
    #             try:
    #                 articles[v['title']] = int(sum(vs)/len(vs)*30)
    #             except:
    #                 pass


    #Version 1
    #articles = getcategorymembers(site,query,depth=depth)
    #articles = getpageviews2(site, articles)

    #Version 2
    articles = getpageviews3(site,query,depth=depth)

    # if difference:
    #     b = getcategorymembers(site,difference)
    #     remaining = articles.keys() - b.keys()
    #     articles = {x:y for (x,y) in articles.items() if x in remaining}

    print(articles)

WIKIPEDIA = 'https://en.wikipedia.org/w/'
CNWIKIPEDIA = 'https://zh.wikipedia.org/w/'
JPWIKIPEDIA = 'https://ja.wikipedia.org/w/'
WIKTIONARY = 'https://en.wiktionary.org/w/'

query = ['2021年日本電影作品']
subsection= None #String
#subsection finder https://en.wikipedia.org/w/api.php?action=parse&prop=sections&page=query&format=json&formatversion=2&redirects
site = CNWIKIPEDIA
depth = 0#float('inf')
#Root is depth 0/ No subcategories
intersect = ['2020s_video_games']
difference = ['Website_stubs']

#getinfo(site, query, depth=depth, category=True, views=True, size=False)
categoryviews(site,query,depth=depth)

# article_list = {}

# qry = site + "api.php?action=query&list=random&rnlimit=500&rnnamespace=0&format=json&formatversion=2&rnfilterredir=nonredirects"
# response = requests.get(qry, headers=headers)
# response = response.json()
# for art in response['query']['random']:
#     article_list[art['title']] = 0

# getpageviews(article_list)
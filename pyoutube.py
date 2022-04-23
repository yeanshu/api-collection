import googleapiclient.discovery

with open('./keys/youtube.txt', 'r') as f:
    DEVELOPER_KEY = f.read()

VID = "QpSHcxdEPtw"
PID = "PL500B0E6974367F5E"

def playlist_query(sorted=True):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=DEVELOPER_KEY)

    ptoken = None
    views = {}
    while True:
        vids = []
        if ptoken:
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=PID,
                maxResults=50,
                pageToken=ptoken
            )
        else:
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=PID,
                maxResults=50
            )
        response = request.execute()
        for i in response['items']:
            vids.append(i['snippet']['resourceId']['videoId'])
        
        vid_string = ','.join(vids)

        request = youtube.videos().list(
            part="snippet,statistics",
            id=vid_string
        )
        vresponse = request.execute()
        for i in vresponse['items']:
            title = i['snippet']['title']
            #views[title] = int(i['statistics']['viewCount'])
            #views[title] = comment_count(i['id'])
            #views[title] = round(comment_count(i['id'])/int(i['statistics']['viewCount'])*100,2)
            views[title] = [int(i['statistics']['viewCount']),comment_count(i['id'])]

        if "nextPageToken" in response:
            ptoken = response['nextPageToken']
        else:
            break
    
    if sorted:
        views = dict(sorted(views.items(), key=lambda item: item[1], reverse=True))
    return views

def comment_count(vid):
    count = 0
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=DEVELOPER_KEY)
    ptoken = None
    while True:
        if ptoken:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=vid,
                maxResults=100,
                pageToken = ptoken
            )
        else:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=vid,
                maxResults=100
            )
        cresponse = request.execute()
        for c in cresponse['items']:
            count += 1
            count += c['snippet']['totalReplyCount']

        if "nextPageToken" in cresponse:
            ptoken = cresponse['nextPageToken']
        else:
            break

    return count

def dictcsv(dict):
    for i in dict.items():
        print(i[0],'~',i[1][0],'~', i[1][1])

dat = playlist_query(sorted=False)
dictcsv(dat)
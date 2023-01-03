from ytmusicapi import YTMusic
import pandas as pd
import datetime
import os
import time
from pytube import YouTube

ytmusic = YTMusic()


#define artiste data collection funtion
def get_artiste_details(ytmusic,c_id,img_path):
    #get timestamp
    cur_time = datetime.datetime.now()
    time_stamp = str(cur_time.day) + "-" + str(cur_time.month) + "-" + str(cur_time.year) + " " + str(cur_time.hour) + ":" + str(cur_time.minute)
    
    artiste = YTMusic.get_artist(ytmusic,channelId=c_id)
    artiste_info = dict(artiste_channel = c_id,
                        artiste_name = artiste.get('name'),
                        no_of_subscribers = artiste.get('subscribers'),
                        bio = artiste.get('description'),
                        update_time = time_stamp)

    #get artiste image
    image_url = artiste['thumbnails'][-1]['url']
    artiste_img = img_path + "/" + artiste['name'] + '_' + c_id + '_img.jpg'

    artiste_image = requests.get(image_url).content
    with open(artiste_img, 'wb') as handler:
        handler.write(artiste_image)

    return artiste_info

#define function to pull collections (album,EP,singles)
def get_artiste_collections(ytmusic,c_id,img_path):
    #get timestamp
    cur_time = datetime.datetime.now()
    time_stamp = str(cur_time.day) + "-" + str(cur_time.month) + "-" + str(cur_time.year) + " " + str(cur_time.hour) + ":" + str(cur_time.minute)
    
    artiste_info = YTMusic.get_artist(ytmusic,c_id)
    collections = []
    collection_IDs = []
    
    #check how many albums/EPs the artiste has if any
    if artiste_info.get('albums') != None:
        no_of_collections = len(artiste_info.get('albums').get('results'))
    else:
        no_of_collections = 0

    #collect info for each album/EP
    for i in range(no_of_collections):
        collection_info = dict(channel_artiste_id = c_id,
                               collection_owners = '',
                               collection_id = artiste_info.get('albums')['results'][i]['browseId'],
                               collection_title = artiste_info.get('albums')['results'][i]['title'],
                               release_year = artiste_info.get('albums')['results'][i]['year'])

        other_info = YTMusic.get_album(ytmusic,collection_info['collection_id'])
        collection_type = other_info.get('type')

        collection_info['collection_type'] = collection_type
        collection_info['update_time'] = time_stamp

        #collate owning artiste names
        owner_artiste_names = []
        owners = other_info['artists']
        for i in range(len(owners)):
            owner_name = owners[i]['name']
            owner_artiste_names.append(owner_name)

        #join artiste names dynamically
        if len(owner_artiste_names)>1:
            owner_artiste_names = ', '.join(owner_artiste_names[0:-1]) + ' & ' + owner_artiste_names[-1]
        else:
            owner_artiste_names = ','.join(owner_artiste_names)
        collection_info['collection_owners'] = owner_artiste_names

        collections.append(collection_info)
        collection_IDs.append(collection_info['collection_id'])
    
    #check if artiste has singles playlist, then collect the info
    if artiste_info.get('singles').get('params'):
        param = artiste_info['singles']['params']
        singles = YTMusic.get_artist_albums(ytmusic,c_id,param)
        for s in range(len(singles)):
            singles_info = dict(channel_artiste_id = c_id,
                                collection_owners = '',
                                collection_id = singles[s].get('browseId'),
                                collection_title = singles[s].get('title'),
                                release_year = singles[s].get('year'))
            singles_info['collection_type'] = 'Single'
            singles_info['update_time'] = time_stamp

            other_info = YTMusic.get_album(ytmusic,singles_info['collection_id'])

            owner_artiste_names = []
            owners = other_info['artists']
            for i in range(len(owners)):
                owner_name = owners[i]['name']
                owner_artiste_names.append(owner_name)

            if len(owner_artiste_names)>1:
                owner_artiste_names = ', '.join(owner_artiste_names[0:-1]) + ' & ' + owner_artiste_names[-1]
            else:
                owner_artiste_names = ','.join(owner_artiste_names)
            singles_info['collection_owners'] = owner_artiste_names

            collections.append(singles_info)
            collection_IDs.append(singles_info['collection_id'])

    
    #check if artiste has singles but no playlist, then collect the info
    elif artiste_info.get('singles').get('results'):
        singles = artiste_info['singles']['results']
        for l in range(len(singles)):
            singles_info = dict(channel_artiste_id = c_id,
                                collection_owners = '',
                                collection_id = singles[l].get('browseId'),
                                collection_title = singles[l].get('title'),
                                release_year = singles[l].get('year'))
            singles_info['collection_type'] = 'Single'
            singles_info['update_time'] = time_stamp

            other_info = YTMusic.get_album(ytmusic,singles_info['collection_id'])

            owner_artiste_names = []
            owners = other_info['artists']
            for i in range(len(owners)):
                owner_name = owners[i]['name']
                owner_artiste_names.append(owner_name)

            if len(owner_artiste_names)>1:
                owner_artiste_names = ', '.join(owner_artiste_names[0:-1]) + ' & ' + owner_artiste_names[-1]
            else:
                owner_artiste_names = ','.join(owner_artiste_names)
            singles_info['collection_owners'] = owner_artiste_names

            collections.append(singles_info)
            collection_IDs.append(singles_info['collection_id'])
            
    
    #check if artiste has videos playlist, then create videos pseudo collection
    if artiste_info.get('videos').get('browseId') or len(artiste_info.get('videos').get('results'))>=1:
        video_collection = dict(channel_artiste_id = c_id,
                                collection_owners = artiste_info['name'],
                                collection_id = c_id + '_Videos',
                                collection_title = artiste_info['name'] + '_Videos',
                                release_year = '',
                                collection_type = 'Videos',
                                update_time = time_stamp)


        collections.append(video_collection)
    
    Collections_and_IDs = [collections,collection_IDs]
    
    return Collections_and_IDs


#define function to collect songs data
def get_songs_info(ytmusic,col_id,c_id,songs_list):    
    
    #get timestamp
    cur_time = datetime.datetime.now()
    time_stamp = str(cur_time.day) + "-" + str(cur_time.month) + "-" + str(cur_time.year) + " " + str(cur_time.hour) + ":" + str(cur_time.minute)
    
    songs = []
    songs_update = []
    error_vids = []
    audio_not_dl = []
    collection = YTMusic.get_album(ytmusic,col_id)
    
    #determine number of songs in collection
    no_of_songs = len(collection['tracks'])
    
    #loop through each song in collection and collect song info
    for i in range(no_of_songs):
        vid_id = collection['tracks'][i]['videoId']
        try:
            song_details = YTMusic.get_song(ytmusic,vid_id)
            #check if song info is already collected, then collect only views count
            if 'id_' + vid_id in songs_list:
                song_view_update = dict(song_id ='id_' + vid_id,
                                        views = song_details.get('microformat').get('microformatDataRenderer').get('viewCount'),
                                       update_time = time_stamp)
                songs_update.append(song_view_update)
            else:    
                if song_details['playabilityStatus']['status'] == 'OK':
                    song_info = dict(artiste_id = c_id,
                                     song_owners = '',
                                     collection_id = col_id,
                                     song_id = 'id_'+ vid_id,
                                     song_title = collection['tracks'][i]['title'],
                                     track_number = i+1)

                    secs = song_details.get('microformat').get('microformatDataRenderer').get('videoDetails').get('durationSeconds')
                    view_count = song_details.get('microformat').get('microformatDataRenderer').get('viewCount')
                    publish_date = song_details.get('microformat').get('microformatDataRenderer').get('publishDate')
                    main_title = song_details['microformat']['microformatDataRenderer']['linkAlternates'][-1]['title']
                    #vid_cat = song_details.get('microformat').get('microformatDataRenderer').get('category')

                    try:
                        s_tags = ','.join(song_details['microformat']['microformatDataRenderer']['tags'])
                    except:
                        s_tags = ''

                    song_info['caption'] = main_title
                    #song_info['category'] = vid_cat
                    song_info['len_secs'] = secs
                    song_info['views'] = view_count
                    song_info['release_date'] = publish_date
                    song_info['tags_used'] = s_tags
                    song_info['update_time'] = time_stamp

                    #loop and list all contributing artistes
                    artistes = []
                    no_of_artistes = len(collection['artists'])
                    for j in range(no_of_artistes):
                        artiste = collection['artists'][j]['name']
                        artistes.append(artiste)

                    if len(artistes)>1:
                        artistes = ', '.join(artistes[0:-1]) + ' & ' + artistes[-1]
                    else:
                        artistes = ','.join(artistes)

                    song_info['song_owners'] = artistes

                    songs.append(song_info)
       
        except:
            error_vids.append(vid_id)

        finally:
            #attempt download of audio file
            try:
                if int(secs)<600:
                    yt = YouTube('http://youtube.com/watch?v=' + vid_id)
                    destination = 'C:\\Users\\USER\\Documents\\YTMusic Data\\Music Files'

                    if yt.streams:
                        strms = yt.streams.filter(type='audio')
                        audio_stream = strms.order_by('abr')[-1]
                        file_name = audio_stream.default_filename[:-5]
                        new_file = destination + '\\' + file_name + '_' + vid_id + '.webm'
                        if os.path.exists(new_file) is False:
                            out_file = audio_stream.download(output_path=destination)
                            os.rename(out_file, new_file)
            except:
                audio_not_dl.append(vid_id)
    
    songs_result = [songs,songs_update,error_vids,audio_not_dl]
    
    return songs_result


#define function to pull videos
def get_artiste_videos(ytmusic,c_id,songs_list):
    
    #get timestamp
    cur_time = datetime.datetime.now()
    time_stamp = str(cur_time.day) + "-" + str(cur_time.month) + "-" + str(cur_time.year) + " " + str(cur_time.hour) + ":" + str(cur_time.minute)
    time_stamp
    
    artiste_info = YTMusic.get_artist(ytmusic,c_id)
    
    #get video playlist id or video list
    artist_videos = []
    if artiste_info.get('videos').get('browseId'):
        videos_playlist_id = artiste_info['videos']['browseId']
        artist_videos = videos_playlist_id
    elif artiste_info.get('videos').get('results'):
        videos_list = artiste_info['videos']['results']
        artist_videos.extend(videos_list)
    
    #return list of video ids
    if type(artist_videos) is str:
        videos_playlist_id = artist_videos
        videos = YTMusic.get_playlist(ytmusic,videos_playlist_id, limit = 300)['tracks']
    elif type(artist_videos) is list and len(artist_videos)>0:
        videos = artist_videos

    video_id_list = []
    for vid in range(len(videos)):
        video_id_list.append(videos[vid]['videoId'])

    videos_set = []
    videos_update = []
    error_vids = []
    audio_not_dl = []
    for i in range(len(video_id_list)):
        vid_id = video_id_list[i]
        try:
            #attempt data pull for vid
            if vid_id in songs_list:
                video_view_update = dict(song_id ='id_' + vid_id,
                                         views = video_data.get('microformat').get('microformatDataRenderer').get('viewCount'),
                                         update_time = time_stamp)
                videos_update.append(video_view_update)
            else:
                video_data = YTMusic.get_song(ytmusic,vid_id)
                secs = video_data.get('microformat').get('microformatDataRenderer').get('videoDetails').get('durationSeconds')
                view_count = video_data.get('microformat').get('microformatDataRenderer').get('viewCount')
                publish_date = video_data.get('microformat').get('microformatDataRenderer').get('publishDate')
                main_title = video_data['microformat']['microformatDataRenderer']['linkAlternates'][-1]['title']
                #vid_cat = video_data.get('microformat').get('microformatDataRenderer').get('category')

                try:
                    s_tags = ','.join(video_data['microformat']['microformatDataRenderer']['tags'])
                except:
                    s_tags = ''

                video_info = dict(artiste_id = c_id,
                                  song_owners = video_data['videoDetails']['author'],
                                  collection_id = c_id + '_Videos',
                                  song_id = vid_id,
                                  song_title = video_data['videoDetails']['title'])

                video_info['song_id'] = 'id_' + vid_id
                video_info['caption'] = main_title
                video_info['len_secs'] = secs
                video_info['views'] = view_count
                video_info['release_date'] = publish_date
                video_info['tags_used'] = s_tags
                video_info['update_time'] = time_stamp
                
                videos_set.append(video_info)
        except:
            #iferror, return vid id in error list
            error_vids.append(vid_id)

        finally:
            #attempt download of audio file
            try:
                if int(secs)<600:
                    yt = YouTube('http://youtube.com/watch?v=' + vid_id)
                    destination = 'C:\\Users\\USER\\Documents\\YTMusic Data\\Music Files'
                    if yt.streams:    
                        strms = yt.streams.filter(type='audio')
                        audio_stream = strms.order_by('abr')[-1]

                        file_name = audio_stream.default_filename[:-5]
                        new_file = destination + '\\' + file_name + '_' + vid_id + '.webm'
                        if os.path.exists(new_file) is False:
                            out_file = audio_stream.download(output_path=destination)
                            os.rename(out_file, new_file)
            except:
                #iferror return vid id in error download list
                audio_not_dl.append(vid_id)
    
    video_results = [videos_set,videos_update,error_vids,audio_not_dl]
    return video_results


#read csv files for collected data
song_info_file = r'C:\Users\USER\Documents\YTMusic Data\yt_songs_info.csv'
collection_info_file = r'C:\Users\USER\Documents\YTMusic Data\yt_collections_info.csv'
artiste_info_file = r'C:\Users\USER\Documents\YTMusic Data\yt_artistes_info.csv'

#store in pandas table
song_info_data = pd.read_csv(song_info_file)
collection_info_data = pd.read_csv(collection_info_file)
artiste_info_data = pd.read_csv(artiste_info_file)

#song list
songsid = song_info_data['song_id'].tolist()

#collections list ---> colid_unique
chansid = collection_info_data['channel_artiste_id'].tolist()
colsid = collection_info_data['collection_id'].tolist()

colid_unique = []
for i in range(len(colsid)):
    unique_col_id = chansid[i] + "_" + colsid[i]
    colid_unique.append(unique_col_id)

#artiste list
artistesid = artiste_info_data['artiste_channel'].tolist()


files_directory = 'YTMusic Data'
img_directory = 'images'
parent_dir = "C:/Users/USER/Documents/"
path = os.path.join(parent_dir, files_directory)
img_path = os.path.join(parent_dir, files_directory, img_directory)
#os.mkdir(path)
#os.mkdir(img_path)

path = "C:/Users/USER/Documents/YTMusic Data/"

yt_artiste_filename = path + 'yt_artistes_info.csv'
yt_collections_filename = path + 'yt_collections_info.csv'
yt_songs_filename = path + 'yt_songs_info.csv'

channel_id_file = r'C:\Users\USER\Documents\YTMusic Data\artiste_channel_ids.csv'
data = pd.read_csv(channel_id_file)

YT_channel_ids = data['Youtube ID'].tolist()
Artiste_Name = data['Artiste Name'].tolist()

id_pairs = []
for i in range(len(YT_channel_ids)):
    yt = YT_channel_ids[i]
    art_name = Artiste_Name[i]

    id_pair = dict(a_name = art_name, yt_id = yt)
    id_pairs.append(id_pair)

yt_artistes_info_comp = []
yt_artistes_collections_comp = []
yt_artistes_songs_comp = []
durations = []
yt_streams_update = []
error_vid_list = []
audio_not_dl_list = []

count = 0
print(f"Pulling data for {len(YT_channel_ids)} artistes")
for i in range(len(id_pairs)):
    start = time.time()
    try:
        #get artiste info and collections from YTMusic
        print(f"{id_pairs[i]['a_name']} data pull started. {i+1}/{len(YT_channel_ids)}")
        yt_artist_info = get_artiste_details(ytmusic,id_pairs[i]['yt_id'],img_path)
        print(f"  {id_pairs[i]['a_name']} YT bio pull finished.")
        yt_artistes_info_comp.append(yt_artist_info)

        print(f"    {id_pairs[i]['a_name']} YT collections pull started.")
        yt_artiste_collections = get_artiste_collections(ytmusic,id_pairs[i]['yt_id'],img_path)
        print(f"    {id_pairs[i]['a_name']} YT collections pull finished.")
        yt_artistes_collections_comp.extend(yt_artiste_collections[0])

        #get songs from collections on YTMusic
        for j in range(len(yt_artiste_collections[1])):
            print(f"      Songs pull from {yt_artiste_collections[0][j]['collection_title']} collection on YT started. {j+1}/{len(yt_artiste_collections[1])}")
            yt_col = yt_artiste_collections[1][j]
            yt_artiste_songs = get_songs_info(ytmusic,yt_col,id_pairs[i]['yt_id'],songsid)
            print(f"      Songs pull from {yt_artiste_collections[0][j]['collection_title']} collection on YT finished. {j+1}/{len(yt_artiste_collections[1])}")
            yt_artistes_songs_comp.extend(yt_artiste_songs[0])
            yt_streams_update.extend(yt_artiste_songs[1])
            error_vid_list.extend(yt_artiste_songs[2])
            audio_not_dl_list.extend(yt_artiste_songs[3])

        #get videos from channel and add to songs list
        print(f"      Videos data pull for {id_pairs[i]['a_name']} on YT started.")
        yt_videos = get_artiste_videos(ytmusic,id_pairs[i]['yt_id'],songsid)
        print(f"      Videos data pull for {id_pairs[i]['a_name']} on YT finished.")
        yt_artistes_songs_comp.extend(yt_videos[0])
        yt_streams_update.extend(yt_videos[1])
        error_vid_list.extend(yt_videos[2])
        audio_not_dl_list.extend(yt_videos[3])

        print(f"{id_pairs[i]['a_name']} YT artiste data pull finished. {i+1}/{str(len(YT_channel_ids))}")

        end = time.time()
        duration = {'artiste':id_pairs[i]['a_name'],'pull time_seconds':int(end - start)}
        durations.append(duration)
        count = i+1
        
    except:
        print(f"Error during pull for {id_pairs[i]['a_name']}")

print(f"Data pull for {count} of {len(YT_channel_ids)} artistes completed")
if len(error_vid_list)>0:
    print(f"Videos with data query errors:\n{error_vid_list}")

if len(audio_not_dl_list)>0:
    print(f"\nVideos not dowloaded:\n{audio_not_dl_list}")

#load to pandas dataframe
yt_artiste_df = pd.DataFrame(yt_artistes_info_comp)
yt_collections_df = pd.DataFrame(yt_artistes_collections_comp)
yt_songs_df = pd.DataFrame(yt_artistes_songs_comp)
yt_streams_update_df = pd.DataFrame(yt_streams_update)

#collate new data with existing data in pandas dataframe
#add new pulls to existing df
artiste_info_data = pd.concat([yt_artiste_df, artiste_info_data])
collection_info_data = pd.concat([yt_collections_df, collection_info_data])
song_info_data = pd.concat([song_info_data, yt_songs_df])

#remove duplicate records on artiste and collections tables
artiste_info_data = artiste_info_data.drop_duplicates(subset='artiste_channel')
artiste_info_data = artiste_info_data.sort_values(by=['artiste_name'])

collection_info_data = collection_info_data.drop_duplicates(subset=['channel_artiste_id','collection_id'])
collection_info_data = collection_info_data.sort_values(by=['collection_title'])

song_info_data = song_info_data.drop_duplicates(subset=['artiste_id','song_id'])
song_info_data = song_info_data.sort_values(by=['release_date'])

#update songs df with new streaming info
if len(yt_streams_update) > 0:
    for i in range(len(yt_streams_update)):
        song_info_data.loc[song_info_data.song_id == yt_streams_update[i]['song_id'], ['views']] = yt_streams_update[i]['views']
        song_info_data.loc[song_info_data.song_id == yt_streams_update[i]['song_id'], ['update_time']] = yt_streams_update[i]['update_time']

#write to csv
artiste_info_data.to_csv(yt_artiste_filename,index=False)
collection_info_data.to_csv(yt_collections_filename,index=False)
song_info_data.to_csv(yt_songs_filename,index=False)

total_time = 0
for i in range(len(durations)):
    total_time += durations[i]['pull time_seconds']

durations, 'Overall pull time is ' + str(total_time) + ' seconds'


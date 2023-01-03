import pandas as pd
import os
import time
from bs4 import BeautifulSoup

#define function to query musical data from VDJ xml file for songs in song list
def get_xml_music_data(xml_data,vid_id_list):

    vid_ids = list(set(vid_id_list))
    songs_data = []

    for i in range(len(vid_ids)):
        #find song tag
        file_id = vid_ids[i][3:] + '.webm'
        song_data_start = xml_data.find(file_id)

        if song_data_start != -1:
            song_data_end = xml_data[song_data_start:].find('Song>')
            song_data = xml_data[song_data_start:song_data_end+song_data_start]

            #find genre
            genre_tag = song_data.find('Genre=')
            if genre_tag != -1:
                genre_tagend = song_data[genre_tag:].find('" ')
                genre = song_data[genre_tag+7:genre_tagend+genre_tag]
            else:
                genre = 'Others'

            #find bpm
            bpm_tag = song_data.find('Bpm=')
            if bpm_tag != -1:
                bpm_tagend = song_data[bpm_tag:].find('" ')
                bpm = round(60/float(song_data[bpm_tag+5:bpm_tagend+bpm_tag]),1)
            else:
                bpm = float('nan')

            #find key
            key_tag = song_data.find('Key=')
            if key_tag != -1:
                key_tagend = song_data[key_tag:].find('" ')
                key = song_data[key_tag+5:key_tagend+key_tag]
            else:
                key = ''

            music_data = dict(Song_Id = vid_ids[i],
                              Genre = genre,
                              Key = key,
                              BPM = bpm)

            songs_data.append(music_data)
    
    return songs_data

#use function in script
#read xml data

st = time.time()
with open('C:\\Users\\USER\\Documents\\VirtualDJ\\database.xml', 'r',encoding="utf8") as f:
    xml_data = f.read()

#load song id list from songs file
song_info_file = r'C:\Users\USER\Documents\YTMusic Data\yt_songs_info.csv'
song_info_data = pd.read_csv(song_info_file)
songs_id_list = song_info_data['song_id'].tolist()

#pass into function
songs_other_data = get_xml_music_data(xml_data,songs_id_list)

#write results to dataframe
songs_other_data_pd = pd.DataFrame(songs_other_data)

#write to file
path = "C:/Users/USER/Documents/YTMusic Data/"
songs_musical_filename = path + 'yt_songs_musical_info.csv'
songs_other_data_pd.to_csv(songs_musical_filename,index=False)

et = time.time()

run_time = int(et - st)

print(f"Run time is {str(run_time)} seconds")


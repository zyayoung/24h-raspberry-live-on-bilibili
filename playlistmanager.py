# coding = utf-8
import os
import var_set
import multiprocessing as mp
import random
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode
import json
from mutagen.mp3 import MP3
from PIL import Image
import glob

class PlaylistManager:
    def __init__(self):
        print('Initializing play list...')
        self.play_list_ids = []
        self.file_names = []
        self.q_new_song = mp.Queue()

        # load local playlist
        if os.path.exists(var_set.download_path):
            self.song_path = os.path.join(var_set.download_path, 'song')
            if os.path.exists(self.song_path):
                self.file_names = os.listdir(self.song_path)
                for file_name in self.file_names:
                    self.play_list_ids.append(int(file_name[:10]))
            else:
                os.mkdir(self.song_path)

            self.pic_path = os.path.join(var_set.download_path, 'pic')
            if not os.path.exists(self.pic_path):
                os.mkdir(self.pic_path)

        else:
            os.mkdir(var_set.download_path)
            self.song_path = os.path.join(var_set.download_path, 'song')
            os.mkdir(self.song_path)
            self.pic_path = os.path.join(var_set.download_path, 'pic')
            os.mkdir(self.pic_path)
            self.add_song_by_id(521416315)

        self.player = mp.Process(target=self.player, name='Player', args=(self.q_new_song, self.file_names))
        self.player.start()

    def add_song_by_name(self, name):
        try:
            print('Searching '+name)
            api_url = 'https://api.imjad.cn/cloudmusic/?'
            code = urlencode({'type': 'search', 'limit': 1, 's': name})
            code = json.loads(urlopen(api_url + code).read().decode('utf-8'))
            if code['code'] == 200:
                song_id = code['result']['songs'][0]['id']
                self.add_song_by_id(song_id)
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def add_song_by_id(self, song_id):
        print('Adding', song_id)

        try:
            self.file_names = os.listdir(self.song_path)
            self.play_list_ids = []
            for file_name in self.file_names:
                self.play_list_ids.append(int(file_name[:10]))

            # check id
            if song_id in self.play_list_ids:
                for file in glob.glob(os.path.join(self.song_path, '%010d' % song_id + '*')):
                    self.q_new_song.put(os.path.split(file)[1])
                return

            # get song url
            info = json.loads(urlopen('https://api.imjad.cn/cloudmusic/?id=' + str(song_id) + '&br=320000').read().decode('utf-8'))
            if info['code'] != 200:
                print('[error]')
                print(info)
                return
            song_url = info['data'][0]['url']
            detil_info = json.loads(urlopen('https://api.imjad.cn/cloudmusic/?type=detail&id=' + str(song_id)).read().decode('utf-8'))
            if detil_info['code'] != 200:
                print('[error]')
                print(detil_info)
                return
            song_name = detil_info['songs'][0]['name']
            pic_url = detil_info['songs'][0]['al']['picUrl']

            # download song & pic
            mp3_file_name = '%010d' % song_id + ' ' + song_name + '.mp3'
            jpg_file_name = '%010d' % song_id + ' ' + song_name + '.jpg'

            print('Downloading...')
            print('songName: ' + song_name)
            print('songUrl: ' + song_url)
            print('picUrl: ' + pic_url)
            urlretrieve(song_url, os.path.join(self.song_path, mp3_file_name))
            urlretrieve(pic_url, os.path.join(self.pic_path, jpg_file_name))

            # resize img
            print('resizing image')
            img = Image.open(os.path.join(self.pic_path, jpg_file_name))
            w, h = img.size
            if h > 720 or w > 1280:
                ratio = min(720.0/h, 1280.0/w)
                img.thumbnail((int(h*ratio), int(w*ratio)))
            img = img.convert('RGB')
            img.save(os.path.join(self.pic_path, jpg_file_name), 'jpeg')

            print('done')

            # push q_new_song
            self.q_new_song.put(mp3_file_name)
            self.play_list_ids.append(song_id)
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def del_song_by_id(self, song_id):
        # del song & pic files
        try:
            self.file_names = os.listdir(self.song_path)
            self.play_list_ids = []
            for file_name in self.file_names:
                self.play_list_ids.append(int(file_name[:10]))

            if song_id in self.play_list_ids:
                for file in glob.glob(os.path.join(self.song_path, '%010d' % song_id + '*')):
                    os.remove(file)
                for file in glob.glob(os.path.join(self.pic_path, '%010d' % song_id + '*')):
                    os.remove(file)
            print('Deleted')
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    @staticmethod
    def player(q_add_song, playlist):
        while True:
            song_path = os.path.join(var_set.download_path, 'song')
            if os.path.exists(song_path):
                playlist = os.listdir(song_path)

            # get next song
            nxt_song_filename = None
            if not q_add_song.empty():
                nxt_song_filename = q_add_song.get()
                if nxt_song_filename not in playlist:
                    nxt_song_filename = random.choice(playlist)
            else:
                nxt_song_filename = random.choice(playlist)

            if nxt_song_filename:
                song_path = os.path.join(var_set.download_path, 'song')
                mp3_file_path = os.path.join(song_path, nxt_song_filename)

                pic_path = os.path.join(var_set.download_path, 'pic')
                img_file_path = os.path.join(pic_path, nxt_song_filename[:-4]+'.jpg')
                if not os.path.exists(img_file_path):
                    img_file_path = os.path.join(song_path, 'default_img.jpg')

                audio = MP3(mp3_file_path)
                seconds = audio.info.length  # 获取时长
                print('Next: ', nxt_song_filename[10:-4])

                cmd = 'ffmpeg -threads 0 -re -loop 1 -r 2 -t ' + str(int(seconds)) + ' -f image2' \
                      + ' -i "' + img_file_path + '"' \
                      + ' -i "' + mp3_file_path + '"' \
                      + ' -acodec copy -c:v h264 -crf 28 -f flv '\
                      + '"' + var_set.rtmp+var_set.live_code + '"'
                print(cmd)

                # start streaming
                os.system(cmd)
                # time.sleep(int(seconds))




# universal 24h live on bilibili (not only on raspberry pi)

b站直播点歌台（精简版）

demo: [http://live.bilibili.com/3448847](http://live.bilibili.com/3448847)

本项目是[晨旭大佬的直播点歌台](https://github.com/chenxuuu/24h-raspberry-live-on-bilibili)的精简重构版，目前的功能为：

重构的原有功能：
- 弹幕点歌
- 切歌
- 闲时随机播放预留歌曲
- 播放音乐时背景图片随机选择
- 已点播歌曲、视频自动进入缓存，无人点播时随机播放

新增功能：
- 播放音乐时显示专辑封面

未实现的原有功能：
- 存储空间达到设定值时，自动按点播时间顺序删除音乐、视频来释放空间
- 实时显示歌曲/视频长度
- 根据投喂礼物的多少来决定是否允许点播
- 弹幕点MV
- 弹幕反馈（发送弹幕）
- 旧版实现的视频推流功能
- 自定义介绍字幕
- 歌词滚动显示，同时滚动显示翻译歌词
- 显示排队播放歌曲，渲染视频
- 可点播b站任意视频（会员限制除外，番剧根据b站规定，禁止点播）


已知问题：

- 换歌、视频时会闪断

## 食用方法：

~~我这里用的是树莓派3B，系统2017-09-07-raspbian-stretch.img，官方默认软件源，其他配置请自测~~

在树莓派上食用请自行将编码器改为h264_omx

`-c:v h264`改为`-c:v h264_omx`

### 先准备餐具：

安装FFmpeg
```Bash
sudo apt-get install ffmpeg
```

若不成功，则可以尝试编译安装：

```Bash
sudo apt-get -y install autoconf automake build-essential libass-dev libfreetype6-dev libtheora-dev libtool libvorbis-dev pkg-config texinfo wget zlib1g-dev
```

安装x264编码器（时间较长）：

```Bash
git clone git://git.videolan.org/x264
cd x264
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
make
sudo make install
cd ..
rm -rf x264
```

libmp3lame & libopus & libvpx：

```Bash
sudo apt-get install libmp3lame-dev libopus-dev libvpx-dev
```

编译并安装ffmpeg（时间较长）：

```Bash
wget http://ffmpeg.org/releases/ffmpeg-3.3.2.tar.bz2
tar jxvf ffmpeg-3.3.2.tar.bz2
cd ffmpeg-3.3.2
sudo ./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --enable-libass --enable-libfreetype  --enable-omx --enable-omx-rpi --enable-encoder=h264_omx --enable-mmal --enable-hwaccel=h264_mmal --enable-decoder=h264_mmal
make -j4
sudo make install
cd ..
```

（以上有一部分代码参考自[ffmpeg源码编译安装（Compile ffmpeg with source）  Part 2 ： 扩展安装 - 人脑之战 - 博客园](http://www.cnblogs.com/yaoz/p/6944942.html)）

安装python3的mutagen & aiohttp库：

```Bash
sudo pip3 install mutagen aiohttp
```

### 烹饪&摆盘：

请修改下载里的`var_set.py`文件中的各种变量

### 吃吃吃：

```Bash
python3 main.py
```

# Thanks

[弹幕姬python](https://github.com/lyyyuna/bilibili_danmu)

[晨旭的直播点歌台](https://github.com/chenxuuu/24h-raspberry-live-on-bilibili)

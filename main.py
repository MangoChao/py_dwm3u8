from download_m3u8 import dlm
from search_m3u8 import sm

if __name__ == '__main__':
    # url = 'https://fuaf-uying.mushroomtrack.com/hls/AjToHMToKg1OJpr40BMizg/1715636791/24000/24397/24397.m3u8'
    # m3u8_url = 'https://ikcdn01.ikzybf.com/20221018/Drqu7QAg/2000kb/hls/index.m3u8'
    # m3u8_url = 'https://ikcdn01.ikzybf.com/20221018/Drqu7QAg/index.m3u8'

    weburl = 'https://99kubo.cc/vod-199959734/play-ep1031.html'
    save_file_name = 'ep1031'


    [title, m3u8_url_list] = sm.search(weburl)
    m3u8_url_list = list(set(m3u8_url_list))
    print(title)
    print(m3u8_url_list)
    # m3u8_url_list = ['https://surrit.com/0bfbc967-4b90-40a3-821a-87bb0073c5a7/1280x720/video.m3u8']
    for m3u8_url in m3u8_url_list:
        if dlm.download(m3u8_url, save_file_name):
            print(f'{m3u8_url} 下載成功')
        else:
            print(f'{m3u8_url} 下載失敗')


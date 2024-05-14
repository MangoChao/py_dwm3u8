import urllib.parse
from playwright.sync_api import sync_playwright
import requests
import re

from download_m3u8 import dlm

def get_ts_url(base_url, ts_url):
    if ts_url.startswith('http'):
        return ts_url

    if ts_url.startswith('/'):
        parsed_base_url = urllib.parse.urlparse(base_url)
        domain_with_scheme = parsed_base_url.scheme + '://' + parsed_base_url.netloc
        return domain_with_scheme + ts_url

    return base_url.rsplit('/', 1)[0] + '/' + ts_url

def check_content(url):
    response = requests.get(url)
    print(f"請求 URL: {url}, 狀態碼: {response.status_code}")

    if response.status_code == 200:
        content = response.text
        m3u8_urls = re.findall(r'https?://[^\s]*\.m3u8', content)
        if m3u8_urls:
            print("找到的 .m3u8 檔案：")
            for m3u8_url in m3u8_urls:
                print(m3u8_url)
                check_content(m3u8_url)
        else:
            ts_urls = re.findall(r'\b\w+\.ts\b', content)
            if ts_urls:
                print("找到正確的 .m3u8 路徑：",url)
            else:
                m3u8_paths = re.findall(r'(?<!\S)/?[^\s]+\.m3u8(?!\S)', content)
                if m3u8_paths:
                    print("找到的 .m3u8 字串：")
                    for m3u8_path in m3u8_paths:
                        print(m3u8_path)
                        m3u8_url = get_ts_url(url, m3u8_path)
                        print(m3u8_url)
                        check_content(m3u8_url)
                else:
                    print("沒找到 content：", content)

    else:
        print(f"無法取得網絡資料，狀態碼: {response.status_code}")


def getResponse(response):
    if "m3u8" in response.url:
        print("檢查m3u8 load url：",response.url)
        check_content(response.url)


def getm3u8():

    # weburl = 'https://jable.tv/videos/sone-185/'
    weburl = 'https://99kubo.cc/vod-199959734/play-ep1032.html'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.on('response', getResponse)
        page.goto(weburl)
        page.wait_for_load_state('load')
        browser.close()


if __name__ == '__main__':
    # url = 'https://fuaf-uying.mushroomtrack.com/hls/AjToHMToKg1OJpr40BMizg/1715636791/24000/24397/24397.m3u8'
    m3u8_url = 'https://ikcdn01.ikzybf.com/20221018/Drqu7QAg/2000kb/hls/index.m3u8'
    # m3u8_url = 'https://ikcdn01.ikzybf.com/20221018/Drqu7QAg/index.m3u8'
    save_file_name = 'test'

    if dlm.download(m3u8_url, save_file_name):
        print('下載成功')
    else:
        print('下載失敗')
    # getm3u8()


import urllib.parse
import requests
import re
from playwright.sync_api import sync_playwright
import time

class SearchM3u8():
    def __init__(self) -> None:
        self.m3u8_url_list = []

    def get_ts_url(self, base_url, ts_url):
        if ts_url.startswith('http'):
            return ts_url

        if ts_url.startswith('/'):
            parsed_base_url = urllib.parse.urlparse(base_url)
            domain_with_scheme = parsed_base_url.scheme + '://' + parsed_base_url.netloc
            return domain_with_scheme + ts_url

        return base_url.rsplit('/', 1)[0] + '/' + ts_url

    def check_content(self, url):
        response = requests.get(url)
        print(f"請求 URL: {url}, 狀態碼: {response.status_code}")

        if response.status_code == 200:
            content = response.text
            m3u8_urls = re.findall(r'https?://[^\s]*\.m3u8', content)
            if m3u8_urls:
                print("找到的 .m3u8 檔案：")
                for m3u8_url in m3u8_urls:
                    print(m3u8_url)
                    self.check_content(m3u8_url)
            else:
                ts_urls = re.findall(r'\b\w+\.ts\b', content)
                if ts_urls:
                    print("找到正確的 .m3u8 路徑：", url)
                    self.m3u8_url_list.append(url)
                else:
                    m3u8_paths = re.findall(r'(?<!\S)/?[^\s]+\.m3u8(?!\S)', content)
                    if m3u8_paths:
                        print("找到的 .m3u8 字串：")
                        for m3u8_path in m3u8_paths:
                            print(m3u8_path)
                            m3u8_url = self.get_ts_url(url, m3u8_path)
                            print(m3u8_url)
                            self.check_content(m3u8_url)
                    # else:
                        # print("沒找到 content：", content)

        else:
            print(f"無法取得網絡資料，狀態碼: {response.status_code}, 依舊加入")
            self.m3u8_url_list.append(url)

    def getResponse(self, response):
        if "m3u8" in response.url:
            print("檢查m3u8 load url：", response.url)
            self.check_content(response.url)

    def search(self, weburl):
        self.m3u8_url_list = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.on('response', self.getResponse)
            page.goto(weburl)
            page.wait_for_load_state('load')
            title = page.title()

            browser.close()
        return [title, self.m3u8_url_list]

sm = SearchM3u8()




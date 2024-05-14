import aiohttp
import asyncio
import os
import urllib.parse

class DownloadM3u8():
    def __init__(self) -> None:
        self.download_dir = 'dw'

    # 合併ts
    async def merge_ts_files(self, base_file_path, num_files):
        print('開始合併ts..')
        merged_file_path = f'{self.download_dir}/{base_file_path}.ts'
        with open(merged_file_path, 'wb') as merged_file:
            for i in range(num_files):
                ts_file_path = f'{self.download_dir}/{base_file_path}_{i}.ts'
                if not os.path.exists(ts_file_path):  # 檢查
                    continue
                with open(ts_file_path, 'rb') as ts_file:
                    merged_file.write(ts_file.read())
                os.remove(ts_file_path)  # 刪除
        print('合併完成')

    def get_ts_url(self, base_url, ts_url):
        if ts_url.startswith('http'):
            return ts_url

        if ts_url.startswith('/'):
            parsed_base_url = urllib.parse.urlparse(base_url)
            domain_with_scheme = parsed_base_url.scheme + '://' + parsed_base_url.netloc
            return domain_with_scheme + ts_url

        return base_url.rsplit('/', 1)[0] + '/' + ts_url
    async def download_ts_file(self, ts_url, ts_file_path):
        for _ in range(3): #重試次數
            try:
                async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=60)) as session:
                    async with session.get(ts_url) as response:
                        if response.status != 200:
                            print(f'{ts_url} 下載失敗')
                            return False
                        with open(ts_file_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                # print(f'{ts_url} 下載完成')
                return True
            except Exception as e:
                print(f'{ts_url} Exception: {e}')
                print('等待重試...')
                await asyncio.sleep(1)
        return False

    #檢查m3u8內容是否有效,是否有ts
    def check_m3u8_valid(self, m3u8_text):
        if not '.ts' in m3u8_text:
            return False
        return True
    async def download_m3u8_video(self, m3u8_url, save_file_name):
        print('下載中..')
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(m3u8_url) as response:
                if response.status != 200:
                    print('m3u8連結無效')
                    return False

                m3u8_text = await response.text()
                if not self.check_m3u8_valid(m3u8_text):
                    print('m3u8內沒有ts路徑')
                    return False
                m3u8_list = m3u8_text.split('\n')
                m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

                tasks = []
                for i, ts_url in enumerate(m3u8_list):
                    #跳過沒有ts的行數
                    if self.check_m3u8_valid(ts_url):
                        ts_url = self.get_ts_url(m3u8_url, ts_url)
                        ts_file_path = f'{self.download_dir}/{save_file_name}_{i}.ts'

                        task = asyncio.ensure_future(
                            self.download_ts_file(ts_url, ts_file_path))
                        tasks.append(task)
                    else:
                        print('沒有ts字串 行數:', i+1)
                await asyncio.gather(*tasks)

        print('下載完成')
        await self.merge_ts_files(save_file_name, len(m3u8_list))
        return True

    def download(self, m3u8_url, save_file_name):
        # 如果資料夾不存在,新建
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.download_m3u8_video(m3u8_url, save_file_name))
        return result

dlm = DownloadM3u8()




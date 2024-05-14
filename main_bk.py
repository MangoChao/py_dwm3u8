import aiohttp
import asyncio
import os

async def download_ts_file(ts_url, ts_file_path):
    for _ in range(3):  # 尝试重试3次
        try:
            async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(ts_url) as response:
                    if response.status != 200:
                        print(f'{ts_url} 下载失败')
                        return False
                    with open(ts_file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
            # print(f'{ts_url} 下载完成')
            return True
        except Exception as e:
            print(f'下载 {ts_url} 时出现错误: {e}')
            print('等待并重试...')
            await asyncio.sleep(1)  # 等待一段时间后重试
    return False

async def download_m3u8_video(url, file_path):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print('m3u8视频下载链接无效')
                return False

            m3u8_text = await response.text()
            m3u8_list = m3u8_text.split('\n')
            m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

            tasks = []
            for i, ts_url in enumerate(m3u8_list):
                ts_url = url.rsplit('/', 1)[0] + '/' + ts_url
                ts_file_path = file_path.rsplit('.', 1)[0] + f'_{i}.ts'
                task = asyncio.ensure_future(
                    download_ts_file(ts_url, ts_file_path))
                tasks.append(task)

            await asyncio.gather(*tasks)

    print('m3u8视频下载完成')
    await merge_ts_files(file_path, len(m3u8_list))
    return True

async def merge_ts_files(base_file_path, num_files):
    merged_file_path = base_file_path.rsplit('.', 1)[0] + '_merged.ts'
    with open(merged_file_path, 'wb') as merged_file:
        for i in range(num_files):
            ts_file_path = base_file_path.rsplit('.', 1)[0] + f'_{i}.ts'
            if not os.path.exists(ts_file_path):  # 检查文件是否存在
                continue
            with open(ts_file_path, 'rb') as ts_file:
                merged_file.write(ts_file.read())
            os.remove(ts_file_path)  # 删除临时的.ts文件
    print('所有ts文件合并完成')

if __name__ == '__main__':
    url = 'https://galav-oxwy.mushroomtrack.com/hls/jfQduXTHTY-YfDxC-PURIQ/1715707789/28000/28608/28608.m3u8'
    ts_file_path = 'dw/22148.ts'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_m3u8_video(url, ts_file_path))

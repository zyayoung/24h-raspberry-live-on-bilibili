# coding=utf-8

import asyncio
from bilibiliClient import bilibiliClient
import multiprocessing as mp

if __name__ == '__main__':
    q = mp.Queue()

    while True:
        try:
            danmuji = bilibiliClient()

            tasks = [
                        danmuji.connectServer(),
                        danmuji.HeartbeatLoop()
                    ]
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(asyncio.wait(tasks))
            except KeyboardInterrupt:
                danmuji.connected = False
                danmuji.closePlayer()
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                loop.run_forever()
                loop.close()
                exit()
        except Exception as e:  # 防炸
            print('shit')
            print(e)
            danmuji.connected = False
            danmuji.closePlayer()
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_forever()
            loop.close()

import os

import requests
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
from time import sleep

# 假设BASE_URL已经被定义
# BASE_URL = 'http://8.152.7.118:9999'
# BASE_URL = 'http://poxiaoai.com:29999'
BASE_URL = os.environ.get("MAGIC_API","http://192.168.31.125:9999")

class RClient:
    def __init__(self, timeout=1000, retries=2, backoff_factor=0.8):
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor

    def _handle_request(self, method, *args, **kwargs):
        for attempt in range(self.retries + 1):
            try:
                kwargs['timeout'] = self.timeout
                response = method(*args, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as errh:
                logging.error(f"Http Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                logging.error(f"Error Connecting: {errc}")
            except requests.exceptions.Timeout as errt:
                logging.error(f"Timeout Error: {errt}")
            except requests.exceptions.RequestException as err:
                logging.error(f"OOps: Something Else {err}")

            if attempt < self.retries:
                wait_time = self.backoff_factor * (2 ** attempt)
                logging.info(f"Retrying in {wait_time} seconds...")
                sleep(wait_time)
            else:
                logging.error("Max retries exceeded.")
                return None

    def post(self, endpoint, data=None, params=None,json=None, data_class=None, headers={'Content-Type': 'application/json'}):
        if endpoint.startswith('/'):
            url = f"{BASE_URL}{endpoint}"
        else:
            url = f"{BASE_URL}/{endpoint}"
            # logging.info(f"Sending POST request to {url}")
        response = self._handle_request(requests.post, url, data=data,params=params, json=json, headers=headers, timeout=self.timeout)
        if response and response.status_code == 200:
            data = response.json()
            if (data['message'] != 'success'):
                logging.error(f"服务执行出错,服务错误信息为：{data}")
                return None
            if (data['code'] != 1):
                logging.error(f"服务执行出错,服务错误信息为{data}")
                return None
            data_list = data['data']
            if data_class and isinstance(data_list, list):
                return [data_class(**item) for item in data_list]
            else:
                return data_list
        else:
            logging.error("Failed to retrieve data.")
            return None

    def get(self, endpoint, params=None, json=None,headers=None, data_class=None):
        if endpoint.startswith('/'):
            url = f"{BASE_URL}{endpoint}"
        else:
            url = f"{BASE_URL}/{endpoint}"

            # logging.info(f"Sending GET request to {url}")
        response = self._handle_request(requests.get, url, json=json,params=params, headers=headers, timeout=self.timeout)
        if response and response.status_code == 200:
            data = response.json()
            if (data['message'] != 'success'):
                logging.error(f"服务执行出错,服务错误信息为：{data}")
                return None
            if (data['code'] != 1):
                logging.error(f"服务执行出错,服务错误信息为{data}")
                return None
            data_list = data['data']
            if data_class and isinstance(data_list, list):
                return [data_class(**item) for item in data_list]
            else:
                return data_list
        else:
            logging.error("Failed to retrieve data.")
            return None

class ClientUtils:
    @staticmethod
    def dynamic_update_lady_material(body, params):
        response=RClient().post('/editor_content/clip_lady_material/dynamic_update',json=body,params=params)
        if response is None:
            raise Exception(f"动态更新美女号视频状态失败 body:{body},params:{params}")
        return response

    @staticmethod
    def not_carry(target_path,video_path):
        body={
            "target_path": target_path,
            "video_path": video_path
        }
        response=RClient().post('/editor_content/clip_carry_material/set_uncarry',json=body)
        if response is None:
            raise Exception("设置游戏号视频状态失败")
        return response

    @staticmethod
    def carry_with_voice(target_path,video_path):
        body={
            "target_path": target_path,
            "video_path": video_path
        }
        response=RClient().post('/editor_content/clip_carry_material/carry_has_voice',json=body)
        if response is None:
            raise Exception("设置游戏号视频状态失败")
        return response
    @staticmethod
    def carry_without_voice(target_path,video_path):
        body={
            "target_path": target_path,
            "video_path": video_path
        }
        response=RClient().post('/editor_content/clip_carry_material/carry_has_no_voice',json=body)
        if response is None:
            raise Exception("设置游戏号视频状态失败")
        return response


# 使用示例

if __name__ == '__main__':
    # rows_affected = ClientUtils.dynamic_update_lady_material(body={"is_carry": 1, "has_voice":1, "video_path": ""}, params=None)
    body = {
        "is_carry":2,
        # "has_voice": self.has_voice,
        "video_path": "F:/wsl/chfs/搬运视频/国内搬运/美女号/已筛选/搬运/100000003/dy_7449958001177365787_test.mp4"
    }
    params = {
        "video_path": "F:/wsl/chfs/搬运视频/国内搬运/美女号/已筛选/搬运/100000003/dy_7449958001177365787.mp4"
    }
    rows_affected = ClientUtils.dynamic_update_lady_material(body=body, params=params)
    # target_path='F:/wsl/chfs/搬运视频/国内搬运/待筛选/抖音/dy_1744256860424.mp41'
    # video_path='F:/wsl/chfs/搬运视频/国内搬运/待筛选/抖音/dy_1744256860424.mp4'
    # ClientUtils.not_carry(target_path,video_path)
    # ClientUtils.carry_with_voice(target_path,video_path)
    # print(ClientUtils.carry_without_voice(target_path,video_path))
    # ClientUtils.set_fetch_data_is_transcribe_transcribing_game([1,2,3,4,5])
    # ClientUtils.set_is_transcribe_to_zero_game()
    # ClientUtils.set_is_transcribe_game(1,11)
   # print(ClientUtils.fetch_data_from_game(10))
    # print(ClientUtils.fetch_data_from_AIMountain(1))
    # print(ClientUtils.set_fetch_data_is_transcribe_transcribing_AIMountain([1,2]))
    # ClientUtils.set_is_transcribe_AIMountain(3,3)                    rows_affected = ClientUtils.dynamic_update_carry_material(body={"is_carry": self.is_carry, "has_voice": self.has_voice},params=None)
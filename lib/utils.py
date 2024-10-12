# test
import requests
import time
import json
import re
import sys
import warnings
import requests
import os
from zipfile import ZipFile
import shutil


def get_time_now() -> str:
    '''
    返回一个代表当前时间字符串，格式如[2024-10-08 15:12:55]
    '''
    time_str = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())

    return time_str


def count_to_unit(count: int, digit = 2) -> str:
    '''
    将一个大于10_000整数转化为带有K，M，G，T，P，E的字符串
    例如 11230转化为 “11.23K”， 7486522转化为“7.486M”
    '''
    if count < 10000:
        return (str(count))

    unit_lst = ['K', 'M', 'G', 'T', 'P', 'E', 'KE', 'ME', 'GE', 'TE', 'PE', 'EE', '']
    is_converted = False
    for i in range(len(unit_lst)):
        if round(count / 1000 ** (i + 1), digit) < 1:
            unit = unit_lst[i - 1]
            num = count / 1000 ** i
            is_converted = True
            break

    if not is_converted:
        return str(count)

    # print(round(num, 2), unit)
    return str(round(num, digit)) + unit


def send_message(machine_type: str, machine_id: str, data_dir: str) -> int:
    """
    若数据已经传输完成,则把相应信息发送到飞书群里面通知大家可以使用该数据
    """

    msg = f"{get_time_now()} 下机数据传输完成，机器类型： {machine_type} 机器号：{machine_id}，数据路径：{data_dir}"
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/3feb487a-e2c3-4ea1-b96f-26e1278489d4'

    data = {
        "msg_type": "text",
        "content": {"text": msg},
    }
    r = requests.post(webhook, headers = headers, data = json.dumps(data))
    return r.status_code


def generate_remote_data_path(local_path: str = '', machine_id_int: int = 0, id_to_tag_file: str = 'Pro_id.txt', remote_root = '/share/data/salus', machine_type = 'Pro') -> str:
    '''
    从本地数据路径，机器号等信息，生成服务器的上传路径，通常上传路径是/share/data/salus/{machine_type}/{machine_tag}_{machine_id}/
    例如：/share/data/salus/Pro/C2201010004_4/
    '''

    id_tag_dict = {}
    with open(id_to_tag_file) as in_f:
        for line_str in in_f:
            line_str = line_str.strip()
            if len(line_str) == 0 or line_str.startswith('#'):
                continue

            line_lst = line_str.split()

            try:
                id_tag_dict[int(line_lst[0])] = line_lst[1]
            except ValueError as ex:
                print(ex)
                print('generate_remote_data_path： 目前machine id仅支持数字和下划线', line_lst[0], '不是数字')
                continue

    machine_id_from_path_int = int(re.findall(f'(?<={machine_type})\\d+', local_path)[0])
    if machine_id_int != 0:
        if machine_id_int != machine_id_from_path_int:
            message = f'generate_remote_data_path:警告 本地数据路径{local_path} 中的 machine_id: {machine_id_from_path_int} 与提供的machine_id： {machine_id_int}不符'
            warnings.warn(message)
        machine_id_final_int = machine_id_int

    else:
        machine_id_final_int = machine_id_from_path_int

    try:
        machine_tag_str = id_tag_dict[machine_id_final_int]
    except KeyError as ex:
        message = f'generate_remote_data_path: 在tag文件{id_to_tag_file}中未找到machine id {machine_id_final_int}的tag'
        sys.exit(message)

    remote_data_path_str = f'{remote_root}/{machine_type}/{machine_tag_str}_{machine_id_final_int}'

    return remote_data_path_str


def self_upgrade(url: str = 'https://github.com/yaotianran/upload_to_server/archive/refs/heads/master.zip') -> int:
    '''
    silently upgrade
    '''

    try:
        get_response = requests.get(url, stream = True)
    except Exception:
        return

    file_name = url.split("/")[-1]
    try:

        with open(file_name, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size = 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    except:
        return

    try:
        with ZipFile(file_name, 'r') as zObject:
            zObject.extractall()
    except:
        return

    file_replace_lst: list[tuple[str, str], ...] = [('upload_to_server-master\\upload.py', 'app\\upload.py'),
                                                    ('upload_to_server-master\\lib\\server.py', 'app\\lib\\server.py'),
                                                    ('upload_to_server-master\\lib\\utils.py', 'app\\lib\\utils.py'),
                                                    ]

    for src, dst in file_replace_lst:
        try:
            os.replace(src, dst)
        except:
            pass

    try:
        os.remove('master.zip')
        shutil.rmtree('upload_to_server-master')
    except:
        pass

    return 0


if __name__ == '__main__':

    # r = send_message('测试3', '测试3')

    # local_path = r'E:\NGS\NGS\OutFile\202408291906_Pro004_B_PPH32501170007_PCR3_1_3_WGS_PE150_1000M_23PM'
    # id_to_tag_file = r'..\Pro_id.txt'
    # remote_data_path_str = generate_remote_data_path(local_path = local_path, machine_id_int = 14, id_to_tag_file = id_to_tag_file)
    # print(remote_data_path_str)
    i = 1

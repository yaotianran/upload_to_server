# v0.1a
import sys
import os
import os.path as path
from time import time

sys.path.append('app\\lib')
sys.path.append('python-3.12.7-embed-amd64\\Lib\\site-packages')

import requests
import paramiko
from server import server
import utils


# from lib.server import server
# import lib.utils as utils


# import server
# import utils


def get_arguments() -> dict:
    '''
    获取参数.
    '''

    arguments_dict = {}
    if os.access('machine.ini', os.R_OK):
        with open('machine.ini', 'rt') as in_f:
            for line_str in in_f:
                line_lst = line_str.split()
                arguments_dict[line_lst[0]] = line_lst[1]

    # 上传的项目目录
    arguments_dict['local_path'] = []
    while True:
        local_path_str = input('<将所需上传的项目目录（例如：202410181422_C22091401_A_PRM32502260044_SEQ_A_AB_PE150）拖曳到此处后按回车，直接回车结束输入> ')
        if local_path_str != '' and local_path_str not in arguments_dict['local_path']:
            arguments_dict['local_path'].append(local_path_str)
        elif arguments_dict['local_path'] != []:
            break
        else:
            pass

    # 上传文件类型
    arguments_dict['pattern'] = ['.fastq.gz', '.fq.gz', '.fq', '.fastq', '.md5']
    is_upload_image_str = input('<是否上传图像文件，输入y上传，直接按回车不上传> ')
    if is_upload_image_str.upper() in ['Y', 'YES', 'T', 'TRUE', '是']:
        arguments_dict['pattern'].extend(['.tif', '.tiff', '.png', '.TIF', '.TIFF', '.PNG'])
    else:
        is_upload_image_str = '否'

    # 测序仪类型
    while True:
        if 'machine_type' in arguments_dict.keys():
            machine_type_str = input(f'<输入测序仪类型【Pro, Nimbo, Evo】，直接按回车默认为{arguments_dict['machine_type']}> ')
            if machine_type_str == '':
                machine_type_str = arguments_dict['machine_type']
        else:
            machine_type_str = input(f'<输入测序仪类型【Pro, Nimbo, Evo】，直接按回车默认为Pro> ')
            if machine_type_str == '':
                machine_type_str = 'Pro'

        if machine_type_str.lower() in ['pro', 'evo', 'nimbo']:
            break
    arguments_dict['machine_type'] = machine_type_str[0].upper() + machine_type_str[1:].lower()

    # 机器号
    while True:
        if 'machine_id' in arguments_dict.keys():
            temp = input(f"<直接按回车使用{arguments_dict['machine_id']} 或手动输入机器号（测试请输入99999）> ")
            if temp == '':
                temp = arguments_dict['machine_id']
        else:
            temp = input(f'<输入机器号> ')

        try:
            machine_id_int = int(temp)
            break
        except ValueError:
            pass
    arguments_dict['machine_id'] = machine_id_int

    # 确认
    print()
    print('确认信息')
    print(f'{len(arguments_dict['local_path'])}个上传目录：')
    for local_path_str in arguments_dict['local_path']:
        print(f'{local_path_str}')
    print()
    print(f'是否上传图片：{is_upload_image_str}')
    print()
    print(f'机器类型和编号：{machine_type_str}，{machine_id_int}')
    if input('<确认上述信息是否正确，直接按回车确认正确，输入N重新运行>') != '':
        print('上述信息有误，重新运行脚本')
        sys.exit(1)

    # 保存machine_type和machine_id
    with open('machine.ini', 'wt') as out_f:
        for key in ['machine_type', 'machine_id']:
            out_f.writelines(f'{key}\t{arguments_dict[key]}\n')

    return arguments_dict


def main(argvList = sys.argv, argv_int = len(sys.argv)):

    try:
        if int(str(time())[-1]) == 9:
            _ = utils.self_upgrade()
            sys.exit(1)
    except Exception as ex:
        pass

    arguments_dict = get_arguments()

    local_path = arguments_dict['local_path'][0]
    machine_id_int = arguments_dict['machine_id']
    machine_type = arguments_dict['machine_type']
    id_to_tag_file = 'app\\' + arguments_dict['machine_type'] + '_id.txt'
    remote_folder_str = utils.generate_remote_data_path(local_path, machine_id_int, id_to_tag_file, machine_type = machine_type)
    print('服务器数据上传路径： ', remote_folder_str)

    data_server = server(ip = '192.168.0.185')
    print('正在连接服务器192.168.0.185 ...')
    data_server.generate_sftp_client(username = 'dtrans', private_key_file = 'app\\test_id_rsa')

    for local_path_str in arguments_dict['local_path']:
        if 'Res' not in os.listdir(local_path_str) and 'Res1' not in os.listdir(local_path_str):
            message = f'{path.basename(local_path_str)}，该上传目录下无Res，确定这是一个项目文件？'
            print(message)
        data_server.upload_a_folder(local_path_str, remote_folder_str, pattern = arguments_dict['pattern'])
        _ = utils.send_message(machine_type, str(machine_id_int), path.basename(local_path_str), remote_folder_str)
    print('\nDone')

    return


if __name__ == '__main__':
    main()




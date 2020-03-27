# -*- coding: utf-8 -*-
import json
import re
import requests
import time
import pandas as pd
import os
import requests.sessions
lists = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
         "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

reg_code_dic = {
    '100': '亚洲',
    '200': '非洲',
    '300': '欧洲',
    '400': '拉丁美洲',
    '500': '北美洲',
    '600': '大洋洲',
}


# def get_cookies(url):
#     str = ''
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     browser = webdriver.Chrome(options=options)
#     browser.get(url)
#     for i in browser.get_cookies():
#         try:
#             name = i.get('name')
#             value = i.get('value')
#             str = str + name + '=' + value + ';'
#         except ValueError as e:
#             print(e)
#     return str

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}
url = "http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=gjnd&rowcode=sj&colcode=reg&wds=%5B%7B%22wdcode%22%3A%22zb%22%2C%22valuecode%22%3A%22A{}%22%7D%5D&dfwds=%5B%7B%22wdcode%22%3A%22reg%22%2C%22valuecode%22%3A%22{}%22%7D%5D&k1={}"


def get_code(ids, reg):  #
    c = int(time.time() * 1000)   # 时间戳
    id_list = ids.split(".")      
    b = ""
    for i in range(1, len(id_list)):
        index = int(id_list[i])
        if index < 36:
            b += "0" + lists[index]
        else:
            b += "1" + lists[index - 36]
    new_url = url.format(b, reg, c)
    # response = requests.get(new_url, headers=headers).content.decode()
    s = requests.session()
    s.get('http://data.stats.gov.cn/easyquery.htm?m=getOtherWds&dbcode=gjnd&rowcode=sj&colcode=reg&wds=%5B%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%22LAST20%22%7D%5D')
    response = s.get(new_url, headers=headers).content.decode()
    return response, b, '.'.join(id_list[0:len(id_list) - 1])


def save_as_csv(json_file, file_name):
    data = json_file
    sj_dic = {}
    reg_dic = {}

    # for i in range(len(data['returndata']['wdnodes'][0]['nodes'])):
    #     cname_zb = data['returndata']['wdnodes'][0]['nodes'][i]['cname'] + '(' + \
    #                data['returndata']['wdnodes'][0]['nodes'][i]['unit'] + ')'
    #     code_zb = data['returndata']['wdnodes'][0]['nodes'][i]['code']
    #     zb_dic[cname_zb] = code_zb

    zb_k = data['returndata']['wdnodes'][0]['nodes'][0]['cname']
    zb_v = data['returndata']['wdnodes'][0]['nodes'][0]['code']

    for i in range(len(data['returndata']['wdnodes'][1]['nodes'])):
        cname_reg = data['returndata']['wdnodes'][1]['nodes'][i]['cname']
        code_reg = data['returndata']['wdnodes'][1]['nodes'][i]['code']
        reg_dic[cname_reg] = code_reg

    for i in range(len(data['returndata']['wdnodes'][2]['nodes'])):
        cname_sj = data['returndata']['wdnodes'][2]['nodes'][i]['cname']
        code_sj = data['returndata']['wdnodes'][2]['nodes'][i]['code']
        sj_dic[cname_sj] = code_sj

    data_dic = {"时间": []}
    add_zb = True

    # for sj_k, sj_v in sj_dic.items():
    #     #     for zb_k, zb_v in zb_dic.items():
    #     #         # data['returndata']['datanodes']  # 数据
    #     #         # len(data['returndata']['datanodes'])
    #     #         newcode = 'zb.{0}_sj.{1}'.format(zb_v, sj_v)
    #     #         if add_zb:
    #     #             data_dic["指标"].append(zb_k)
    #     #         # print(zb_k)
    #     #         for item in data['returndata']['datanodes']:
    #     #             if item['code'] == newcode:
    #     #                 if sj_k in data_dic.keys():
    #     #                     data_dic[sj_k].append(item['data']['data'])
    #     #                 else:
    #     #                     data_dic[sj_k] = [item['data']['data']]
    #     #                 break
    #     #     add_zb = False

    for reg_k, reg_v in reg_dic.items():
        for sj_k, sj_v in sj_dic.items():
            newcode = 'zb.{0}_reg.{1}_sj.{2}'.format(zb_v, reg_v, sj_v)
            if add_zb:
                data_dic["时间"].append(sj_k)
            for item in data['returndata']['datanodes']:
                if item['code'] == newcode:
                    if reg_k in data_dic.keys():
                        data_dic[reg_k].append(item['data']['data'])
                    else:
                        data_dic[reg_k] = [item['data']['data']]
                    break
        add_zb = False

    df = pd.DataFrame(data=data_dic).sort_index(axis=0, ascending=True)
    df.to_csv(file_name + ".csv", index=False, encoding="utf-8")


def detile_response(response, file_name):  # 保存文件
    try:
        py_str = json.loads(response)  # 若获取到的响应不是严格的json格式,loads会报错
    except:
        py_str = {"info": "不是json格式"}
    save_as_csv(py_str, file_name)
    print('已爬取--', file_name)


if __name__ == '__main__':
    while reg_code_dic:
        reg_item = reg_code_dic.popitem()
        root_name = "指标" + "\\" + reg_item[1]
        reg = reg_item[0]
        if not os.path.exists(root_name):
            os.makedirs(root_name)
        tree_dic = {}
        file_path_dic = {}
        with open("gj_filetree_1.txt", "r", encoding="utf-8") as tree:
            for line in tree:
                ids, name = line.replace("\n", "").split(",", 1)
                tree_dic[ids] = name
                response, a, parent = get_code(ids, reg)
                if parent == '1':
                    file_path_dic[ids] = root_name + "\\" + name
                    if not os.path.exists(file_path_dic[ids]):
                        os.makedirs(file_path_dic[ids])
                    print("(" + ids + ")" + name)
                else:
                    if parent == '1.7':
                        file_path_dic[ids] = file_path_dic[parent] + "\\" + name
                        if not os.path.exists(file_path_dic[ids]):
                            os.makedirs(file_path_dic[ids])
                    else:
                        if parent in file_path_dic.keys():
                            file_name = file_path_dic[parent] + "\\" + name
                            detile_response(response, file_name)
                





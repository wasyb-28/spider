# -*- coding: utf-8 -*-
import json
import re
import requests
import time
import pandas as pd
import os

lists = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
         "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
url = "http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22zb%22%2C%22valuecode%22%3A%22A{}%22%7D%2C%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%22LAST20%22%7D%5D&k1={}"


def get_code(ids):  #
    
    c = int(time.time() * 1000)   # 时间戳
    id_list = ids.split(".")      
    b = ""
    for i in range(1, len(id_list)):
        index = int(id_list[i])
        if index < 36:
            b += "0" + lists[index]
        else:
            b += "1" + lists[index - 36]
    new_url = url.format(b, c)
    response = requests.get(new_url, headers=headers).content.decode()
    return response, b, '.'.join(id_list[0:len(id_list) - 1])


def save_as_csv(json_file, file_name):
    data = json_file
    zb_dic = {}
    sj_dic = {}
    for i in range(len(data['returndata']['wdnodes'][0]['nodes'])):
        cname_zb = data['returndata']['wdnodes'][0]['nodes'][i]['cname'] + '(' + \
                   data['returndata']['wdnodes'][0]['nodes'][i]['unit'] + ')'
        code_zb = data['returndata']['wdnodes'][0]['nodes'][i]['code']
        zb_dic[cname_zb] = code_zb

    for i in range(len(data['returndata']['wdnodes'][1]['nodes'])):
        cname_sj = data['returndata']['wdnodes'][1]['nodes'][i]['cname']
        code_sj = data['returndata']['wdnodes'][1]['nodes'][i]['code']
        sj_dic[cname_sj] = code_sj

    data_dic = {"指标": []}
    add_zb = True
    for sj_k, sj_v in sj_dic.items():
        for zb_k, zb_v in zb_dic.items():
            # data['returndata']['datanodes']  # 数据
            # len(data['returndata']['datanodes'])
            newcode = 'zb.{0}_sj.{1}'.format(zb_v, sj_v)
            if add_zb:
                data_dic["指标"].append(zb_k)
            # print(zb_k)
            for item in data['returndata']['datanodes']:
                if item['code'] == newcode:
                    if sj_k in data_dic.keys():
                        data_dic[sj_k].append(item['data']['data'])
                    else:
                        data_dic[sj_k] = [item['data']['data']]
                    break
        add_zb = False

    df = pd.DataFrame(data=data_dic).sort_index(axis=1, ascending=False)
    df.to_csv(file_name + ".csv", index=False, encoding="utf-8")


def detile_response(response, file_name):  # 保存文件
    try:
        py_str = json.loads(response)  # 若获取到的响应不是严格的json格式,loads会报错
    except:
        py_str = {"info": "不是json格式"}
    save_as_csv(py_str, file_name)


if __name__ == '__main__':
    root_name = "国内指标"
    if os.path.exists(root_name) == False:
        os.makedirs(root_name)
    tree_dic = {}
    file_path_dic = {}
    with open("filetree.txt", "r", encoding="utf-8-sig") as tree:
        for line in tree:
            ids, name = line.replace("\n", "").split(",")
            # if ids == "1.5.7":
            #     aaa = 0
            tree_dic[ids] = name
            response, a, parent = get_code(ids)
            if parent in file_path_dic.keys():
                file_name = file_path_dic[parent] + "\\" + name
            else:
                file_name = root_name + "\\" + name
                print(line)
                
            if len(re.findall(r"对不起，未能找到符合查询条件的信息", response)) == 0:
                detile_response(response, file_name)
            else:
                if parent == "1":
                    file_path_dic[ids] = root_name + "\\" + name
                    if os.path.exists(file_path_dic[ids]) == False:
                        os.makedirs(file_path_dic[ids])
                    print("(" + ids + ")" + name)
                else:
                    file_path_dic[ids] = file_path_dic[parent] + "\\" + name
                    if os.path.exists(file_path_dic[ids]) == False:
                        os.makedirs(file_path_dic[ids])
                    print("    " * parent.count("."), "(" + ids + ")" + name)

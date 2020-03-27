import os
reg_dic = {
    '100': '亚洲',
    '200': '非洲',
    '300': '欧洲',
    '400': '拉丁美洲',
    '500': '北美洲',
    '600': '大洋洲',
}

reg_item = reg_dic.popitem()
print(reg_item)
print(reg_dic)
reg_item = reg_dic.popitem()
print(reg_item)
print(reg_dic)
# root_name = '指标' + "\\" + reg_item[1]
# if not os.path.exists(root_name):
#     os.makedirs(root_name)
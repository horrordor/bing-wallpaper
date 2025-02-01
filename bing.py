import copy
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'referer': 'https://www.pixiv.net/ranking.php?mode=daily&content=illust',
}


def split_array(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]


def get_bing_pic(json_path='./bing.json'):
    enddate = None
    json_data = None
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    with open(json_path, 'w', encoding='utf-8') as f:
        url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'
        temp = requests.get(url, headers=headers).json()['images'][0]
        if 'https://bing.com' + temp['urlbase'] != json_data[0][1]:
            print('New picture found!')
            json_data.insert(
                0, [temp['copyright'], 'https://bing.com' + temp['urlbase']])

        enddate = temp['enddate']
        f.write(json.dumps(json_data, ensure_ascii=False, indent=4))
    return datetime(int(enddate[:4]), int(enddate[4:6]), int(enddate[6:]))


# def get_pixiv_pic(path):
#     for n in range(1, 2):
#         url = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%d&format=json' % n
#         response = requests.get(url, headers=headers)
#         illust_id = re.findall('"illust_id":(\d+?),', response.text)
#         picUrl = ['https://www.pixiv.net/artworks/' + i for i in illust_id]
#         for url in picUrl:
#             repeat = 1
#             response = requests.get(url, headers=headers)
#             # 提取图片名称
#             name = re.search('"illustTitle":"(.+?)"', response.text)
#             name = name.group(1)
#             if re.search('[\\\ \/ \* \? \" \: \< \> \|]', name) != None:
#                 name = re.sub('[\\\ \/ \* \? \" \: \< \> \|]', str(repeat),
#                               name)
#                 repeat += 1
#             # 提取图片原图地址
#             picture = re.search('"original":"(.+?)"},"tags"', response.text)
#             pic = requests.get(picture.group(1), headers=headers)
#             with open(path + '%s.%s' % (name, picture.group(1)[-3:]),
#                       'wb') as f:
#                 f.write(pic.content)


def build(today):
    # 创建Jinja2环境
    env = Environment(loader=FileSystemLoader('templates'))

    # 获取图片列表
    img_list = []
    with open('./bing.json', 'r', encoding='utf-8') as f:
        img_list = json.load(f)

    _today = copy.deepcopy(today)
    index = 0
    for i in img_list:
        data = {
            'pre':  f"/pages/{img_list[index - 1][1].split('=')[1]}.html" if index >= 1 else 'javascript:void(0);', \
            'next': f"/pages/{img_list[index + 1][1].split('=')[1]}.html" if index < len(img_list) - 1 else 'javascript:void(0);', \
            'pic': img_list[index][1] + '_1920x1080.jpg',
            'back': '/' if index < 12 else '/p/%08d.html' % (index // 12, ),
            'title': img_list[index][0],
            'date': _today.strftime('%Y-%m-%d')
        }

        with open( \
                f"./pages/{img_list[index][1].split('=')[1]}.html", "w", encoding='utf-8' \
            ) as g:
            g.write(env.get_template('page.j2').render(data))
        index += 1
        _today = _today - timedelta(days=1)

    _today = copy.deepcopy(today)
    index = 0
    for i in split_array(img_list, 12):
        items = []
        for j in i:
            items.append({
                'thumbnail': j[1] + '_400x240.jpg',
                'pic_480p': j[1] + '_800x480.jpg',
                'pic_1080p': j[1] + '_1920x1080.jpg',
                'pic_uhd': j[1] + '_UHD.jpg',
                'page': f"/pages/{j[1].split('=')[1]}.html",
                'title': j[0],
                'date': today.strftime('%Y-%m-%d')
            })
            today = today - timedelta(days=1)


        data = {
            'items': items,
            'index': index + 1,
            'statement': index != (len(img_list) + 11) // 12 - 1,
            'count': (len(img_list) + 11) // 12,
            'pre': "/p/%08d.html" % (index - 1, ) if index > 1 else '/', \
            'next': "/p/%08d.html" % (index + 1, ) if index < (len(img_list) + 11) // 12 - 1 else 'javascript:void(0);'
        }
        with open("p/%08d.html" % (index, ) if index != 0 else 'index.html', \
                  "w", encoding='utf-8') as f:
            f.write(env.get_template('index.j2').render(data))
        index += 1

    with open("sitemap.xml", "w", encoding='utf-8') as f:
        pages = []
        items = []

        for index, item in enumerate(split_array(img_list, 12)):
            pages.append({
                'loc':
                f"p/{index:08d}.html" if index > 0 else 'index.html',
            })

            for j in item:
                items.append({
                    'loc': f"pages/{j[1].split('=')[1]}.html",
                })

        date = _today.strftime('%Y-%m-%d')

        f.write(
            env.get_template('map.j2').render({
                'pages': pages,
                'items': items,
                'date': date
            }))


if __name__ == "__main__":
    build(get_bing_pic())

    # saved_path = "./pixiv/"
    # Path(saved_path).mkdir(parents=True, exist_ok=True)
    # shutil.rmtree(saved_path)
    # Path(saved_path).mkdir(parents=True, exist_ok=True)
    # get_pixiv_pic(saved_path)
    # list_pic(path=saved_path)

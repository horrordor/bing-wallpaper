import json
import random
import requests
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            mpath, margs = self.path.split('?')
        except:
            mpath = self.path
            margs = ''
        self.do_action(mpath, margs)

    def do_POST(self):
        try:
            mpath, margs = self.path.split('?')
        except:
            mpath = self.path
            margs = ''
        datas = self.rfile.read(int(self.headers['content-length']))
        self.do_action(mpath, datas)

    def do_action(self, path, args):
        json_url = 'https://cdn.jsdelivr.net/gh/horrordor/bing-wallpaper/bing.json'
        img_list = json.loads(requests.get(json_url).text)
        if (not args):
            img_url = random.choice(img_list)[1] + '_1920x1080.jpg'
            self.send_response(302)
            self.send_header('Location', img_url)
            self.end_headers()
        else:
            args = parse_qs(args)
            # 图片尺寸
            if 'size' in args.keys():
                size = args['size'][0]
                if size not in [
                        '1920x1080',
                        '1366x768',
                        '1280x720',
                        '1024x768',
                        '800x600',
                        '800x480',
                        '768x1280',
                        '720x1280',
                        '640x480',
                        '480x800',
                        '400x240',
                        '320x240',
                        '240x320',
                ]:
                    self.send_404()
                    return
            else:
                size = '1920x1080'
            # 返回类型
            if 'type' in args.keys():
                type = args['type'][0]
                if type not in ['302', 'json']:
                    self.send_404()
                    return
            else:
                type = '302'
            # 是否返回图片信息
            if 'info' in args.keys():
                info = args['info'][0]
                if info not in ['true', 'false']:
                    self.send_404()
                    return
            else:
                info = 'false'
            # 随机范围
            if 'range' in args.keys():
                range = args['range'][0]
                try:
                    range = int(range)
                    if range < 1:
                        range = 1
                    elif range > len(img_list):
                        range = len(img_list)
                except:
                    self.send_404()
                    return
            else:
                range = len(img_list)

            img_item = random.choice(img_list[0:range])
            img_info = img_item[0]
            img_url = img_item[1] + '_' + size + '.jpg'

            if type == '302':
                self.send_response(302)
                self.send_header('Location', img_url)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                if info == 'true':
                    self.wfile.write(
                        json.dumps({
                            'info': img_info,
                            'url': img_url
                        },\
                        ensure_ascii=False).encode()
                    )
                else:
                    self.wfile.write(json.dumps({'url': img_url}).encode())
                self.wfile.close()

    def send_404(self):

        html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>404 Not Found</title>
    <style>
        <style type="text/css">
	    *{
            margin: 0;padding: 0;
        }
        div{
            width:150vw;
            height: 100vh;
            display: table-cell;
            vertical-align: middle;
            text-align: center;
            border:1px solid #000;
        }
</style>
    </style>
</head>

<body>
<div>
    <img src="https://http.cat/images/404.jpg"/>
</div>
</body>
</html>'''

        self.send_response(404)
        self.end_headers()
        self.wfile.write(html.encode())
        self.wfile.close()

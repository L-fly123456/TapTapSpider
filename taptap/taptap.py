import requests
from lxml import etree
import json
import re
from copy import deepcopy

def get_index():
    for i in range(1,3):
        index_url = 'https://www.taptap.com/ajax/top/developers?page=%d&total=30'%i
        try:
            response = json.loads(requests.get(index_url).text).get("data")
            yield response
        except requests.ConnectionError as e :
            print('请求失败',e.args)


def index_parse():
    '''
    解析索引页的数据
    :return:
    '''
    response = get_index()
    for res in response:
        html = etree.HTML(res['html'])
        item = {}
        name_list = html.xpath('//a[@class="developer-item"]')
        for name in name_list:
            # 公司名称
            item['name'] = name.xpath('./div[2]/div//span[1]/text()')[0]
            # 公司粉丝
            item['fans'] = name.xpath('./div[2]/div/span[1]/text()')[0].replace('粉丝数','')
            # 公司评分
            item['score'] = ''.join([i.replace('\n','').replace(' ','').replace('评分','')for i in name.xpath('./div[2]/div/span[2]/text()')])
            # 游戏数量
            item['game_num'] = name.xpath('./div[2]/p/span/text()')[0]
            # 详情页地址
            item['detail_url'] = name.xpath('./@href')[0]
            yield item

def detail_parse():
    '''
    详情页的数据
    :return:
    '''
    a = []
    item = index_parse()
    for i in item:
        response = requests.get(i['detail_url']).text
        html =etree.HTML(response)
        # 公司官网
        i['com_url'] = html.xpath('//div[@class="show-dev-info"]/span[1]/text()')
        # 公司介绍
        i['content_detail'] = [i.replace('\r','').replace('\n','')for i in html.xpath('//p[@class="content-detail"]/text()')]
        # 用正则匹配公司id
        id = int(re.match('https://www.taptap.com/developer/(\d+)',i['detail_url']).group(1))
        page=1
        while page:
            detail_url = 'https://www.taptap.com/ajax/developer/apps/%d?page=%d'%(id,page)
            print(detail_url)
            app_url_response = json.loads(requests.get(detail_url).text).get('data').get('html')
            xml = etree.HTML(app_url_response)
            # 公司的游戏名称
            com_game = xml.xpath('//div[@class="app-item-caption"]/a/@title')
            # 该爬虫的难点：
            if len(com_game)<36:
                for game in com_game:
                    a.append(game)
                break
            else:
                page+=1
                for game in com_game:
                    a.append(game)
        i['com_game'] = a
        print(i)


if __name__=="__main__":
    detail_parse()
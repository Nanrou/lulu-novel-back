from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from urllib.parse import urlparse, urlunparse
import os
import sys

from lxml import etree
import requests

from src.common.exception import OutTryException
from src.common.logger import CRAWLER_LOGGER

HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0',
}
MAX_TRY_AGAIN_TIME = 3
MAX_WORKERS = 5
TIMEOUT = 3
SLEEP_TIME = 3

# 最小单位
Item = namedtuple('Item', ['url', 'rule'])
DetailItem = namedtuple('DetailItem', ['url', 'detail'])


class Crawler:
    def __init__(self, items: list, debug=False):
        self.items = items
        self.debug = debug

    def _scrap(self):
        res = {}
        with requests.Session() as session:
            session.headers.update(HEADER)
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                url_mapper = {
                    executor.submit(self._thread_scrap, item, session): item.url
                    for item in self.items
                }
                for future in as_completed(url_mapper):
                    _url = url_mapper[future]
                    try:
                        res[_url] = future.result()
                        if self.debug:
                            CRAWLER_LOGGER.debug('working~ {}/{}'.format(len(res), len(self.items)))
                    except OutTryException:
                        CRAWLER_LOGGER.warning('超过重试次数 {}'.format(_url))
                    except Exception as exc:
                        CRAWLER_LOGGER.warning((exc, '最外层: ', _url))
        return res

    def _thread_scrap(self, item, session):
        response = self._request(item.url, session)
        return self._fetch_static_content(self.transform2utf8(response), item)

    @staticmethod
    def _fetch_static_content(content, item):
        body = etree.HTML(content)
        scrape_res = {}
        fail_time = 0
        for k, v in item.rule.items():
            try:
                if v is None:
                    scrape_res[k] = None
                    continue
                _value = body.xpath('string(' + v + ')')  # string(rule)
                if _value:
                    scrape_res[k] = _value
                else:
                    scrape_res[k] = None
                    CRAWLER_LOGGER.info('{} 的 {} 部分规则有问题'.format(item.url, k))
                    fail_time += 1
            except Exception as exc:  # 后面可以看一下需要捕捉什么异常
                CRAWLER_LOGGER.warning(('In fetch: ', exc))
                fail_time += 1
        if fail_time > 3:
            CRAWLER_LOGGER.warning('提取数据失败 {}'.format(item.url))
        else:
            return DetailItem(url=item.url, detail=scrape_res)

    @staticmethod
    def _request(url, session=None, extra_cookie=None):
        """ 单独的请求函数 """
        max_try_again_time = MAX_TRY_AGAIN_TIME
        if session and extra_cookie:
            session.cookies = extra_cookie
        while max_try_again_time:
            try:
                if session:
                    resp = session.get(url, timeout=TIMEOUT)
                else:
                    resp = requests.get(url, headers=HEADER, timeout=TIMEOUT)
                if resp.status_code == 200:
                    return resp
                else:
                    max_try_again_time -= 1
            except requests.Timeout:
                max_try_again_time -= 1
            else:
                raise OutTryException

    @classmethod
    def transform2utf8(cls, resp):
        """ 转换编码 """
        if resp.encoding == 'utf-8':
            return resp.text
        try:
            return resp.content.decode('utf-8')  # 先猜文档本身是utf8，只是没从头部识别出来
        except UnicodeDecodeError:
            return resp.content.decode('gbk').encode('utf-8').decode('utf-8')


if __name__ == '__main__':
    pass

import collections
import datetime
from collections import namedtuple
import logging

import bs4
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('zalando')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)


class ShopParser(self):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                        'Chrome/98.0.4758.102 Safari/537.36'
        }
        self.result = []

    def get_page(self, page : int = None):
        params = {
            'order' : 'activation_date',
            'desc' : '',
            'price_from' : '9'
        }
        if page and page > 1:
            params['p'] = page

        url = 'https://en.zalando.de/sweatshirts-hoodies-men/'
        r = self.session.get(url, params=params)
        r = self.raise_for_status()
        return r.text


    def parse_page(self, text : str ):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.kpgVnb.w8MdNG.cYylcv.QylWsg._75qWlu.iOzucJ.JT3_zV.DvypSJ')
        for block in container:
            self.parse_block(block=block)


    def parse_block(self, block):
        logger.info(block)
        logger.info('=' * 100)

        url_block = block.selections('a._LM.JT3_zV.CKDt_l.LyRfpJ')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no url')
            return

        name_block = block.select_one('div.hPWzFB')
        if not name_block:
            logger.error(f'no name_block on {url}')
            return

        brand_name = block.select_one('span.u-6V88.ka2E9k.uMhVZi.FxZV-M.Kq1JPK.pVrzNP.ZkIJC-.r9BRio.qXofat.EKabf7.nBq1-s._2MyPg2')
        if not brand_name:
            logger.error(f'no brand_name {url}')
            return

        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = block.select_one('h3.u-6V88.ka2E9k.uMhVZi.FxZV-M._6yVObe.pVrzNP.ZkIJC-.r9BRio.qXofat.EKabf7.nBq1-s._2MyPg2')
        if not goods_name:
            logger.error(f'no goods_name {url}')
            return

        goods_name = goods_name.text
        goods_name = goods_name.replace('/', '').strip()


        goods_image = block.select_one('img._6yVObe.u-6V88.ka2E9k.uMhVZi.FxZV-M._2Pvyxl.JT3_zV.EKabf7.mo6ZnF._1RurXL._7ZONEy')
        if not goods_image:
            logger.error(f'no goods_image {url}')
            return

        goods_image = goods_image.text
        goods_image = goods_image.replace('/', '').strip()

        self.result.append(ParseResult(
            url = url,
            brand_name = brand_name,
            goods_name = goods_name,
            goods_image = goods_image,
        ))
        logger.debug('=' * 100)

    def run(self):
        text = self.get_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')



import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PAGE_PARAMETER = '?PG='

def init():
    # search_index()
    search_detail()

def search_index():

    csv = pd.read_csv('tabelog_index.csv', sep=',', encoding='utf-8', index_col=False, header=None)

    csv = csv.drop(csv.index[[0, 1]])

    lines = csv.values
    for line in lines:
        prefecture = line[2]
        area = line[3]
        total_count = line[4]
        endpoint = line[5]
        parameter = line[6]
        pages = page_count(total_count)

        for page in range(0, pages):
            page = page + 1
            url = endpoint + PAGE_PARAMETER + str(page) + parameter
            print(url)
            time.sleep(2)
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            main_logic(soup)
            if page != pages:
                continue

        # print('完了')

def main_logic(soup):
    detail_links = soup.find_all("a", {"class": "list-rst__rst-name-target"})
    detail_urls = get_detail_urls(detail_links)
    to_write_detail_csv(detail_urls)
    return

def page_count(total):
    total = int(total)
    pages = total // 20
    if 0 < total % 20:
        pages += 1
    return pages

def get_detail_urls(detail_links):
    urls = []
    for i in range(len(detail_links)):
        detail_link = detail_links[i].get("href")
        urls.append(detail_link)
    return urls

def to_write_detail_csv(urls):
    df = pd.DataFrame(urls, columns=['url'])
    df.to_csv('detail.csv', mode='a', header=False, index=False)


def search_detail():

    csv = pd.read_csv('detail.csv', sep=',', encoding='utf-8', index_col=False, header=None)
    urls = list(csv[0])

    for index in range(len(urls)):

        url = urls[index]
        res = requests.get(url)
        time.sleep(3)
        soup = BeautifulSoup(res.text, 'html.parser')

        print(url)

        columns = ['店名', 'ジャンル', '予約お問い合わせ', '住所', '営業時間・定休日', '予算', '口コミ予算', '席数', '利用シーン', 'ロケーション', '電話番号', 'ホームページ', 'Facebook', 'Twitter', 'Instagram', 'オープン日', '備考', 'お店のPR']
        dic = {
            '店名': '', 
            'ジャンル': '', 
            '住所': '', 
            '営業時間・定休日': '', 
            '予算': '',
            '口コミ予算': '', 
            '席数': '', 
            '利用シーン': '', 
            'ロケーション': '',
            '電話番号': '', 
            'ホームページ': '', 
            'Facebook': '', 
            'Twitter': '', 
            'Instagram': '', 
            'オープン日': '', 
            '備考': '', 
            'お店のPR': ''
        }
        table_titles = soup.find_all('h4', {'class': 'rstinfo-table__title'})
        tables = soup.find_all('table', {"class": 'c-table'})
        for table_index in range(len(tables)):
            title = table_titles[table_index].getText()
            if title == '店舗基本情報':
                base_table = tables[table_index]
                base_table_rows = base_table.find_all("tr")
                for base_table_row in base_table_rows:
                    base_table_th = base_table_row.find('th').getText()
                    base_table_td = base_table_row.find('td').getText()
                    if base_table_th == '店名':
                        dic['店名'] = base_table_td.strip().replace(',','')
                    elif base_table_th == 'ジャンル':
                        dic['ジャンル'] = base_table_td.strip().replace(',','')
                    elif base_table_th == '住所':
                        dic['住所'] = base_table_td.strip().replace(',','')
                    elif base_table_th == '営業時間・定休日':
                        dic['営業時間・定休日'] =  base_table_td.replace(',','')
                    elif base_table_th == '予算':
                        dic['予算'] = base_table_td.replace(',','')
                    elif base_table_th == '予算（口コミ集計）':
                        dic['口コミ予算'] = base_table_td.replace(',','')
            elif title == '席・設備':
                facility_table = tables[table_index]
                facility_table_rows = facility_table.find_all("tr")
                for facility_table_row in facility_table_rows:
                    facility_table_th = facility_table_row.find('th').getText()
                    facility_table_td = facility_table_row.find('td').getText()
                    if facility_table_th == '席数':
                        dic['席数'] = facility_table_td.strip().replace(',','')
            elif title == '特徴・関連情報':
                feature_table = tables[table_index]
                feature_table_rows = feature_table.find_all("tr")
                for feature_table_row in feature_table_rows:
                    feature_table_th = feature_table_row.find('th').getText()
                    feature_table_td = feature_table_row.find('td')
                    if feature_table_th == '利用シーン':
                        use_scene = feature_table_td.find('a')
                        if use_scene is not None:
                            dic['利用シーン'] = use_scene.getText().strip().replace(',','')
                    elif feature_table_th == 'ロケーション':
                        dic['ロケーション'] = feature_table_td.getText().strip().replace(',','')
                    elif feature_table_th == '電話番号':
                        dic['電話番号'] = feature_table_td.find('strong', {"class": "rstinfo-table__tel-num"}).getText().strip()
                    elif feature_table_th == 'ホームページ':
                        dic['ホームページ'] = feature_table_td.find('p', {"class": "homepage"}).find_next().get('href')
                    elif feature_table_th == '公式アカウント':
                        facebook = feature_table_td.find('a', {"class": "rstinfo-sns-link rstinfo-sns-facebook"})
                        if facebook is not None:
                            dic['Facebook'] = facebook.get('href')
                        instagram = feature_table_td.find('a', {"class": "rstinfo-sns-link rstinfo-sns-instagram"})
                        if instagram is not None:
                            dic['Instagram'] = instagram.get('href')
                        twitter = feature_table_td.find('a', {"class": "rstinfo-sns-link rstinfo-sns-twitter"})
                        if twitter is not None:
                            dic['Twitter'] = twitter.get('href')
                    elif feature_table_th == 'オープン日': 
                        dic['オープン日'] = feature_table_td.find('p', {"class": "rstinfo-opened-date"}).getText().strip()
                    elif feature_table_th == '備考':
                        dic['備考'] = feature_table_td.getText().strip().replace(',','')
                    elif feature_table_th == 'お店のPR':
                        dic['お店のPR'] = feature_table_td.getText().strip().replace(',','')
        to_write_list_csv(columns, dic, index)

def to_write_list_csv(columns, dic, index):
    df = pd.DataFrame([dic], columns=columns)
    df.to_csv('list.csv', mode='a', header=False)

if __name__ == '__main__':
    init()
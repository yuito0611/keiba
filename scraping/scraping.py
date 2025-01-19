import traceback
import urllib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tqdm.notebook import tqdm
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import re
import random
from bs4 import BeautifulSoup


BASE_URL = "https://db.netkeiba.com/race/"



"""
スクレイピングする関数をまとめたモジュール

"""

def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # 確認したユーザーエージェントに置換
    }
    return urllib.request.Request(url,None,headers)

def scrape_kaisai_date(from_: str, to_: str) -> list[str]:
    """
    from_とto_をyyyy-mmの形で指定すると、間の開催日一覧を取得する関数
    """
    kaisai_date_list = []
    for date in tqdm(pd.date_range(from_, to_, freq="MS")):
        year = date.year
        month = date.month
        url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
        req = make_request(url)
        html = urllib.request.urlopen(req).read()  # スクレイピング

        time.sleep(2)  # 絶対忘れないように
        soup = BeautifulSoup(html, "lxml")
        a_list = soup.find("table", class_="Calendar_Table").find_all("a")
        for a in a_list:
            kaisai_date = re.findall(r"kaisai_date=(\d{8})", a["href"])[0]
            kaisai_date_list.append(kaisai_date)
    return kaisai_date_list


def scrape_race_id_list(kaisai_date_list: list[str]) -> list[str]:
    """
    開催日（yyyymmdd形式）をリストで入れると、レースid一覧が返ってくる関数。
    """
    options = Options()
    # ヘッドレスモード（バックグラウンド）で起動
    options.add_argument("--headless")
    # その他のクラッシュ対策
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    race_id_list = []

    with webdriver.Chrome(options=options) as driver:
        # 要素を取得できない時、最大10秒待つ
        driver.implicitly_wait(10)
        for kaisai_date in tqdm(kaisai_date_list):
            url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"

            try:
                driver.get(url)
                time.sleep(1)
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except:
                print(f"stopped at {url}")
                print(traceback.format_exc())
                break
    return race_id_list

  


def scrape_race_result(race_id):
    
    """
    指定されたレースIDのレース結果をスクレイピングする関数。
    ※https://db.netkeiba.com/?pid=race_topのデータベースに保存されている情報が対象のため直近のデータは取得できない

    Parameters:
    race_id (str): レースID

    Returns:
    list: 指定されたレースの結果データ
    """
    req = make_request(BASE_URL+race_id)
    try:
        html = urllib.request.urlopen(req).read() 
    #失敗したら10秒待機してリトライする
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)  # 10秒待機
        html = urllib.request.urlopen(req).read() 

    soup = BeautifulSoup(html, "lxml")  
    soup_span = soup.find_all("span")

    # テーブルを指定
    main_table = soup.find("table", {"class": "race_table_01 nk_tb_common"})

    # テーブル内の全ての行を取得
    main_rows = main_table.find_all("tr")

    race_data = []
    for i, row in enumerate(main_rows[1:], start=1):# ヘッダ行をスキップ
        cols = row.find_all("td")
        #走破時間
        runtime=''
        try:
            runtime= cols[7].text.strip()
        except IndexError:
            runtime = ''
        soup_nowrap = soup.find_all("td",nowrap="nowrap",class_=None)
        #通過順
        pas = ''
        try:
            pas = str(cols[10].text.strip())
        except:
            pas = ''
        weight = 0
        weight_dif = 0
        #体重
        var = cols[14].text.strip()
        try:
            weight = int(var.split("(")[0])
            weight_dif = int(var.split("(")[1][0:-1])
        except ValueError:
            weight = 0
            weight_dif = 0
        weight = weight
        weight_dif = weight_dif
        #上がり
        last = ''
        try:
            last = cols[11].text.strip()
        except IndexError:
            last = ''
        #人気
        pop = ''
        try:
            pop = cols[13].text.strip()
        except IndexError:
            pop = ''
        
        #レースの情報
        try:
            var = soup_span[8]
            sur=str(var).split("/")[0].split(">")[1][0]
            rou=str(var).split("/")[0].split(">")[1][1]
            dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
            con=str(var).split("/")[2].split(":")[1][1]
            wed=str(var).split("/")[1].split(":")[1][1]
        except IndexError:
            try:
                var = soup_span[7]
                sur=str(var).split("/")[0].split(">")[1][0]
                rou=str(var).split("/")[0].split(">")[1][1]
                dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                con=str(var).split("/")[2].split(":")[1][1]
                wed=str(var).split("/")[1].split(":")[1][1]
            except IndexError:
                var = soup_span[6]
                sur=str(var).split("/")[0].split(">")[1][0]
                rou=str(var).split("/")[0].split(">")[1][1]
                dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                con=str(var).split("/")[2].split(":")[1][1]
                wed=str(var).split("/")[1].split(":")[1][1]
        soup_smalltxt = soup.find_all("p",class_="smalltxt")
        detail=str(soup_smalltxt).split(">")[1].split(" ")[1]
        date=str(soup_smalltxt).split(">")[1].split(" ")[0]
        clas=str(soup_smalltxt).split(">")[1].split(" ")[2].replace(u'\xa0', u' ').split(" ")[0]
        title=str(soup.find_all("h1")[1]).split(">")[1].split("<")[0].strip()

        race_data.append([
            race_id,#レースID
            cols[0].text.strip(),#着順
            cols[1].text.strip(),#馬番
            cols[2].text.strip(),#枠番
            cols[3].text.strip(),#馬の名前
            cols[4].text.strip()[0],#性
            cols[4].text.strip()[1],#齢
            cols[5].text.strip(),#斤量
            re.findall(r"/(\d+)", cols[3].a.get("href"))[0],#馬のID
            cols[6].text.strip(),#騎手の名前
            re.findall(r"/(\d+)", cols[6].a.get("href"))[0],#騎手のID
            runtime,#走破時間
            pas,#通過順
            last,#上がり
            cols[12].text.strip(),#オッズ,
            pop,#人気
            weight,#体重
            weight_dif,#体重変化
            title,#レース名
            date,#日付
            detail,#開催回詳細
            clas,#クラス
            sur,#芝かダートか
            dis,#距離
            rou,#回り
            con,#馬場状態
            wed,#天気
            race_id[4:6],#競馬場ID
            soup.find("ul",class_="race_place").find("a",class_="active").text #競馬場名
        ])
        
    return race_data

def scrape_race_refund(race_id):
    
    """
    指定されたレースIDの払い戻し金額をスクレイピングする関数。
    ※https://db.netkeiba.com/?pid=race_topのデータベースに保存されている情報が対象のため直近のデータは取得できない

    Parameters:
    race_id (str): レースID

    Returns:
    dataFrame: 指定されたレースの払い戻し金額のデータ
    """
    req = make_request(BASE_URL+race_id)
    req = make_request(BASE_URL+race_id)
    try:
        html = urllib.request.urlopen(req).read() 
    #失敗したら10秒待機してリトライする
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)  # 10秒待機
        html = urllib.request.urlopen(req).read() 

    soup = BeautifulSoup(html, "lxml")  

    # テーブルを指定
    refund_tables = soup.find_all("table", {"class": "pay_table_01"})

    result = []
    for table in refund_tables:
        # テーブル内の全ての行を取得
        rows = table.find_all("tr")
        for row in rows:
            _res = [race_id]
            # テーブル内の全てのセルを取得        
            _res.append(row.find("th").text)
            # print(row.find("th").text)
            cells = row.find_all("td")
            for cell in cells:
                v=re.sub('(<|</)td.*?>','',str(cell).replace('<br/>', ' '))
                _res.append(v)
            result.append(_res)

    return pd.DataFrame(result)
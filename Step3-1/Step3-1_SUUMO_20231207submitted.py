from bs4 import BeautifulSoup
import requests
from time import sleep
import pandas as pd

# 変数urlにSUUMOのURLを格納（文京区）
url = "https://suumo.jp/chintai/tokyo/sc_bunkyo/?page={}"

# 変数d_listに空のリストを準備
d_list = []

# while文でループ
i = 1
while True:
    # 変数target_urlにアクセス先のURLを格納する
    target_url = url.format(i)

    # taget_urlへのアクセス結果を変数rに格納
    r = requests.get(target_url)

    # 0.3秒秒空ける
    sleep(0.3)
    # 取得結果をsoupに格納
    soup = BeautifulSoup(r.text, 'html.parser')

    # ページ内の全ての情報を取得する/class = cassetteitem のdivタグを取得してcontentsに格納
    contents = soup.find_all("div", class_="cassetteitem")

    # 各物件情報をforループで取得する
    for content in contents:
        # 建物情報（= div class = cassetteitem_detail)をdetailに格納
        detail = content.find("div", class_="cassetteitem-detail")
        # 部屋情報（= table class = cassetteitem_other)をdetailに格納
        table = content.find("table", class_="cassetteitem_other")
        # 変数detailから建物情報を取得
        # 物件名
        title = detail.find("div", class_="cassetteitem_content-title").text
        # 住所
        address = detail.find("li", class_="cassetteitem_detail-col1").text
        # アクセス
        access = detail.find("li", class_="cassetteitem_detail-col2").text
        # 築年数, 階建
        outline = detail.find("li", class_="cassetteitem_detail-col3").text

        # 変数tableから部屋情報を取得
        tr_tags = table.find_all('tr', class_="js-cassette_link")
        # forループでtr_tagsから部屋情報を取得
        for tr_tag in tr_tags:
            # trタグの中にtdタグが9個。3番目から6番目に必要な情報がある。
            # 階数, 賃料/管理費, 敷金/礼金, 間取り/占有面積
            floor, price, fisrt_fee, capacity = tr_tag.find_all("td")[2:6]
            # priceをfeeとmanagement feeにunpack
            fee, management_fee = price.find_all("li")
            # 同様にfirst fee
            deposit, gratuity = fisrt_fee.find_all("li")
            # 同様にcapacity
            madori, menseki = capacity.find_all("li")
            # 変数dに取得した情報を辞書として格納する（部屋情報はまだtextにしていないからここで）
            d = {
                "title" : title,
                "address" : address,
                "access" : access,
                "outline" : outline,
                "floor" : floor.text,
                "fee" : fee.text,
                "management_fee": management_fee.text,
                "deposit" : deposit.text,
                "gratuity" : gratuity.text,
                "madori" : madori.text,
                "menseki" : menseki.text
            }
            # 取得した辞書をd_listに格納
            d_list.append(d)

    # 次のページが存在しない場合はループ終了
    if not contents:
        break
    # 次のページへ
    i += 1

# d_listをデータフレームに格納
df = pd.DataFrame(d_list)

# 加工しやすいように円や万円を削除してfloatに変換
# fee, deposit gratuityから「万円」を削除
df['fee'] = df['fee'].str.replace('万円', '')
df['deposit'] = df['deposit'].str.replace('万円', '')
df['gratuity'] = df['gratuity'].str.replace('万円', '')

# "-"をNaNに変換し、NaNを0に置き換え
df['deposit'] = pd.to_numeric(df['deposit'], errors='coerce').fillna(0).astype(float)
df['gratuity'] = pd.to_numeric(df['gratuity'], errors='coerce').fillna(0).astype(float)

# それぞれの数字に1,000を乗じて金額に書き換え
df['fee'] = pd.to_numeric(df['fee']) * 10000
df['deposit'] = pd.to_numeric(df['deposit']) * 10000
df['gratuity'] = pd.to_numeric(df["gratuity"]) * 10000

# management_feeから「円」を削除,「-」をゼロしてfloatに変換
df["management_fee"] = df["management_fee"].str.replace("円", "").str.replace("-", "0").astype(float)

# mensekiから「m2」を削除してfloatに変換
df["menseki"] = df["menseki"].str.replace("m2", "").astype(float)

# 「新築」を「築1年」に変換
df["outline"] = df["outline"].str.replace("新築", "築1年")

# outlineを築年数と総階数に分ける
df['age'] = df['outline'].str.extract(r'築(\d+)年').astype(float)
df['total_floor'] = df['outline'].str.extract(r'(\d+)階建').astype(float)

# 重複を削除（とりあえず重複はaddress, floor, fee, management_fee, madori, menseki, age, total_floorがすべて一致したものと定義）
df_unique = df.drop_duplicates(subset=['address', 'floor', 'fee', 'management_fee', 'madori', 'menseki', 'age', 'total_floor'])

# Googleスプレッドシートに格納
import gspread
from google.oauth2.service_account import Credentials

from dotenv import load_dotenv
import os
load_dotenv()

# GoogleSheetsAPI、GoogleDriveAPI、及び認証鍵の指定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# jsonファイル名指定
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Service Accountの認証情報を取得
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 認証情報を用いてGoogleSheetsにアクセス
gs = gspread.authorize(credentials)

# 対象のスプレッドシートとワークシートを指定
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
workbook = gs.open_by_key(SPREADSHEET_KEY)
worksheet = workbook.worksheet("シート1")

# DataFrameの値を文字列に変換
df_unique = df_unique.applymap(lambda x: str(x) if not pd.isnull(x) else "")

# "Floor" カラム内の各セルに対して str.strip() を適用して不要なスペースを削除
df_unique.loc[:, 'floor'] = df_unique['floor'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# DataFrameをリストに変換
values = [df_unique.columns.tolist()] + df_unique.values.tolist()

# スプレッドシートの1行目（A1セル）からデータを追加
worksheet.update("A1", values)
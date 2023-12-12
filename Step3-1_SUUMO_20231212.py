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
            # 階数, 賃料/管理費, 敷金/礼金, 間取り/占有面積, NA, NA, URL元
            floor, price, fisrt_fee, capacity, _, _, url_key = tr_tag.find_all("td")[2:9]
            # priceをfeeとmanagement feeにunpack
            fee, management_fee = price.find_all("li")
            # 同様にfirst fee
            deposit, gratuity = fisrt_fee.find_all("li")
            # 同様にcapacity
            madori, menseki = capacity.find_all("li")
            # 「詳細を見る」の物件詳細ページURLを取得
            get_url = url_key.find("a", class_="js-cassette_link_href")
            href = get_url.get('href')
            base_url = "https://suumo.jp"
            link = base_url+href

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
                "menseki" : menseki.text,
                "url" : link
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

# それぞれの数字に10,000を乗じて金額に書き換え
df['fee'] = pd.to_numeric(df['fee']) * 10000
df['deposit'] = pd.to_numeric(df['deposit']) * 10000
df['gratuity'] = pd.to_numeric(df["gratuity"]) * 10000

# management_feeから「円」を削除,「-」をゼロしてfloatに変換
df["management_fee"] = df["management_fee"].str.replace("円", "").str.replace("-", "0").astype(float)

# mensekiから「m2」を削除してfloatに変換
df["menseki"] = df["menseki"].str.replace("m2", "").astype(float)

# 「新築」を「築1年」に変換, 「平屋」を「1階建」に変換
df["outline"] = df["outline"].str.replace("新築", "築1年")
df["outline"] = df["outline"].str.replace("平屋", "1階建")

# outlineを築年数と総階数に分ける
df['age'] = df['outline'].str.extract(r'築(\d+)年').astype(float)
df['total_floor'] = df['outline'].str.extract(r'(\d+)階建').astype(float)

# 路線を分ける
access_split = df['access'].str.split("\n", expand=True)
for col in access_split.columns:
    df[f'access_{col}'] = access_split[col]
# access0,4に不要カラムができてしまうのでdrop
df = df.drop(columns=["access_0", "access_4"], axis=1)

# 「バス」,「都電」という文字列を含むデータを削除（アプリ対象地域ではバスや都バス以外の方が便利。かつペルソナのようなイケてる人はバスや都電は使わないということで、、）
for i in range(1, 4):
    col_prefix = f'access_{i}'
    df.loc[df[col_prefix].str.contains('バス|都電'), col_prefix] = ''

# アクセス情報（路線、最寄駅、徒歩）のカラム分ける（最大3つのアクセスが掲載されているのでそれぞれ）
for i in range(1, 4):
    col_prefix = f'access_{i}'
    route_col = f'route_{i}'
    station_col = f'station_{i}'
    time_col = f'time_{i}'

    df[[route_col, station_col, time_col]] = df[col_prefix].str.extract(r'(.+?)\s?/([^ ]+?)駅\s?(.+?)分')

    # 時間をfloatに
    df[time_col] = df[time_col].str[1:].astype(float)

    # 不要な列の削除
    df = df.drop(columns=col_prefix, axis=1)

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

# "Floor" カラム内の各セルに対して str.strip() を適用して不要なスペースを削除
df_unique.loc[:, 'floor'] = df_unique['floor'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# 空欄にゼロを格納
df_unique_filled = df_unique.fillna(0)

# DataFrameをリストに変換
values = [df_unique_filled.columns.tolist()] + df_unique_filled.values.tolist()

# スプレッドシートの1行目（A1セル）からデータを追加
worksheet.update("A1", values)
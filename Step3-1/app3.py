import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
import urllib
from streamlit_folium import st_folium
import folium
import urllib.parse

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

# スプレッドシートをDataFrameに取り込む
df = pd.DataFrame(worksheet.get_values()[1:], columns=worksheet.get_values()[0])

# 都市名から緯度と経度を取得する関数
def get_coordinates(address):
    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    s_quote = urllib.parse.quote(address)
    response = requests.get(makeUrl + s_quote)
    if response.json():
        lon, lat = response.json()[0]["geometry"]["coordinates"]
        return [lat, lon]
    else:
        return [None, None]

def filter_data(df, selected_line, selected_room, fee_range, time_range, age_range):
    # 路線で抽出
    df = df[df['route_1'].isin(selected_line)]
    # 間取りで抽出
    df = df[df['madori'].isin(selected_room)]

    # fee 列を整数型に変換
    df['fee'] = pd.to_numeric(df['fee'], errors='coerce')
    # 予算でフィルタリング
    df = df[df['fee'].between(fee_range[0], fee_range[1])]
    # time_1 列を整数型に変換
    df['time_1'] = pd.to_numeric(df['time_1'], errors='coerce')
    # 最寄駅からの時間でフィルタリング
    df = df[df['time_1'].between(time_range[0], time_range[1])]

    # age列を整数型に変換
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    # 最寄駅からの時間でフィルタリング
    df = df[df['age'].between(age_range[0], age_range[1])]
    #築年数も追加する
    return df


def main():

    # Streamlit関連
    st.title("文京区部屋探し")

    # 路線の選択⇒備忘：都営とかJR大文字問題とか、東京メトロとか消したい
    line_options = ["東京メトロ丸ノ内線", "東京メトロ南北線", "東京メトロ千代田線", "都営三田線", "都営大江戸線", "JR山手線", "JR総武線","その他"]
    selected_line = st.sidebar.multiselect("希望路線を選択してください", line_options)

    # 住所の選択
    address_options = ["大塚", "音羽", "春日", "小石川", "後楽", "小日向", "水道", "関口", "千石", "千駄木", "西片", "根津", "白山", "本駒込", "本郷", "向丘", "目白台", "弥生", "湯島"]
    selected_address = st.sidebar.multiselect("希望の住所を選択してください", address_options)

    # 間取の選択⇒選択しなんとかしないと
    room_options = ["ワンルーム", "1K", "1DK", "1SK", "1SDK", "1LDK", "1SLDK", "2K", "2DK","2LK", "2SK", "2LDK", "2SDK", "2SLDK", "3K", "3DK", "3SDK", "3LDK", "3SLDK", "4LD", "4LDK", "4SLDK", "5LDK", "その他"]
    selected_room = st.sidebar.multiselect("間取りを選択してください", room_options)

    # 家賃⇒管理費込みにしたい
    fee_range = st.sidebar.slider("家賃予算を設定してください", 0, 1000000, (0,1000000), 1000)

    # 最寄駅からの徒歩
    time_range = st.sidebar.slider("最寄駅から所要時間を設定してください", 0, 20, (0,20), 1)

    # 築年数
    age_range = st.sidebar.slider("希望の築年数を選択してください", 0, 50, (0,50), 5)
    # min_age, max_age = age_range

    # 検索ボタン
    if st.sidebar.button('検索'):
        # 選択された町名に基づいてデータをフィルタリング
        if selected_address:
            df_filtered_by_address = df[df['address'].str.contains('|'.join(selected_address))]
        else:
            df_filtered_by_address = df

        # その他のフィルターを適用
        filtered_df = filter_data(df_filtered_by_address, selected_line, selected_room, fee_range, time_range, age_range)

        # フィルタリングされたデータフレームのインデックスに名前を設定
        filtered_df.index.name = '物件No.'

        st.dataframe(filtered_df.reset_index()[['title', 'address', 'fee', "madori", "route_1", "time_1", "age"]], width=1500, height=500)

if __name__ == '__main__':
    main()

# Streamlitアプリの構築
# st.title("検索結果")
# 地点の住所
# address = '東京都文京区西片１'
# 緯度と経度を取得
# latitude, longitude = get_coordinates(address)
# データフレームを作成
# data = {'LAT': [latitude], 'LON': [longitude]}
# df_map = pd.DataFrame(data)
# 地図にプロット
# st.map(df_map)

# 条件に一致する行を抽出
# df2 = df[df['route_1'] == "都営三田線"].copy()

# df2を表示
# st.dataframe(df2)

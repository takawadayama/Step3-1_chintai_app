import streamlit as st
import pandas as pd
# import gspread
# from google.oauth2.service_account import Credentials
import requests
import urllib
from streamlit_folium import st_folium
import folium
import urllib.parse

from dotenv import load_dotenv
import os
load_dotenv()

#GoogleSheetsAPI、GoogleDriveAPI、及び認証鍵の指定
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# # jsonファイル名指定
# SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# # Service Accountの認証情報を取得
# credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# # 認証情報を用いてGoogleSheetsにアクセス
# gs = gspread.authorize(credentials)

# # 対象のスプレッドシートとワークシートを指定
# SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
# workbook = gs.open_by_key(SPREADSHEET_KEY)
# worksheet = workbook.worksheet("シート1")

# # スプレッドシートをDataFrameに取り込む
# df = pd.DataFrame(worksheet.get_values()[1:], columns=worksheet.get_values()[0])

# ファイルの絶対パスを取得
file_path = os.path.join(os.path.dirname(__file__), "suumo.csv")

# CSVファイルを読み込み
df = pd.read_csv(file_path)
# 新しいカラムを作成し、複数のカラムを結合
df['merged_route'] = df.apply(lambda row: f"{row['route_1']}_{row['route_2']}_{row['route_3']}", axis=1)

# 都市名から緯度と経度を取得する関数
# def get_coordinates(address):
#     makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
#     s_quote = urllib.parse.quote(address)
#     response = requests.get(makeUrl + s_quote)
#     if response.json():
#         lon, lat = response.json()[0]["geometry"]["coordinates"]
#         return [lat, lon]
#     else:
#         return [None, None]

def filter_data(df, selected_line, selected_room, max_fee, max_time, max_age):
    # 路線で抽出
    if selected_line is not None:
        if isinstance(selected_line, list):
        # selected_lineがリストの場合、merged_routeがその中のいずれかの文字列を含む行を抽出
            df = df[df['merged_route'].str.contains('|'.join(selected_line))]
        else:
        # selected_lineが文字列の場合、merged_routeがその文字列を含む行を抽出
            df = df[df['merged_route'].str.contains(selected_line)]
    # 間取りで抽出
    df = df[df['madori'].isin([selected_room])]

    # fee 列を整数型に変換
    df['fee'] = pd.to_numeric(df['fee'], errors='coerce')
    # 予算でフィルタリング
    df = df[df['fee'] <= max_fee]
    # time_1 列を整数型に変換
    df['time_1'] = pd.to_numeric(df['time_1'], errors='coerce')
    # 最寄駅からの時間でフィルタリング
    df = df[df['time_1'] <= max_time]

    # age列を整数型に変換
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    # 築年数でフィルタリング
    df = df[df['age'] <= max_age]

    # 築年数も追加する
    return df


def main():
    # Streamlit関連
    st.title("文京区楽々部屋探し")

    # 路線の選択
    # line_options = ["東京メトロ丸ノ内線", "東京メトロ南北線", "東京メトロ千代田線", "都営三田線", "都営大江戸線", "JR山手線", "JR総武線", "その他"]
    # selected_line = st.sidebar.multiselect("希望路線を選択してください", line_options)

    # 勤務地の設定
    work_location = ["丸の内", "銀座", "大手町", "六本木", "渋谷", "新宿"]
    # 勤務地と路線の対応関係を表す辞書を作成
    location_to_line = {
        "丸の内": "東京メトロ丸ノ内線",
        "銀座": "東京メトロ丸ノ内線",
        "大手町": "都営三田線",
        "六本木": "東京メトロ南北線",
        "渋谷": "東京メトロ千代田線",
        "新宿": "都営大江戸線",
        "池袋": "東京メトロ丸ノ内線"
    }
    # 選択された勤務地に対応する路線を取得
    selected_location = st.sidebar.radio("勤務地を選択してください", work_location, horizontal=True)
    # 選択された勤務地に対応する路線を取得し、表示
    selected_line = location_to_line.get(selected_location, "該当する路線がありません")

    # 家族構成
    family =  ["1人暮らし", "夫婦", "3人家族", "4人家族", "5人以上"]
    # 家族構成と間取りの対応関係を表す辞書を作成
    family_to_madori = {
        "1人暮らし": "1K",
        "夫婦": "1LDK",
        "3人家族": "2LDK",
        "4人家族": "3LDK",
        "5人以上": "4LDK"
        }
    # 家族構成をラジオボタンで選択
    selected_family = st.sidebar.radio("家族構成を選択してください", family, horizontal=True)
    # 選択された家族構成に対応する間取りを取得し、表示
    selected_room = family_to_madori.get(selected_family, "該当がありません")


    # 世帯年収の入力
    income = st.sidebar.number_input("単位：万円",0)
    #income_list = ["～600万円", "600万円～800万円", "800万円～1,000万円", "1,000万円～"]
    #income = st.sidebar.radio("世帯年収を選択してください", income_list, horizontal=True)
    # 家賃にどれぐらい使うか
    budget = st.sidebar.radio("家賃の考え方に近いものを選択してください",("無限", "多少無理してでも良い", "一般的な水準", "足るを知る", "節約志向"), horizontal=True)
    budget_to_fee = {
        "無限": 1,
        "多少無理してでも良い": 0.5,
        "一般的な水準": 0.3,
        "足るを知る": 0.25,
        "節約志向": 0.15
        }
    # 選択された感かが得方に対応する家賃条件
    budget_ratio = budget_to_fee.get(budget, "該当がありません")
    max_fee = income*10000*budget_ratio/12

    # address_options = ["大塚", "音羽", "春日", "小石川", "後楽", "小日向", "水道", "関口", "千石", "千駄木", "西片", "根津", "白山", "本駒込", "本郷", "向丘", "目白台", "弥生", "湯島"]
    # イメージ
    image = ["#閑静", "#野球好き", "#買い物が便利", "#神楽坂でも飲みたい", "#文京区なのに猥雑", "#住んでるだけで頭良さそう", "#高級住宅街","#大きい公園がある", "#下町", "#通勤は敢えて坂道"]
    # イメージと住所の対応
    image_to_address = {
        "#閑静": "小日向",
        "#野球好き": "後楽",
        "#買い物が便利": "小石川",
        "#神楽坂でも飲みたい": "水道",
        "#文京区なのに猥雑": "湯島",
        "#住んでるだけで頭良さそう": "本郷",
        "#高級住宅街": "西片",
        "#大きい公園がある": "本駒込",
        "#下町": "千駄木",
        "#通勤は敢えて坂道": "春日"
    }
    # 選択されたイメージに対応する住所を取得
    selected_image = st.sidebar.multiselect("希望のイメージを選択してください", image)
    # selected_image が文字列ならば、リストに変換
    selected_address = [image_to_address[loc] for loc in selected_image] if selected_image else None

    # 最寄駅からの徒歩
    if st.sidebar.checkbox("駅近物件"):
        max_time = 5
    else:
        max_time = 100

    # 築年数
    if st.sidebar.checkbox("築浅"):
        max_age = 10
    else:
        max_age = 100

    st.write("おすすめ路線：", selected_line)
    st.write("おすすめ間取り：", selected_room)
    st.write("家賃上限：", max_fee/10000, "万円")
    if selected_address:
        st.write("おすすめの町：", ", ".join(selected_address))

    # 検索ボタン
    if st.sidebar.button('検索'):
        # 選択された町名に基づいてデータをフィルタリング
        if selected_address:
            df_filtered_by_address = df[df['address'].str.contains('|'.join(selected_address))]
        else:
            df_filtered_by_address = df

        # その他のフィルターを適用
        filtered_df = filter_data(df_filtered_by_address, selected_line, selected_room, max_fee, max_time, max_age)

        # カラム名変更
        new_column_names = ['タイトル', '住所', 'アクセス', '建物概要', '階数', '家賃', '管理費', '敷金', '礼金', '間取り', '面積', '詳細URL', '築年数', '何階建て', '路線', '最寄駅', '駅徒歩', '路線2', '駅2', '徒歩2', '路線3', '駅3', '徒歩3', '検索用']
        filtered_df.columns = new_column_names
        # 家賃で降順にソート
        sorted_df = filtered_df.sort_values(by='家賃', ascending=False)
        # 駅徒歩、築年数 列の各行に「分、年」を追加
        sorted_df['駅徒歩'] = sorted_df['駅徒歩'].astype(str) + '分'
        sorted_df['築年数'] = sorted_df['築年数'].astype(str) + '年'

        st.dataframe(sorted_df.reset_index()[['タイトル', '住所',"築年数", "間取り", "家賃", "管理費", "最寄駅", "駅徒歩", "詳細URL"]], width=1500, height=500)
        # 詳細URLをリンク化
        for index, row in sorted_df.iterrows():
            st.write(f"{row['タイトル']} - [SUUMO詳細ページへ]({row['詳細URL']})")

if __name__ == '__main__':
    main()
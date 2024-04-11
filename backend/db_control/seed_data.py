# seed_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mymodels import Store, Brand, Manufacturer, Base, User, Post, Photo
import pandas as pd
import numpy as np
import re

engine = create_engine('sqlite:///beerlog.db')
Base.metadata.bind = engine

# テーブルを作成
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# CSV→dfに変換
csv_file_path = '東京都樽生母体_tw.csv'  # CSVファイルのパス
df = pd.read_csv(csv_file_path, encoding='cp932', dtype={'store_phonenumber': str})  
df['store_phonenumber'] = df['store_phonenumber'].replace({np.nan: ''})  # np.nan を空文字列で置き換える

# 画像ファイルを読み込んでバイナリデータに変換
with open('20240308191826_img_4311_2.jpg', 'rb') as f:
    profile_data = f.read()

with open('beer_photo1.jpg', 'rb') as f:
    photo1_data = f.read()

with open('beer_photo2.jpg', 'rb') as f:
    photo2_data = f.read()

with open('beer_photo3.jpg', 'rb') as f:
    photo3_data = f.read()

for _, row in df.iterrows():
    store = Store(
        store_name=row['store_name'],
        store_address=row['store_address'],
        store_phonenumber=row.get('store_phonenumber', '')  
    )
    session.add(store)
    session.flush()  # IDを取得するためにflushする

    # 新しいブランドを追加
    brand_name = row['brand_name']
    # 正規表現でブランド名だけを抽出
    match = re.search(r'[A-Z]{1}\d{3}(.+?)\d+L', brand_name)
    if match:
        brand_name = match.group(1).strip()
    brand = Brand(store_id=store.store_id, brand_name=brand_name)
    session.add(brand)
    
# ダミーデータの作成
user1 = User(user_id='user1', user_name='よっちゃん', user_mail="yo.kishimoto99@gmail.com", user_password='sapporolove', user_picture=profile_data, user_profile='ソラチを愛してやまない29歳', age=29, gender='male')
user2 = User(user_id='user2', user_name='テストユーザー2', user_mail="test2@example.com", user_password='password2', user_picture=None, user_profile='テストユーザー2のプロフィール', age=30, gender='female')

post1 = Post(users=user1, review='おいしかった～', rating=5)
post2 = Post(users=user1, review='微妙っす・・', rating=3)
post3 = Post(users=user2, review='まずかった', rating=2)

photo1 = Photo(posts=post1, photo_data=photo1_data)
photo2 = Photo(posts=post1, photo_data=photo2_data)
photo3 = Photo(posts=post3, photo_data=photo3_data)

manufacturer1 = Manufacturer(manufacturer_name='SAPP0RO')

session.add_all([user1, user2, post1, post2, post3, photo1, photo2, photo3, manufacturer1])
session.commit()
session.close()
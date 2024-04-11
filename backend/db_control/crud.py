# uname() error回避
import platform
print("platform", platform.uname())
 
from sqlalchemy import create_engine, insert, delete, update, select
import sqlalchemy
from sqlalchemy.orm import sessionmaker, joinedload
import json
import pandas as pd

from db_control.connect import engine
from db_control.mymodels import Users, Post, Photo
import base64
 

def myinsert(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mymodel).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
 
    # セッションを閉じる
    session.close()
    return "inserted"
 
def myselect(mymodel, user_id):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(mymodel).filter(mymodel.user_id == user_id)
    
    try:
        # トランザクションを開始
        with session.begin():
            # Usersのデータを取得し、関連するPostsとPhotosをプリロードする
            result = query.options(
                joinedload(Users.posts).joinedload(Post.photos)
            ).first()
            
            if result is None:
                return None
            
            # 結果をオブジェクトから辞書に変換
            result_dict = {
                "user_id": result.user_id,
                "user_name": result.user_name,
                "user_mail": result.user_mail,
                "user_password": result.user_password,  # 追加: user_password を含める
                "user_profile": result.user_profile,
                "age": result.age,
                "gender": result.gender,
                "user_picture": base64.b64encode(result.user_picture).decode() if result.user_picture else None,
                "posts": [
                    {
                        "post_id": post.post_id,
                        "review": post.review,
                        "rating": post.rating,
                        "photos": [
                            base64.b64encode(photo.photo_data).decode() if photo.photo_data else None
                            for photo in post.photos
                        ]
                    }
                    for post in result.posts
                ]
            }
            
            return result_dict
            
    except sqlalchemy.exc.IntegrityError as e:
        print(f"一意制約違反により、取得に失敗しました: {e}")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    finally:
        session.close()

def myupdate(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = values.pop("user_id")
 
    query = update(mymodel).where(mymodel.user_id==user_id).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
    # セッションを閉じる
    session.close()
    return "put"

def mydelete(mymodel, user_id):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = delete(mymodel).where(mymodel.user_id==user_id)
    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
 
    # セッションを閉じる
    session.close()
    return user_id + " is deleted"
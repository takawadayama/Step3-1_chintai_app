<<<<<<< HEAD
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, Text

Base = declarative_base()

# ユーザーテーブル定義
class Users(Base):
    __tablename__ = 'users'
    user_id = Column(String(255), primary_key=True)
    user_name = Column(String(50), nullable=False)
    user_mail = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    user_picture = Column(LargeBinary)  # BLOB型でプロフィール画像を格納
    user_profile = Column(Text)  # ユーザーのプロフィール文
    age = Column(Integer)
    gender = Column(String(50))

    # UserとPostは1対多の関係
    posts = relationship('Post', back_populates='users')

# POSTテーブル定義
class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    review = Column(Text)  # レビューコメント
    rating = Column(Integer)  # 評価は1から5まで
    photos = relationship('Photo', back_populates='posts')

    # Postは特定のUserに属する
    users = relationship('Users', back_populates='posts')

    # PostとPhotoは1対多の関係
    photos = relationship('Photo', back_populates='posts')

# 写真テーブル定義
class Photo(Base):
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    photo_data = Column(LargeBinary)
    posts = relationship('Post', back_populates='photos')

    # PhotoはPostに属する
    posts = relationship('Post', back_populates='photos')
    
    
# Userモデルに'posts'関係を追加
    Users.posts = relationship('Post', order_by=Post.post_id, back_populates='users')
    
# Store テーブル定義
class Store(Base):
    __tablename__ = 'stores'
    store_id = Column(Integer, Sequence('store_id_seq'), primary_key=True, autoincrement=True)
    store_name = Column(String(255), nullable=False)
    store_address = Column(String(255), nullable=False)
    store_phonenumber = Column(String(255), nullable=True)

# Brand テーブル定義
class Brand(Base):
    __tablename__ = 'brands'
    brand_id = Column(Integer, Sequence('brand_id_seq'), primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('stores.store_id'), nullable=False)
    brand_name = Column(String(255), nullable=False)

# Manufacturer テーブル定義
class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    manufacturer_id = Column(Integer, Sequence('manufacturer_id_seq'), primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255), nullable=False)
    
if __name__ == '__main__':
=======
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, Text

Base = declarative_base()

# ユーザーテーブル定義
class User(Base):
    __tablename__ = 'users'
    user_id = Column(String(255), primary_key=True)
    user_name = Column(String(50), nullable=False)
    user_mail = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    user_picture = Column(LargeBinary)  # BLOB型でプロフィール画像を格納
    user_profile = Column(Text)  # ユーザーのプロフィール文
    age = Column(Integer)
    gender = Column(String(50))

    # UserとPostは1対多の関係
    posts = relationship('Post', back_populates='users')

# POSTテーブル定義
class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    review = Column(Text)  # レビューコメント
    rating = Column(Integer)  # 評価は1から5まで
    photos = relationship('Photo', back_populates='posts')

    # Postは特定のUserに属する
    users = relationship('User', back_populates='posts')

    # PostとPhotoは1対多の関係
    photos = relationship('Photo', back_populates='posts')

# 写真テーブル定義
class Photo(Base):
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    photo_data = Column(LargeBinary)
    posts = relationship('Post', back_populates='photos')

    # PhotoはPostに属する
    posts = relationship('Post', back_populates='photos')
    
    
# Userモデルに'posts'関係を追加
    User.posts = relationship('Post', order_by=Post.post_id, back_populates='users')
    
# Store テーブル定義
class Store(Base):
    __tablename__ = 'stores'
    store_id = Column(Integer, Sequence('store_id_seq'), primary_key=True, autoincrement=True)
    store_name = Column(String(255), nullable=False)
    store_address = Column(String(255), nullable=False)
    store_phonenumber = Column(String(255), nullable=True)

# Brand テーブル定義
class Brand(Base):
    __tablename__ = 'brands'
    brand_id = Column(Integer, Sequence('brand_id_seq'), primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('stores.store_id'), nullable=False)
    brand_name = Column(String(255), nullable=False)

# Manufacturer テーブル定義
class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    manufacturer_id = Column(Integer, Sequence('manufacturer_id_seq'), primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255), nullable=False)
    
if __name__ == '__main__':
>>>>>>> 697dd81a4d61d8dc460934f8b35796282b3499de
    app.run(debug=True)
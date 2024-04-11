"use client";
import { useEffect, useState } from 'react';
import { useRouter } from "next/navigation"; // ルーターフックのインポート
import './globals.css';

const Home = () => {
  const [isJwt, setIsJwt] = useState<boolean>(false);
  const [jwtMessage, setJwtMessage] = useState<string>('');
  const router = useRouter(); // useRouter フックの使用

  useEffect(() => {
    const jwt = localStorage.getItem('token');
    if (jwt) {
      setJwtMessage(`JWTあり`);
      setIsJwt(true);
    } else {
      setJwtMessage('JWTなし');
    }
  }, []);

  const handleLoginRedirect = () => {
    router.push('/login'); // `/login` への遷移
  };

  const handleMyRedirect = () => {
    router.push('/user'); // `/mypage` への遷移
  };

  const handleLogout = () => {
    localStorage.removeItem('token'); // JWTをローカルストレージから削除
    setIsJwt(false);
    setJwtMessage('JWTなし');
  };

  return (
    <>
      <div className='maindiv'>
        <div className="header blue">Beerlog</div>
        <div className='containt-body'>
          <div>
            <p>{jwtMessage}</p>
            {!isJwt && ( // JWTがない場合、ログインページへ
              <button onClick={handleLoginRedirect}>ログインページへ</button>
            )}
            {isJwt && ( // JWTがある場合、マイページへとログアウトボタンを表示
              <>
                <button onClick={handleMyRedirect}>マイページへ</button>
                <button onClick={handleLogout}>ログアウト</button>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
// pages/login.tsx
"use client";
import { useState } from 'react';
import { useRouter } from "next/navigation";

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: username, user_password: password }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.access_token;
        localStorage.setItem('token', token);
        router.push('/user');
      } else {
        throw new Error('ログインに失敗しました。');
      }
    } catch (error) {
      console.error(error);
      alert('ログイン中にエラーが発生しました。');
    }
  };

  return (
    <>
      <div className="header blue">ログイン画面</div>
      <div className='containt-body'>
        <div>
          <form onSubmit={handleLogin} className='form-container'>
            <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button type="submit">ログイン</button>
          </form>
        </div>
      </div>
    </>
  );
};

export default Login;
import React from 'react';

export default function OneUserInfoCard({ user_name, user_profile, user_picture }) {
  return (
    <div className="m-2 card shadow-md rounded-lg overflow-hidden">
      <div className="flex items-center justify-center">
        <div className="w-32 h-32 rounded-full overflow-hidden mb-4">
          <img
            src={`data:image/jpeg;base64,${user_picture}`}
            alt={`${user_name}さんのプロフィール画像`}
            className="w-full h-full object-cover"
          />
        </div>
      </div>
      <div className="rounded-lg p-4 bg-gray-100 text-center">
        <h2 className="text-2xl font-semibold mb-2 text-black">{user_name}</h2>
        <p className="text-base text-black">{user_profile}</p>
      </div>
    </div>
  );
}
export default function OneUserPostCard({ photos, rating, review }) {
  return (
    <div className="m-2 card shadow-md rounded-lg overflow-hidden">
      <div className="grid grid-cols-3 gap-1">
        {/* 3列のグリッドレイアウト */}
        {photos &&
          photos.map((photo, index) => (
            <div key={index} className="w-24 h-24 overflow-hidden">
              <img
                src={`data:image/jpeg;base64,${photo}`}
                alt={`User Post Image ${index}`}
                className="object-cover w-full h-full"
              />
            </div>
          ))}
      </div>
    </div>
  );
}
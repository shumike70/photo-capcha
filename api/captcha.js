import { ImageResponse } from '@vercel/og';

export const config = {
  runtime: 'edge',
};

export default function handler(request) {
  const { searchParams } = new URL(request.url);
  const text = searchParams.get('text') || '1234';

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundImage: 'url(https://i.ibb.co.com/Mxpk7wwc/image.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div
          style={{
            fontSize: 65,
            fontWeight: 'bold',
            color: '#00e5ff',
            letterSpacing: '10px',
            textShadow: '0 0 20px #00e5ff',
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            padding: '10px 30px',
            borderRadius: '16px',
            border: '2px solid #00e5ff',
            display: 'flex',
          }}
        >
          {text}
        </div>
      </div>
    ),
    {
      width: 450,
      height: 250,
    }
  );
}

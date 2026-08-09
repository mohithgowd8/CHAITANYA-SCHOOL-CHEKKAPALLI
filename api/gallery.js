let memoryGallery = [
  { type: 'image', src: 'student_life_1.png' },
  { type: 'image', src: 'student_life_2.png' },
  { type: 'image', src: 'student_life_3.png' },
  { type: 'image', src: 'student_life_4.png' },
  { type: 'image', src: 'student_life_5.png' },
  { type: 'image', src: 'student_life_6.png' }
];

const BLOB_URL = 'https://jsonblob.com/api/jsonBlob/019fe645-ebee-744b-b148-de57692728e2';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch(e){}
    }
    const gallery = body && body.gallery ? body.gallery : body;
    if (Array.isArray(gallery) && gallery.length > 0) {
      memoryGallery = gallery;
      try {
        await fetch(BLOB_URL, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(gallery)
        });
      } catch (err) {
        console.error('Blob sync error:', err);
      }
    }
    return res.status(200).json({ success: true, gallery: memoryGallery });
  }

  // GET Request
  try {
    const cloudRes = await fetch(BLOB_URL, {
      headers: { 'Accept': 'application/json' }
    });
    if (cloudRes.ok) {
      const data = await cloudRes.json();
      if (Array.isArray(data) && data.length > 0) {
        memoryGallery = data;
      }
    }
  } catch (err) {
    console.error('Blob fetch error:', err);
  }

  return res.status(200).json(memoryGallery);
}

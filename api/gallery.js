const FIRESTORE_REST_URL = 'https://firestore.googleapis.com/v1/projects/chaitanya-school-42b25/databases/(default)/documents/school_gallery/student_life';

let memoryCache = [
  { type: 'image', src: 'student_life_1.png' },
  { type: 'image', src: 'student_life_2.png' },
  { type: 'image', src: 'student_life_3.png' },
  { type: 'image', src: 'student_life_4.png' },
  { type: 'image', src: 'student_life_5.png' },
  { type: 'image', src: 'student_life_6.png' }
];

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
      memoryCache = gallery;
      try {
        const firestorePayload = {
          fields: {
            itemsJson: { stringValue: JSON.stringify(gallery) }
          }
        };
        await fetch(FIRESTORE_REST_URL, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(firestorePayload)
        });
      } catch(e) {}
    }
    return res.status(200).json({ success: true, gallery: memoryCache });
  }

  // GET Request
  try {
    const fsRes = await fetch(FIRESTORE_REST_URL);
    if (fsRes.ok) {
      const data = await fsRes.json();
      if (data && data.fields && data.fields.itemsJson && data.fields.itemsJson.stringValue) {
        const parsed = JSON.parse(data.fields.itemsJson.stringValue);
        if (Array.isArray(parsed) && parsed.length > 0) {
          memoryCache = parsed;
          return res.status(200).json(parsed);
        }
      }
    }
  } catch(e) {}

  return res.status(200).json(memoryCache);
}

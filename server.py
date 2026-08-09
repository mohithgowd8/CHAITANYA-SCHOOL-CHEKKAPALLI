import http.server
import socketserver
import os
import json
import uuid
import re

PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(DIRECTORY, "uploads")
GALLERY_JSON = os.path.join(DIRECTORY, "gallery.json")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

if not os.path.exists(GALLERY_JSON):
    default_gallery = [
        {"type": "image", "src": "student life.png"},
        {"type": "image", "src": "student life2.png"},
        {"type": "image", "src": "student life 3.png"},
        {"type": "image", "src": "student life 4.png"},
        {"type": "image", "src": "student life 5.png"},
        {"type": "image", "src": "student life6.png"}
    ]
    with open(GALLERY_JSON, "w", encoding="utf-8") as f:
        json.dump(default_gallery, f, indent=2)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/gallery':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            if os.path.exists(GALLERY_JSON):
                with open(GALLERY_JSON, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'[]')
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                length = int(self.headers.get('Content-Length', 0))
                raw_data = self.rfile.read(length)
                
                boundary = None
                if 'boundary=' in content_type:
                    boundary = content_type.split('boundary=')[1].strip('"').strip("'").encode()

                uploaded_files = []
                if boundary and boundary in raw_data:
                    parts = raw_data.split(b'--' + boundary)
                    for part in parts:
                        if b'filename="' in part:
                            header_part, body = part.split(b'\r\n\r\n', 1)
                            body = body.rsplit(b'\r\n', 1)[0]
                            
                            header_str = header_part.decode('utf-8', errors='ignore')
                            match = re.search(r'filename="([^"]+)"', header_str)
                            if match:
                                filename = match.group(1)
                                ext = os.path.splitext(filename)[1].lower()
                                if not ext:
                                    ext = '.jpg'
                                new_name = f"uploaded_{uuid.uuid4().hex[:8]}{ext}"
                                save_path = os.path.join(UPLOAD_DIR, new_name)
                                with open(save_path, 'wb') as f:
                                    f.write(body)
                                
                                is_video = ext in ['.mp4', '.webm', '.mov', '.avi']
                                uploaded_files.append({
                                    'type': 'video' if is_video else 'image',
                                    'src': f"uploads/{new_name}"
                                })

                with open(GALLERY_JSON, 'r', encoding='utf-8') as f:
                    current_gallery = json.load(f)
                
                current_gallery.extend(uploaded_files)
                with open(GALLERY_JSON, 'w', encoding='utf-8') as f:
                    json.dump(current_gallery, f, indent=2)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'gallery': current_gallery}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return

        if self.path == '/api/delete':
            try:
                length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(length)
                data = json.loads(post_data.decode('utf-8'))
                index = data.get('index')
                
                with open(GALLERY_JSON, 'r', encoding='utf-8') as f:
                    current_gallery = json.load(f)
                
                if 0 <= index < len(current_gallery):
                    deleted_item = current_gallery.pop(index)
                    if deleted_item.get('src', '').startswith('uploads/'):
                        file_to_del = os.path.join(DIRECTORY, deleted_item['src'])
                        if os.path.exists(file_to_del):
                            try: os.remove(file_to_del)
                            except: pass
                    
                    with open(GALLERY_JSON, 'w', encoding='utf-8') as f:
                        json.dump(current_gallery, f, indent=2)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'gallery': current_gallery}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                return

        super().do_POST()

if __name__ == '__main__':
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    server = ThreadedHTTPServer(("", PORT), CustomHandler)
    print(f"Serving multi-threaded server on port {PORT}...")
    server.serve_forever()

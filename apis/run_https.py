#!/usr/bin/env python
"""
Simple HTTPS server for Django using wsgiref
Minimal dependencies - just uses Python standard library
"""

import os
import sys
import ssl
import socket
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.x.x"

def main():
    """Main entry point"""
    
    print("\n" + "="*70)
    print("Face Recognition Server - HTTPS Startup")
    print("="*70 + "\n")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apis.settings')
    
    import django
    django.setup()
    print("✅ Django initialized\n")
    
    # Check certificates
    cert_dir = Path(__file__).parent / 'certs'
    cert_file = cert_dir / 'localhost.crt'
    key_file = cert_dir / 'localhost.key'
    
    if not cert_file.exists() or not key_file.exists():
        print("⚠️  SSL certificates not found. Generating...")
        os.system(f"{sys.executable} generate_cert.py")
        print()
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ Failed to generate certificates. Exiting.")
        sys.exit(1)
    
    print(f"✅ Certificates found\n")
    
    # Get WSGI application
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    print("✅ WSGI application loaded\n")
    
    # Setup server
    from wsgiref.simple_server import make_server
    
    host = '0.0.0.0'
    port = 8000
    
    # Check command line args
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    print(f"Creating HTTPS server on {host}:{port}...\n")
    
    # Create the server
    httpd = make_server(host, port, app)
    
    # Wrap socket with SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(cert_file), str(key_file))
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print("="*70)
    print("✅ HTTPS Server is running!")
    print("="*70)
    print()
    print("📱 Access the app at:")
    print(f"   https://localhost:{port}/user_faces/frontend/")
    print()
    print("🌐 From another device on your network:")
    local_ip = get_local_ip()
    print(f"   https://{local_ip}:{port}/user_faces/frontend/")
    print()
    print("⚠️  Browser will show a security warning (expected)")
    print("   Click 'Advanced' → 'Proceed anyway'")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



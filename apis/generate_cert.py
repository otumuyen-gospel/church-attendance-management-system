#!/usr/bin/env python3
"""
Generate a self-signed SSL certificate for local development
This allows HTTPS to work on any IP address
"""

import subprocess
import os
from pathlib import Path

def generate_cert():
    """Generate a self-signed SSL certificate"""
    
    cert_dir = Path(__file__).parent / 'certs'
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / 'localhost.crt'
    key_file = cert_dir / 'localhost.key'
    
    if cert_file.exists() and key_file.exists():
        print(f"✓ Certificate already exists at {cert_dir}")
        return str(cert_file), str(key_file)
    
    print("Generating self-signed SSL certificate...")
    print(f"Certificates will be saved to: {cert_dir}")
    
    # Generate private key and certificate
    cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', str(key_file),
        '-out', str(cert_file),
        '-days', '365', '-nodes',
        '-subj', '/CN=localhost'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Certificate generated: {cert_file}")
        print(f"✓ Key generated: {key_file}")
        return str(cert_file), str(key_file)
    except FileNotFoundError:
        print("✗ OpenSSL not found. Please install it:")
        print("  Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("  Or use: pip install pyOpenSSL")
        
        # Try Python alternative
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from datetime import datetime, timedelta
            
            print("\nUsing Python cryptography module...")
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost"),
                    x509.DNSName(u"127.0.0.1"),
                    x509.DNSName(u"*.local"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Write key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            print(f"✓ Certificate generated: {cert_file}")
            print(f"✓ Key generated: {key_file}")
            return str(cert_file), str(key_file)
            
        except ImportError:
            print("✗ Could not generate certificate with cryptography module")
            return None, None

if __name__ == '__main__':
    cert, key = generate_cert()
    if cert and key:
        print("\n" + "="*60)
        print("Certificate Setup Complete!")
        print("="*60)
        print(f"\nTo run the server with HTTPS, use:")
        print(f"  python manage.py runserver_plus --cert-file {cert} --key-file {key}")
        print(f"Or simply:")
        print(f"  python manage.py runserver_plus")
        print(f"\nYou can then access the app at:")
        print(f"  https://YOUR_IP:8000/user_faces/frontend/")
        print(f"\nNote: Browsers will show a security warning for self-signed certs.")
        print(f"      Click 'Advanced' and 'Proceed anyway' to continue.")
        print("="*60)

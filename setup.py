#!/usr/bin/env python3
"""
Setup Script for Academic Certificate Verification System
Initializes the system with sample data and configuration
"""

import json
import os
import sys
from datetime import datetime

def print_header():
    print("🎓 Academic Certificate Verification System")
    print("=" * 60)
    print("Setup and Initialization Script")
    print("=" * 60)

def check_dependencies():
    print("\n🔍 Checking dependencies...")

    required_modules = [
        'flask', 'cryptography', 'qrcode', 'sqlite3', 'hashlib'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            elif module == 'hashlib':
                import hashlib
            else:
                __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} (missing)")

    if missing_modules:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies satisfied!")
    return True

def initialize_system():
    print("\n🔧 Initializing system...")

    try:
        from blockchain import AcademicBlockchain
        from wallet import WalletManager
        from certificate_issuer import CertificateIssuer

        # Initialize components
        blockchain = AcademicBlockchain()
        wallet_manager = WalletManager()
        issuer = CertificateIssuer(blockchain, wallet_manager)

        print("✅ Blockchain initialized")
        print("✅ Wallet manager created") 
        print("✅ Certificate issuer ready")

        return blockchain, wallet_manager, issuer

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None, None, None

def load_sample_data(issuer):
    print("\n📊 Loading sample data...")

    try:
        # Load institutions
        if os.path.exists('sample_institutions.json'):
            with open('sample_institutions.json', 'r') as f:
                institutions_data = json.load(f)

            for inst in institutions_data['institutions']:
                result = issuer.register_institution(
                    inst['institution_name'],
                    inst['authority_id']
                )
                if result['success']:
                    print(f"✅ Registered: {inst['institution_name']}")
                else:
                    print(f"⚠️ {inst['institution_name']}: {result['error']}")

        # Load sample certificates
        if os.path.exists('sample_students.json'):
            with open('sample_students.json', 'r') as f:
                students_data = json.load(f)

            for student in students_data['students']:
                # Map institution names to authority IDs
                institution_map = {
                    "Massachusetts Institute of Technology": "mit",
                    "Stanford University": "stanford", 
                    "Harvard University": "harvard",
                    "University of California, Berkeley": "berkeley",
                    "California Institute of Technology": "caltech"
                }

                authority_id = institution_map.get(student['institution'])
                if authority_id:
                    result = issuer.issue_certificate(authority_id, student)
                    if result['success']:
                        print(f"✅ Certificate issued: {student['student_name']}")
                    else:
                        print(f"⚠️ Failed: {student['student_name']} - {result['error']}")

        print("\n✅ Sample data loaded successfully!")

    except Exception as e:
        print(f"❌ Sample data loading failed: {e}")

def create_directories():
    print("\n📁 Creating necessary directories...")

    directories = ['wallets', 'data', 'exports', 'logs']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created: {directory}/")
        else:
            print(f"✅ Exists: {directory}/")

def show_system_info(blockchain):
    print("\n📈 System Information:")
    print("-" * 40)

    try:
        info = blockchain.get_chain_info()
        print(f"Total Blocks: {info['total_blocks']}")
        print(f"Total Certificates: {info['total_certificates']}")
        print(f"Total Authorities: {info['total_authorities']}")
        print(f"Chain Valid: {'✅' if info['chain_valid'] else '❌'}")

        if info['latest_block_hash']:
            print(f"Latest Block: {info['latest_block_hash'][:16]}...")

    except Exception as e:
        print(f"❌ Could not retrieve system info: {e}")

def main():
    print_header()

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        sys.exit(1)

    # Create directories
    create_directories()

    # Initialize system
    blockchain, wallet_manager, issuer = initialize_system()
    if not blockchain:
        print("\n❌ Setup failed: Could not initialize system")
        sys.exit(1)

    # Load sample data
    load_sample_data(issuer)

    # Show system info
    show_system_info(blockchain)

    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\n🚀 Next steps:")
    print("   1. Run demo: python demo.py")
    print("   2. Run tests: python test.py")
    print("   3. Start web app: python app.py")
    print("   4. Open browser: http://localhost:5000")
    print("\n✨ The system is ready for use!")

if __name__ == "__main__":
    main()

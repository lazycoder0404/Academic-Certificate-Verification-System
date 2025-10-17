# Create sample data files for the project
import json
from datetime import datetime, timedelta
import random

# Create sample institutions data
sample_institutions = {
    "institutions": [
        {
            "authority_id": "mit",
            "institution_name": "Massachusetts Institute of Technology",
            "location": "Cambridge, MA, USA",
            "established": "1861",
            "website": "https://web.mit.edu/",
            "accreditation": "NEASC"
        },
        {
            "authority_id": "stanford",
            "institution_name": "Stanford University", 
            "location": "Stanford, CA, USA",
            "established": "1885",
            "website": "https://www.stanford.edu/",
            "accreditation": "WSCUC"
        },
        {
            "authority_id": "harvard",
            "institution_name": "Harvard University",
            "location": "Cambridge, MA, USA", 
            "established": "1636",
            "website": "https://www.harvard.edu/",
            "accreditation": "NEASC"
        },
        {
            "authority_id": "berkeley",
            "institution_name": "University of California, Berkeley",
            "location": "Berkeley, CA, USA",
            "established": "1868", 
            "website": "https://www.berkeley.edu/",
            "accreditation": "WSCUC"
        },
        {
            "authority_id": "caltech",
            "institution_name": "California Institute of Technology",
            "location": "Pasadena, CA, USA",
            "established": "1891",
            "website": "https://www.caltech.edu/", 
            "accreditation": "WSCUC"
        }
    ]
}

# Create sample students data
sample_students = {
    "students": [
        {
            "student_name": "Alice Johnson",
            "student_id": "MIT2024001",
            "degree": "Bachelor of Science in Computer Science",
            "institution": "Massachusetts Institute of Technology",
            "issue_date": "2024-06-15",
            "graduation_date": "2024-06-15",
            "grade": "Magna Cum Laude",
            "gpa": "3.8",
            "major": "Computer Science",
            "minor": "Mathematics",
            "email": "alice.johnson@mit.edu"
        },
        {
            "student_name": "Bob Smith",
            "student_id": "STAN2024002",
            "degree": "Master of Business Administration",
            "institution": "Stanford University", 
            "issue_date": "2024-06-20",
            "graduation_date": "2024-06-20",
            "grade": "Distinction",
            "gpa": "3.9",
            "major": "Business Administration",
            "specialization": "Technology Management",
            "email": "bob.smith@stanford.edu"
        },
        {
            "student_name": "Carol Davis", 
            "student_id": "HVD2024003",
            "degree": "Doctor of Medicine",
            "institution": "Harvard University",
            "issue_date": "2024-05-30",
            "graduation_date": "2024-05-30", 
            "grade": "Summa Cum Laude",
            "gpa": "3.95",
            "major": "Medicine",
            "specialization": "Cardiology",
            "email": "carol.davis@harvard.edu"
        },
        {
            "student_name": "David Wilson",
            "student_id": "UCB2024004", 
            "degree": "Bachelor of Science in Electrical Engineering",
            "institution": "University of California, Berkeley",
            "issue_date": "2024-05-15",
            "graduation_date": "2024-05-15",
            "grade": "Cum Laude",
            "gpa": "3.7",
            "major": "Electrical Engineering",
            "minor": "Computer Science", 
            "email": "david.wilson@berkeley.edu"
        },
        {
            "student_name": "Emma Brown",
            "student_id": "CIT2024005",
            "degree": "Doctor of Philosophy in Physics", 
            "institution": "California Institute of Technology",
            "issue_date": "2024-06-01",
            "graduation_date": "2024-06-01",
            "grade": "Distinction",
            "gpa": "3.85",
            "major": "Physics",
            "research_area": "Quantum Mechanics",
            "email": "emma.brown@caltech.edu"
        }
    ]
}

# Create configuration file
config = {
    "system": {
        "name": "Academic Certificate Verification System",
        "version": "1.0.0",
        "description": "Decentralized blockchain-based certificate verification",
        "consensus": "Proof-of-Authority"
    },
    "blockchain": {
        "genesis_message": "Academic Certificate Verification System Genesis Block",
        "difficulty": 4,
        "block_time": "on-demand",
        "max_certificates_per_block": 100
    },
    "cryptography": {
        "signature_algorithm": "RSA-PSS",
        "hash_algorithm": "SHA-256", 
        "key_size": 2048,
        "padding": "PSS with MGF1"
    },
    "database": {
        "type": "SQLite",
        "filename": "academic_blockchain.db",
        "backup_interval": "daily"
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "cors_enabled": True,
        "rate_limiting": False
    },
    "security": {
        "require_https": False,
        "session_timeout": 3600,
        "password_encryption": True,
        "audit_logging": True
    }
}

# Save sample data files
with open('sample_institutions.json', 'w') as f:
    json.dump(sample_institutions, f, indent=2)

with open('sample_students.json', 'w') as f:
    json.dump(sample_students, f, indent=2)

with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Created sample data files:")
print("- sample_institutions.json (Sample university data)")
print("- sample_students.json (Sample student certificates)")
print("- config.json (System configuration)")

# Create a setup script
setup_script = """#!/usr/bin/env python3
\"\"\"
Setup Script for Academic Certificate Verification System
Initializes the system with sample data and configuration
\"\"\"

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
    print("\\n🔍 Checking dependencies...")
    
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
        print(f"\\n⚠️ Missing dependencies: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\\n✅ All dependencies satisfied!")
    return True

def initialize_system():
    print("\\n🔧 Initializing system...")
    
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
    print("\\n📊 Loading sample data...")
    
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
        
        print("\\n✅ Sample data loaded successfully!")
        
    except Exception as e:
        print(f"❌ Sample data loading failed: {e}")

def create_directories():
    print("\\n📁 Creating necessary directories...")
    
    directories = ['wallets', 'data', 'exports', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created: {directory}/")
        else:
            print(f"✅ Exists: {directory}/")

def show_system_info(blockchain):
    print("\\n📈 System Information:")
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
        print("\\n❌ Setup failed: Missing dependencies")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize system
    blockchain, wallet_manager, issuer = initialize_system()
    if not blockchain:
        print("\\n❌ Setup failed: Could not initialize system")
        sys.exit(1)
    
    # Load sample data
    load_sample_data(issuer)
    
    # Show system info
    show_system_info(blockchain)
    
    # Final instructions
    print("\\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\\n🚀 Next steps:")
    print("   1. Run demo: python demo.py")
    print("   2. Run tests: python test.py")
    print("   3. Start web app: python app.py")
    print("   4. Open browser: http://localhost:5000")
    print("\\n✨ The system is ready for use!")

if __name__ == "__main__":
    main()
"""

with open('setup.py', 'w') as f:
    f.write(setup_script)

print("✅ Created setup.py (System initialization script)")

# Create final project manifest
manifest = {
    "project": {
        "name": "Academic Certificate Verification System",
        "version": "1.0.0",
        "description": "Decentralized blockchain-based academic certificate management",
        "author": "AI Assistant",
        "license": "Educational Use",
        "created": datetime.now().isoformat()
    },
    "files": {
        "core": [
            "blockchain.py",
            "wallet.py", 
            "certificate_issuer.py",
            "app.py"
        ],
        "configuration": [
            "requirements.txt",
            "config.json",
            "Dockerfile",
            "docker-compose.yml",
            ".gitignore"
        ],
        "documentation": [
            "README.md"
        ],
        "scripts": [
            "demo.py",
            "test.py", 
            "setup.py"
        ],
        "sample_data": [
            "sample_institutions.json",
            "sample_students.json"
        ],
        "generated": [
            "academic_blockchain.db",
            "wallets/",
            "blockchain_export_*.json"
        ]
    },
    "features": {
        "blockchain": [
            "Proof-of-Authority consensus",
            "SQLite persistence",
            "Chain validation",
            "Block mining"
        ],
        "certificates": [
            "Digital issuance",
            "Hash-based verification", 
            "Certificate revocation",
            "Privacy protection"
        ],
        "security": [
            "RSA digital signatures",
            "SHA-256 hashing",
            "Key management",
            "Authority validation"
        ],
        "interface": [
            "Flask web application",
            "REST API",
            "QR code generation",
            "Real-time statistics"
        ]
    },
    "usage": {
        "quick_start": [
            "pip install -r requirements.txt",
            "python setup.py",
            "python app.py"
        ],
        "demo": "python demo.py",
        "tests": "python test.py",
        "docker": "docker-compose up -d"
    }
}

with open('project_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)

print("✅ Created project_manifest.json (Complete project overview)")
print("\n🎯 PROJECT STATISTICS:")
print(f"📁 Total Files Created: {len(manifest['files']['core']) + len(manifest['files']['configuration']) + len(manifest['files']['documentation']) + len(manifest['files']['scripts']) + len(manifest['files']['sample_data']) + 1}")
print(f"🔧 Core Implementation Files: {len(manifest['files']['core'])}")
print(f"⚙️ Configuration Files: {len(manifest['files']['configuration'])}")
print(f"📖 Documentation Files: {len(manifest['files']['documentation'])}")
print(f"🎬 Script Files: {len(manifest['files']['scripts'])}")
print(f"📊 Sample Data Files: {len(manifest['files']['sample_data'])}")
print(f"✨ Key Features: {sum(len(features) for features in manifest['features'].values())}")
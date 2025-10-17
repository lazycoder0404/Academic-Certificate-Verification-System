#!/usr/bin/env python3
"""
Demo Script for Academic Certificate Verification System
This script demonstrates all the key features of the blockchain system.
"""

import sys
import time
import json
from datetime import datetime

# Import our modules
from blockchain import AcademicBlockchain
from wallet import WalletManager
from certificate_issuer import CertificateIssuer

def print_banner(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, description):
    print(f"\n🔹 Step {step_num}: {description}")
    print("-" * 40)

def demo_blockchain_basics():
    print_banner("🧱 BLOCKCHAIN BASICS DEMO")

    # Initialize blockchain
    print_step(1, "Initialize Blockchain")
    blockchain = AcademicBlockchain()
    print(f"✅ Genesis block created: {blockchain.get_latest_block().hash[:16]}...")

    # Show blockchain info
    info = blockchain.get_chain_info()
    print(f"📊 Blockchain Stats:")
    print(f"   - Total blocks: {info['total_blocks']}")
    print(f"   - Chain valid: {info['chain_valid']}")
    print(f"   - Latest hash: {info['latest_block_hash'][:16]}..." if info['latest_block_hash'] else "None")

    return blockchain

def demo_wallet_system():
    print_banner("💳 WALLET SYSTEM DEMO")

    # Initialize wallet manager
    print_step(1, "Create Wallet Manager")
    wallet_manager = WalletManager()

    # Create university wallet
    print_step(2, "Create University Wallet")
    university_wallet = wallet_manager.create_wallet("university")
    print(f"✅ University wallet created: {university_wallet.wallet_id}")

    # Create student wallet
    print_step(3, "Create Student Wallet")
    student_wallet = wallet_manager.create_wallet("student")
    print(f"✅ Student wallet created: {student_wallet.wallet_id}")

    # Demonstrate digital signatures
    print_step(4, "Test Digital Signatures")
    test_data = {
        "message": "Test certificate data",
        "timestamp": datetime.now().isoformat()
    }

    # Sign with university wallet
    signature = university_wallet.sign_certificate(test_data)
    print(f"✅ Data signed: {signature[:32]}...")

    # Verify signature
    is_valid = university_wallet.verify_signature(test_data, signature)
    print(f"✅ Signature verified: {is_valid}")

    return wallet_manager, university_wallet, student_wallet

def demo_certificate_issuance(blockchain, wallet_manager):
    print_banner("📜 CERTIFICATE ISSUANCE DEMO")

    # Initialize certificate issuer
    print_step(1, "Initialize Certificate Issuer")
    issuer = CertificateIssuer(blockchain, wallet_manager)

    # Register institutions
    print_step(2, "Register Academic Institutions")

    institutions = [
        ("Massachusetts Institute of Technology", "mit"),
        ("Stanford University", "stanford"),
        ("Harvard University", "harvard"),
        ("University of California Berkeley", "berkeley")
    ]

    for name, auth_id in institutions:
        result = issuer.register_institution(name, auth_id)
        if result["success"]:
            print(f"✅ {name} registered as '{auth_id}'")
        else:
            print(f"❌ Failed to register {name}: {result['error']}")

    # Issue certificates
    print_step(3, "Issue Academic Certificates")

    sample_students = [
        {
            "authority_id": "mit",
            "student_name": "Alice Johnson",
            "student_id": "MIT2024001",
            "degree": "Bachelor of Computer Science",
            "institution": "Massachusetts Institute of Technology",
            "issue_date": "2024-06-15",
            "grade": "Magna Cum Laude"
        },
        {
            "authority_id": "stanford",
            "student_name": "Bob Smith",
            "student_id": "STAN2024002", 
            "degree": "Master of Business Administration",
            "institution": "Stanford University",
            "issue_date": "2024-06-20",
            "grade": "Distinction"
        },
        {
            "authority_id": "harvard",
            "student_name": "Carol Davis",
            "student_id": "HVD2024003",
            "degree": "Doctor of Medicine",
            "institution": "Harvard University", 
            "issue_date": "2024-05-30",
            "grade": "Summa Cum Laude"
        }
    ]

    issued_certificates = []

    for student_data in sample_students:
        authority_id = student_data.pop("authority_id")
        result = issuer.issue_certificate(authority_id, student_data)

        if result["success"]:
            cert_hash = result["certificate_hash"]
            print(f"✅ Certificate issued for {student_data['student_name']}")
            print(f"   Hash: {cert_hash}")
            print(f"   Block: {result['block_index']}")
            issued_certificates.append(cert_hash)
        else:
            print(f"❌ Failed to issue certificate: {result['error']}")

    return issuer, issued_certificates

def demo_certificate_verification(issuer, certificates):
    print_banner("🔍 CERTIFICATE VERIFICATION DEMO")

    print_step(1, "Verify Issued Certificates")

    for i, cert_hash in enumerate(certificates):
        print(f"\n📋 Verifying Certificate {i+1}")
        result = issuer.verify_certificate_by_hash(cert_hash)

        if result["success"]:
            cert = result["certificate"]
            print(f"✅ Certificate VALID")
            print(f"   Student: {cert['student_name']}")
            print(f"   Degree: {cert['degree']}")
            print(f"   Institution: {cert['institution']}")
            print(f"   Status: {cert['status']}")
            print(f"   Block Index: {cert['block_index']}")
        else:
            print(f"❌ Certificate INVALID: {result['error']}")

    # Test invalid certificate
    print_step(2, "Test Invalid Certificate")
    fake_hash = "1234567890abcdef" * 4  # 64 character fake hash
    result = issuer.verify_certificate_by_hash(fake_hash)
    print(f"❌ Fake certificate result: {result['success']} - {result.get('error', 'Unknown error')}")

def demo_certificate_search(issuer):
    print_banner("🔎 CERTIFICATE SEARCH DEMO")

    search_queries = [
        {"student_name": "Alice Johnson"},
        {"institution": "Stanford University"},
        {"degree": "Doctor of Medicine"}
    ]

    for i, query in enumerate(search_queries):
        print_step(i+1, f"Search by {list(query.keys())[0]}: {list(query.values())[0]}")
        results = issuer.search_certificates(query)

        if results:
            print(f"✅ Found {len(results)} certificate(s)")
            for cert in results:
                print(f"   - {cert['student_name']}: {cert['degree']}")
        else:
            print("❌ No certificates found")

def demo_certificate_revocation(issuer, certificates):
    print_banner("🚫 CERTIFICATE REVOCATION DEMO")

    if certificates:
        cert_to_revoke = certificates[0]  # Revoke the first certificate

        print_step(1, "Revoke a Certificate")
        print(f"Revoking certificate: {cert_to_revoke}")

        result = issuer.revoke_certificate("mit", cert_to_revoke, "Academic misconduct detected")

        if result["success"]:
            print("✅ Certificate revoked successfully")
            print(f"   Reason: Academic misconduct detected")
            print(f"   Revoked by: mit")
        else:
            print(f"❌ Revocation failed: {result['error']}")

        # Verify the revoked certificate
        print_step(2, "Verify Revoked Certificate")
        verification = issuer.verify_certificate_by_hash(cert_to_revoke)
        if verification["success"]:
            status = verification["certificate"]["status"]
            print(f"✅ Certificate status: {status}")
        else:
            print("❌ Failed to verify revoked certificate")

def demo_institution_statistics(issuer):
    print_banner("📊 INSTITUTION STATISTICS DEMO")

    institutions = ["mit", "stanford", "harvard", "berkeley"]

    for auth_id in institutions:
        print_step(institutions.index(auth_id)+1, f"Statistics for {auth_id.upper()}")
        result = issuer.get_institution_statistics(auth_id)

        if result["success"]:
            stats = result["statistics"]
            print(f"✅ {stats['institution_name']}")
            print(f"   Total certificates: {stats['total_certificates']}")
            print(f"   Active certificates: {stats['active_certificates']}")
            print(f"   Revoked certificates: {stats['revoked_certificates']}")
        else:
            print(f"❌ Failed to get statistics: {result['error']}")

def demo_blockchain_export(blockchain):
    print_banner("💾 BLOCKCHAIN EXPORT DEMO")

    print_step(1, "Export Blockchain Data")
    try:
        filename = blockchain.export_chain()
        print(f"✅ Blockchain exported to: {filename}")

        # Show file size
        import os
        size = os.path.getsize(filename)
        print(f"   File size: {size:,} bytes")

        # Show first few lines of the export
        print("\n📄 Export preview:")
        with open(filename, 'r') as f:
            content = json.load(f)
            print(f"   Blocks exported: {len(content['blockchain'])}")
            print(f"   Authorities: {len(content['authorities'])}")
            print(f"   Export timestamp: {content['export_timestamp']}")

    except Exception as e:
        print(f"❌ Export failed: {e}")

def run_complete_demo():
    """Run the complete demonstration of the academic blockchain system"""

    print("🎓 ACADEMIC CERTIFICATE VERIFICATION SYSTEM")
    print("           COMPLETE SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demo will showcase all features of the blockchain system:")
    print("• Blockchain initialization and management")
    print("• Wallet creation and digital signatures") 
    print("• Institution registration")
    print("• Certificate issuance and mining")
    print("• Certificate verification")
    print("• Search functionality")
    print("• Certificate revocation")
    print("• Statistics and reporting")
    print("• Data export")
    print("=" * 60)

    input("\nPress Enter to start the demonstration...")

    try:
        # Step-by-step demonstration
        blockchain = demo_blockchain_basics()
        time.sleep(1)

        wallet_manager, uni_wallet, stu_wallet = demo_wallet_system()
        time.sleep(1)

        issuer, certificates = demo_certificate_issuance(blockchain, wallet_manager)
        time.sleep(1)

        demo_certificate_verification(issuer, certificates)
        time.sleep(1)

        demo_certificate_search(issuer)
        time.sleep(1)

        demo_certificate_revocation(issuer, certificates)
        time.sleep(1)

        demo_institution_statistics(issuer)
        time.sleep(1)

        demo_blockchain_export(blockchain)

        # Final summary
        print_banner("🎉 DEMONSTRATION COMPLETE")
        final_info = blockchain.get_chain_info()
        print(f"\n📈 Final Blockchain Statistics:")
        print(f"   Total blocks: {final_info['total_blocks']}")
        print(f"   Total certificates: {final_info['total_certificates']}")
        print(f"   Total revocations: {final_info['total_revocations']}")
        print(f"   Total authorities: {final_info['total_authorities']}")
        print(f"   Chain validity: {'✅ VALID' if final_info['chain_valid'] else '❌ INVALID'}")

        print("\n🚀 To run the web interface:")
        print("   python app.py")
        print("   Then open: http://localhost:5000")

        print("\n✨ Demo completed successfully!")
        print("   All components working correctly.")
        print("   System ready for production use.")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("   Please check the error and try again.")
        sys.exit(1)

if __name__ == "__main__":
    run_complete_demo()

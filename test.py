#!/usr/bin/env python3
"""
Test Script for Academic Certificate Verification System
Runs automated tests to verify all components work correctly.
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime

from blockchain import AcademicBlockchain, Block
from wallet import WalletManager, AcademicWallet
from certificate_issuer import CertificateIssuer

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        # Create temporary database for testing
        self.test_db = tempfile.mktemp(suffix='.db')
        self.blockchain = AcademicBlockchain()
        self.blockchain.db_path = self.test_db
        self.blockchain.init_database()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_genesis_block_creation(self):
        """Test that genesis block is created correctly"""
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(genesis.validator, "system")

    def test_authority_management(self):
        """Test adding and validating authorities"""
        success = self.blockchain.add_authority("test_uni", "Test University", "test_public_key")
        self.assertTrue(success)
        self.assertTrue(self.blockchain.is_valid_authority("test_uni"))

        # Test duplicate authority
        duplicate = self.blockchain.add_authority("test_uni", "Test University 2", "test_key_2")
        self.assertFalse(duplicate)

    def test_certificate_operations(self):
        """Test certificate addition and mining"""
        # Add authority first
        self.blockchain.add_authority("test_uni", "Test University", "test_public_key")

        # Add certificate
        cert_data = {
            "student_name": "Test Student",
            "student_id": "TEST001",
            "degree": "Test Degree",
            "institution": "Test University",
            "issue_date": "2024-01-01"
        }

        success = self.blockchain.add_certificate(cert_data, "test_uni")
        self.assertTrue(success)

        # Mine the certificate
        block = self.blockchain.mine_pending_certificates("test_uni")
        self.assertIsNotNone(block)
        self.assertEqual(len(self.blockchain.chain), 2)

    def test_chain_validation(self):
        """Test blockchain validation"""
        self.assertTrue(self.blockchain.is_chain_valid())

        # Add some blocks and test again
        self.blockchain.add_authority("test_uni", "Test University", "test_public_key")
        cert_data = {
            "student_name": "Test Student",
            "degree": "Test Degree",
            "institution": "Test University",
            "issue_date": "2024-01-01"
        }
        self.blockchain.add_certificate(cert_data, "test_uni")
        self.blockchain.mine_pending_certificates("test_uni")

        self.assertTrue(self.blockchain.is_chain_valid())

class TestWallet(unittest.TestCase):

    def setUp(self):
        self.test_wallet_dir = tempfile.mkdtemp()
        self.wallet = AcademicWallet()
        self.wallet.keys_path = os.path.join(self.test_wallet_dir, self.wallet.wallet_id)

    def tearDown(self):
        shutil.rmtree(self.test_wallet_dir, ignore_errors=True)

    def test_key_generation(self):
        """Test RSA key pair generation"""
        success = self.wallet.generate_keys()
        self.assertTrue(success)
        self.assertIsNotNone(self.wallet.private_key)
        self.assertIsNotNone(self.wallet.public_key)

    def test_digital_signatures(self):
        """Test certificate signing and verification"""
        self.wallet.generate_keys()

        test_cert = {
            "student_name": "Test Student",
            "degree": "Test Degree",
            "issue_date": "2024-01-01"
        }

        # Sign certificate
        signature = self.wallet.sign_certificate(test_cert)
        self.assertIsInstance(signature, str)

        # Verify signature
        is_valid = self.wallet.verify_signature(test_cert, signature)
        self.assertTrue(is_valid)

        # Test with tampered data
        tampered_cert = test_cert.copy()
        tampered_cert["student_name"] = "Tampered Name"
        is_valid_tampered = self.wallet.verify_signature(tampered_cert, signature)
        self.assertFalse(is_valid_tampered)

class TestCertificateIssuer(unittest.TestCase):

    def setUp(self):
        self.test_db = tempfile.mktemp(suffix='.db')
        self.test_wallet_dir = tempfile.mkdtemp()

        self.blockchain = AcademicBlockchain()
        self.blockchain.db_path = self.test_db
        self.blockchain.init_database()

        self.wallet_manager = WalletManager()
        self.issuer = CertificateIssuer(self.blockchain, self.wallet_manager)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        shutil.rmtree(self.test_wallet_dir, ignore_errors=True)
        shutil.rmtree("wallets", ignore_errors=True)

    def test_institution_registration(self):
        """Test institution registration"""
        result = self.issuer.register_institution("Test University", "test_uni")
        self.assertTrue(result["success"])
        self.assertEqual(result["authority_id"], "test_uni")
        self.assertIn("wallet_id", result)

    def test_certificate_issuance(self):
        """Test complete certificate issuance flow"""
        # Register institution
        self.issuer.register_institution("Test University", "test_uni")

        # Issue certificate
        student_data = {
            "student_name": "Test Student",
            "student_id": "TEST001",
            "degree": "Bachelor of Testing",
            "institution": "Test University", 
            "issue_date": "2024-01-01"
        }

        result = self.issuer.issue_certificate("test_uni", student_data)
        self.assertTrue(result["success"])
        self.assertIn("certificate_hash", result)
        self.assertIn("block_index", result)

    def test_certificate_verification(self):
        """Test certificate verification"""
        # Setup and issue certificate
        self.issuer.register_institution("Test University", "test_uni")
        student_data = {
            "student_name": "Test Student",
            "student_id": "TEST001",
            "degree": "Bachelor of Testing",
            "institution": "Test University",
            "issue_date": "2024-01-01"
        }

        issue_result = self.issuer.issue_certificate("test_uni", student_data)
        cert_hash = issue_result["certificate_hash"]

        # Verify certificate
        verify_result = self.issuer.verify_certificate_by_hash(cert_hash)
        self.assertTrue(verify_result["success"])
        self.assertEqual(verify_result["certificate"]["student_name"], "Test Student")

    def test_certificate_revocation(self):
        """Test certificate revocation"""
        # Setup and issue certificate
        self.issuer.register_institution("Test University", "test_uni")
        student_data = {
            "student_name": "Test Student",
            "student_id": "TEST001", 
            "degree": "Bachelor of Testing",
            "institution": "Test University",
            "issue_date": "2024-01-01"
        }

        issue_result = self.issuer.issue_certificate("test_uni", student_data)
        cert_hash = issue_result["certificate_hash"]

        # Revoke certificate
        revoke_result = self.issuer.revoke_certificate("test_uni", cert_hash, "Test revocation")
        self.assertTrue(revoke_result["success"])

        # Verify revoked status
        verify_result = self.issuer.verify_certificate_by_hash(cert_hash)
        self.assertTrue(verify_result["success"])
        self.assertEqual(verify_result["certificate"]["status"], "revoked")

def run_all_tests():
    """Run all test suites"""
    print("🧪 Running Academic Blockchain Tests")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestBlockchain))
    test_suite.addTest(unittest.makeSuite(TestWallet))  
    test_suite.addTest(unittest.makeSuite(TestCertificateIssuer))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
        print(f"   Tests run: {result.testsRun}")
        print("   System is ready for use.")
    else:
        print("❌ Some tests failed!")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

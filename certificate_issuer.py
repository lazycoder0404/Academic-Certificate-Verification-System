import os
import shutil
import json
import hashlib
from datetime import datetime
from typing import Dict, List
from blockchain import AcademicBlockchain
from wallet import WalletManager


class CertificateIssuer:
    def __init__(self, blockchain: AcademicBlockchain, wallet_manager: WalletManager):
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.institution_wallets = {}
        self.load_institution_wallets()

    def load_institution_wallets(self):
        """Load wallets for all registered authorities from wallet_manager"""
        for authority_id in self.blockchain.authorities.keys():
            wallet = self.wallet_manager.get_wallet(authority_id)
            if wallet:
                self.institution_wallets[authority_id] = wallet
            else:
                wallet = self.wallet_manager.create_wallet("institution")
                if wallet:
                    old_path = wallet.keys_path
                    wallet.wallet_id = authority_id
                    wallet.keys_path = f"wallets/{authority_id}"
                    os.makedirs(wallet.keys_path, exist_ok=True)
                    if os.path.exists(old_path):
                        if os.path.exists(f"{old_path}/private_key.pem"):
                            shutil.copy(f"{old_path}/private_key.pem", f"{wallet.keys_path}/private_key.pem")
                        if os.path.exists(f"{old_path}/public_key.pem"):
                            shutil.copy(f"{old_path}/public_key.pem", f"{wallet.keys_path}/public_key.pem")
                    wallet.save_wallet_data()
                    self.wallet_manager.wallets[authority_id] = wallet
                    self.institution_wallets[authority_id] = wallet

    def register_institution(self, institution_name: str, authority_id: str = None) -> Dict:
        """Register a new institution as an authority"""
        if not authority_id:
            authority_id = institution_name.lower().replace(' ', '_').replace('.', '')
        if self.wallet_manager.get_wallet(authority_id):
            return {"success": False, "error": "Institution ID already exists"}
        institution_wallet = self.wallet_manager.create_wallet("institution")
        if not institution_wallet:
            return {"success": False, "error": "Failed to create wallet"}
        old_path = institution_wallet.keys_path
        institution_wallet.wallet_id = authority_id
        institution_wallet.keys_path = f"wallets/{authority_id}"
        os.makedirs(institution_wallet.keys_path, exist_ok=True)
        if os.path.exists(old_path):
            if os.path.exists(f"{old_path}/private_key.pem"):
                shutil.move(f"{old_path}/private_key.pem", f"{institution_wallet.keys_path}/private_key.pem")
            if os.path.exists(f"{old_path}/public_key.pem"):
                shutil.move(f"{old_path}/public_key.pem", f"{institution_wallet.keys_path}/public_key.pem")
            try:
                os.rmdir(old_path)
            except Exception:
                pass
        institution_wallet.save_wallet_data()
        self.wallet_manager.wallets[authority_id] = institution_wallet
        public_key = institution_wallet.get_public_key_pem()
        success = self.blockchain.add_authority(authority_id, institution_name, public_key)
        if success:
            self.institution_wallets[authority_id] = institution_wallet
            return {
                "success": True,
                "authority_id": authority_id,
                "institution_name": institution_name,
                "wallet_id": institution_wallet.wallet_id,
                "public_key": public_key
            }
        else:
            return {"success": False, "error": "Failed to register authority"}

    def issue_certificate(self, authority_id: str, student_data: Dict) -> Dict:
        """Issue a new certificate for a student"""
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Institution not registered or inactive"}
        institution_wallet = self.wallet_manager.get_wallet(authority_id)
        if not institution_wallet:
            return {"success": False, "error": "Institution wallet not found. Please register institution again."}
        required_fields = ["student_name", "student_id", "degree", "institution", "issue_date"]
        for field in required_fields:
            if field not in student_data:
                return {"success": False, "error": f"Missing required field: {field}"}
        try:
            certificate = institution_wallet.create_signed_certificate(
                student_name=student_data["student_name"],
                student_id=student_data["student_id"],
                degree=student_data["degree"],
                institution=student_data["institution"],
                issue_date=student_data["issue_date"]
            )
            certificate["grade"] = student_data.get("grade", "Pass")
            certificate["graduation_date"] = student_data.get("graduation_date", student_data["issue_date"])
            certificate["certificate_id"] = self.generate_certificate_id(certificate)
            success = self.blockchain.add_certificate(certificate, authority_id)
            if success:
                block = self.blockchain.mine_pending_certificates(authority_id)
                return {
                    "success": True,
                    "certificate": certificate,
                    "certificate_hash": certificate.get("cert_hash"),
                    "block_index": block.block_index if block else None,
                    "transaction_id": block.hash if block else None
                }
            else:
                return {"success": False, "error": "Failed to add certificate to blockchain"}
        except Exception as e:
            return {"success": False, "error": f"Certificate issuance failed: {str(e)}"}

    def generate_certificate_id(self, certificate: Dict) -> str:
        """Generate a unique certificate ID"""
        cert_string = f"{certificate['student_id']}_{certificate['degree']}_{certificate['issue_date']}"
        return hashlib.md5(cert_string.encode()).hexdigest()[:12].upper()

    def verify_certificate_by_hash(self, cert_hash: str) -> Dict:
        """Verify a certificate by its hash"""
        result = self.blockchain.verify_certificate(cert_hash)
        if result:
            result["verification_timestamp"] = datetime.now().isoformat()
            result["blockchain_verified"] = True
            if result.get("block_index") is not None:
                try:
                    block = self.blockchain.chain[result["block_index"]]
                    result["block_hash"] = block.hash
                    result["block_validator"] = block.validator
                    result["block_timestamp"] = datetime.fromtimestamp(block.timestamp).isoformat()
                except (IndexError, KeyError):
                    result["block_verified"] = False
            return {"success": True, "certificate": result}
        else:
            return {"success": False, "error": "Certificate not found or invalid"}

    def search_certificates(self, search_criteria: Dict) -> List[Dict]:
        """Search for certificates by various criteria"""
        results = []
        for block in self.blockchain.chain:
            if "certificates" in block.data:
                for cert in block.data["certificates"]:
                    if cert.get("type") == "certificate":
                        match = True
                        for key, value in search_criteria.items():
                            if key in cert and cert[key].lower() != value.lower():
                                match = False
                                break
                        if match:
                            cert_hash = cert.get("cert_hash")
                            if cert_hash:
                                verification = self.verify_certificate_by_hash(cert_hash)
                                if verification["success"]:
                                    results.append(verification["certificate"])
        return results

    def revoke_certificate(self, authority_id: str, cert_hash: str, reason: str) -> Dict:
        """Revoke a certificate"""
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Institution not registered or inactive"}
        verification = self.verify_certificate_by_hash(cert_hash)
        if not verification["success"]:
            return {"success": False, "error": "Certificate not found"}
        if verification["certificate"]["status"] == "revoked":
            return {"success": False, "error": "Certificate already revoked"}
        success = self.blockchain.revoke_certificate(cert_hash, authority_id, reason)
        if success:
            return {
                "success": True,
                "message": f"Certificate {cert_hash} revoked successfully",
                "revoked_by": authority_id,
                "reason": reason,
                "revocation_date": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": "Failed to revoke certificate"}

    def get_institution_statistics(self, authority_id: str) -> Dict:
        """Get statistics for an institution"""
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Institution not registered"}
        stats = {
            "authority_id": authority_id,
            "institution_name": self.blockchain.authorities[authority_id]["institution_name"],
            "total_certificates": 0,
            "revoked_certificates": 0,
            "active_certificates": 0,
            "recent_certificates": []
        }
        for block in self.blockchain.chain:
            if block.validator == authority_id and "certificates" in block.data:
                for cert in block.data["certificates"]:
                    if cert.get("type") == "certificate":
                        stats["total_certificates"] += 1
                        cert_hash = cert.get("cert_hash")
                        if cert_hash:
                            verification = self.blockchain.verify_certificate(cert_hash)
                            if verification and verification.get("status") == "revoked":
                                stats["revoked_certificates"] += 1
                            else:
                                stats["active_certificates"] += 1
                        if len(stats["recent_certificates"]) < 10:
                            stats["recent_certificates"].append({
                                "student_name": cert.get("student_name"),
                                "degree": cert.get("degree"),
                                "issue_date": cert.get("issue_date"),
                                "cert_hash": cert.get("cert_hash")
                            })
        return {"success": True, "statistics": stats}

    def export_certificates(self, authority_id: str, format: str = "json") -> Dict:
        """Export all certificates for an institution"""
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Institution not registered"}
        certificates = []
        for block in self.blockchain.chain:
            if block.validator == authority_id and "certificates" in block.data:
                for cert in block.data["certificates"]:
                    if cert.get("type") == "certificate":
                        certificates.append(cert)
        if format.lower() == "json":
            filename = f"certificates_{authority_id}_{int(datetime.now().timestamp())}.json"
            with open(filename, 'w') as f:
                json.dump(certificates, f, indent=2)
            return {
                "success": True,
                "filename": filename,
                "count": len(certificates),
                "format": "json"
            }
        else:
            return {"success": False, "error": "Unsupported format"}

    def validate_certificate_integrity(self, certificate: Dict) -> Dict:
        """Validate the integrity of a certificate"""
        try:
            signature_valid = self.wallet_manager.validate_certificate_signature(certificate.copy())
            cert_hash = certificate.get("cert_hash")
            blockchain_valid = False
            if cert_hash:
                verification = self.blockchain.verify_certificate(cert_hash)
                blockchain_valid = verification is not None
            return {
                "success": True,
                "signature_valid": signature_valid,
                "blockchain_valid": blockchain_valid,
                "overall_valid": signature_valid and blockchain_valid,
                "certificate_hash": cert_hash
            }
        except Exception as e:
            return {"success": False, "error": f"Validation failed: {str(e)}"}


def demo_certificate_issuer():
    print("=== Certificate Issuer Demo ===")
    from blockchain import AcademicBlockchain
    from wallet import WalletManager
    blockchain = AcademicBlockchain()
    wallet_manager = WalletManager()
    issuer = CertificateIssuer(blockchain, wallet_manager)
    mit_registration = issuer.register_institution("Massachusetts Institute of Technology", "mit")
    print(f"MIT Registration: {mit_registration['success']}")
    if mit_registration["success"]:
        student_data = {
            "student_name": "Alice Johnson",
            "student_id": "MIT2024001",
            "degree": "Bachelor of Computer Science",
            "institution": "Massachusetts Institute of Technology",
            "issue_date": "2024-06-15",
            "grade": "Magna Cum Laude",
            "graduation_date": "2024-06-15"
        }
        certificate_result = issuer.issue_certificate("mit", student_data)
        print(f"Certificate issued: {certificate_result['success']}")
        if certificate_result["success"]:
            cert_hash = certificate_result["certificate_hash"]
            print(f"Certificate hash: {cert_hash}")
            verification = issuer.verify_certificate_by_hash(cert_hash)
            print(f"Certificate verified: {verification['success']}")
            stats = issuer.get_institution_statistics("mit")
            print(f"Institution stats: {stats['statistics']['total_certificates']} certificates")


if __name__ == "__main__":
    demo_certificate_issuer()



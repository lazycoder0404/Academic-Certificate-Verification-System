# Create the certificate issuer logic
certificate_issuer_code = """
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import hashlib
from blockchain import AcademicBlockchain
from wallet import AcademicWallet, WalletManager

class CertificateIssuer:
    def __init__(self, blockchain: AcademicBlockchain, wallet_manager: WalletManager):
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.institution_wallets = {}
    
    def register_institution(self, institution_name: str, authority_id: str = None) -> Dict:
        if not authority_id:
            authority_id = institution_name.lower().replace(' ', '_').replace('.', '')
        
        # Create wallet for institution
        institution_wallet = self.wallet_manager.create_wallet("institution")
        
        if not institution_wallet:
            return {"success": False, "error": "Failed to create wallet"}
        
        # Register as authority in blockchain
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
        if authority_id not in self.institution_wallets:
            return {"success": False, "error": "Institution not registered"}
        
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Invalid or inactive authority"}
        
        # Get institution wallet
        institution_wallet = self.institution_wallets[authority_id]
        
        # Validate required fields
        required_fields = ["student_name", "student_id", "degree", "institution", "issue_date"]
        for field in required_fields:
            if field not in student_data:
                return {"success": False, "error": f"Missing required field: {field}"}
        
        try:
            # Create signed certificate
            certificate = institution_wallet.create_signed_certificate(
                student_name=student_data["student_name"],
                student_id=student_data["student_id"],
                degree=student_data["degree"],
                institution=student_data["institution"],
                issue_date=student_data["issue_date"]
            )
            
            # Add additional metadata
            certificate["grade"] = student_data.get("grade", "Pass")
            certificate["graduation_date"] = student_data.get("graduation_date", student_data["issue_date"])
            certificate["certificate_id"] = self.generate_certificate_id(certificate)
            
            # Add to blockchain
            success = self.blockchain.add_certificate(certificate, authority_id)
            
            if success:
                # Mine the certificate block
                block = self.blockchain.mine_pending_certificates(authority_id)
                
                return {
                    "success": True,
                    "certificate": certificate,
                    "certificate_hash": certificate.get("cert_hash"),
                    "block_index": block.index if block else None,
                    "transaction_id": block.hash if block else None
                }
            else:
                return {"success": False, "error": "Failed to add certificate to blockchain"}
                
        except Exception as e:
            return {"success": False, "error": f"Certificate issuance failed: {str(e)}"}
    
    def generate_certificate_id(self, certificate: Dict) -> str:
        cert_string = f"{certificate['student_id']}_{certificate['degree']}_{certificate['issue_date']}"
        return hashlib.md5(cert_string.encode()).hexdigest()[:12].upper()
    
    def verify_certificate_by_hash(self, cert_hash: str) -> Dict:
        result = self.blockchain.verify_certificate(cert_hash)
        
        if result:
            # Add additional verification info
            result["verification_timestamp"] = datetime.now().isoformat()
            result["blockchain_verified"] = True
            
            # Check if certificate is in a valid block
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
        results = []
        
        # Simple search implementation - in production, use database indexing
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
                            # Get verification info
                            cert_hash = cert.get("cert_hash")
                            if cert_hash:
                                verification = self.verify_certificate_by_hash(cert_hash)
                                if verification["success"]:
                                    results.append(verification["certificate"])
        
        return results
    
    def revoke_certificate(self, authority_id: str, cert_hash: str, reason: str) -> Dict:
        if authority_id not in self.institution_wallets:
            return {"success": False, "error": "Institution not registered"}
        
        if not self.blockchain.is_valid_authority(authority_id):
            return {"success": False, "error": "Invalid or inactive authority"}
        
        # Verify certificate exists
        verification = self.verify_certificate_by_hash(cert_hash)
        if not verification["success"]:
            return {"success": False, "error": "Certificate not found"}
        
        # Check if already revoked
        if verification["certificate"]["status"] == "revoked":
            return {"success": False, "error": "Certificate already revoked"}
        
        # Revoke certificate
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
        if authority_id not in self.institution_wallets:
            return {"success": False, "error": "Institution not registered"}
        
        stats = {
            "authority_id": authority_id,
            "institution_name": self.blockchain.authorities[authority_id]["institution_name"],
            "total_certificates": 0,
            "revoked_certificates": 0,
            "active_certificates": 0,
            "recent_certificates": []
        }
        
        # Count certificates
        for block in self.blockchain.chain:
            if block.validator == authority_id and "certificates" in block.data:
                for cert in block.data["certificates"]:
                    if cert.get("type") == "certificate":
                        stats["total_certificates"] += 1
                        
                        # Check status
                        cert_hash = cert.get("cert_hash")
                        if cert_hash:
                            verification = self.blockchain.verify_certificate(cert_hash)
                            if verification and verification.get("status") == "revoked":
                                stats["revoked_certificates"] += 1
                            else:
                                stats["active_certificates"] += 1
                        
                        # Add to recent (last 10)
                        if len(stats["recent_certificates"]) < 10:
                            stats["recent_certificates"].append({
                                "student_name": cert.get("student_name"),
                                "degree": cert.get("degree"),
                                "issue_date": cert.get("issue_date"),
                                "cert_hash": cert.get("cert_hash")
                            })
        
        return {"success": True, "statistics": stats}
    
    def export_certificates(self, authority_id: str, format: str = "json") -> Dict:
        if authority_id not in self.institution_wallets:
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
        try:
            # Check signature
            signature_valid = self.wallet_manager.validate_certificate_signature(certificate.copy())
            
            # Check blockchain presence
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

# Demo function for testing certificate issuer
def demo_certificate_issuer():
    print("=== Certificate Issuer Demo ===")
    
    # Initialize components
    blockchain = AcademicBlockchain()
    wallet_manager = WalletManager()
    issuer = CertificateIssuer(blockchain, wallet_manager)
    
    # Register MIT as an institution
    mit_registration = issuer.register_institution("Massachusetts Institute of Technology", "mit")
    print(f"MIT Registration: {mit_registration['success']}")
    
    if mit_registration["success"]:
        # Issue a certificate
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
            
            # Verify the certificate
            verification = issuer.verify_certificate_by_hash(cert_hash)
            print(f"Certificate verified: {verification['success']}")
            
            # Get institution statistics
            stats = issuer.get_institution_statistics("mit")
            print(f"Institution stats: {stats['statistics']['total_certificates']} certificates")

if __name__ == "__main__":
    demo_certificate_issuer()
"""

# Write certificate_issuer.py
with open('certificate_issuer.py', 'w') as f:
    f.write(certificate_issuer_code)

print("✅ Created certificate_issuer.py successfully!")
print("Features: Institution registration, certificate issuance, verification, revocation, statistics")
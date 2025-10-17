# Let's start by creating the core blockchain implementation
# This will include the Block class, Blockchain class, and Proof of Authority consensus

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sqlite3
import os

# Create the core blockchain module - blockchain.py
blockchain_code = '''
"""
blockchain.py - Core Blockchain Implementation for Academic Certificate Verification System
Uses Proof-of-Authority consensus suitable for academic institutions
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sqlite3

class Block:
    """Represents a block in the blockchain"""
    
    def __init__(self, index: int, timestamp: float, data: Dict, 
                 previous_hash: str, validator: str = None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.validator = validator  # For PoA consensus
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary for JSON serialization"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "hash": self.hash
        }

class AcademicBlockchain:
    """
    Proof-of-Authority Blockchain for Academic Certificate Verification
    Only authorized universities can validate transactions
    """
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_certificates: List[Dict] = []
        self.authorities: Dict[str, Dict] = {}  # University validators
        self.difficulty = 4
        self.db_path = "academic_blockchain.db"
        self.init_database()
        self.create_genesis_block()
    
    def init_database(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create blocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                index INTEGER PRIMARY KEY,
                timestamp REAL,
                data TEXT,
                previous_hash TEXT,
                validator TEXT,
                hash TEXT
            )
        ''')
        
        # Create certificates table for easy lookup
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                cert_id TEXT PRIMARY KEY,
                student_name TEXT,
                student_id TEXT,
                degree TEXT,
                institution TEXT,
                issue_date TEXT,
                cert_hash TEXT,
                block_index INTEGER,
                status TEXT,
                FOREIGN KEY (block_index) REFERENCES blocks (index)
            )
        ''')
        
        # Create authorities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorities (
                authority_id TEXT PRIMARY KEY,
                institution_name TEXT,
                public_key TEXT,
                status TEXT,
                registered_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        if len(self.chain) == 0:
            genesis_data = {
                "type": "genesis",
                "message": "Academic Certificate Verification System Genesis Block",
                "created_by": "system",
                "timestamp": datetime.now().isoformat()
            }
            genesis_block = Block(0, time.time(), genesis_data, "0", "system")
            self.chain.append(genesis_block)
            self.save_block_to_db(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1] if self.chain else None
    
    def add_authority(self, authority_id: str, institution_name: str, 
                     public_key: str) -> bool:
        """Add a new university as an authority (only by system admin)"""
        if authority_id in self.authorities:
            return False
        
        authority = {
            "institution_name": institution_name,
            "public_key": public_key,
            "status": "active",
            "registered_date": datetime.now().isoformat()
        }
        
        self.authorities[authority_id] = authority
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO authorities 
            (authority_id, institution_name, public_key, status, registered_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (authority_id, institution_name, public_key, 
              authority["status"], authority["registered_date"]))
        conn.commit()
        conn.close()
        
        return True
    
    def is_valid_authority(self, authority_id: str) -> bool:
        """Check if an authority is valid and active"""
        return (authority_id in self.authorities and 
                self.authorities[authority_id]["status"] == "active")
    
    def add_certificate(self, certificate_data: Dict, validator_id: str) -> bool:
        """Add a certificate to pending pool (only by authorized validators)"""
        if not self.is_valid_authority(validator_id):
            return False
        
        # Add validator and timestamp
        certificate_data["validator"] = validator_id
        certificate_data["submission_time"] = datetime.now().isoformat()
        certificate_data["type"] = "certificate"
        
        # Generate certificate hash for integrity
        cert_content = json.dumps({
            "student_name": certificate_data.get("student_name"),
            "student_id": certificate_data.get("student_id"),
            "degree": certificate_data.get("degree"),
            "institution": certificate_data.get("institution"),
            "issue_date": certificate_data.get("issue_date")
        }, sort_keys=True)
        
        certificate_data["cert_hash"] = hashlib.sha256(cert_content.encode()).hexdigest()
        self.pending_certificates.append(certificate_data)
        
        return True
    
    def mine_pending_certificates(self, validator_id: str) -> Optional[Block]:
        """Mine a new block with pending certificates (PoA consensus)"""
        if not self.is_valid_authority(validator_id):
            return None
        
        if not self.pending_certificates:
            return None
        
        # Create new block with all pending certificates
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1 if previous_block else 0
        
        block_data = {
            "certificates": self.pending_certificates.copy(),
            "mined_by": validator_id,
            "transaction_count": len(self.pending_certificates)
        }
        
        new_block = Block(
            index=new_index,
            timestamp=time.time(),
            data=block_data,
            previous_hash=previous_block.hash if previous_block else "0",
            validator=validator_id
        )
        
        # Add block to chain
        self.chain.append(new_block)
        self.save_block_to_db(new_block)
        
        # Save certificates to database for easy lookup
        for cert in self.pending_certificates:
            self.save_certificate_to_db(cert, new_block.index)
        
        # Clear pending certificates
        self.pending_certificates = []
        
        return new_block
    
    def save_block_to_db(self, block: Block):
        """Save block to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (index, timestamp, data, previous_hash, validator, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (block.index, block.timestamp, json.dumps(block.data),
              block.previous_hash, block.validator, block.hash))
        conn.commit()
        conn.close()
    
    def save_certificate_to_db(self, cert: Dict, block_index: int):
        """Save certificate to database for quick lookup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cert_id = cert.get("cert_hash", "")
        cursor.execute('''
            INSERT OR REPLACE INTO certificates 
            (cert_id, student_name, student_id, degree, institution, 
             issue_date, cert_hash, block_index, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cert_id, cert.get("student_name"), cert.get("student_id"),
              cert.get("degree"), cert.get("institution"), 
              cert.get("issue_date"), cert.get("cert_hash"),
              block_index, "valid"))
        conn.commit()
        conn.close()
    
    def verify_certificate(self, cert_hash: str) -> Optional[Dict]:
        """Verify a certificate by its hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM certificates WHERE cert_hash = ?
        ''', (cert_hash,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "cert_id": result[0],
                "student_name": result[1],
                "student_id": result[2],
                "degree": result[3],
                "institution": result[4],
                "issue_date": result[5],
                "cert_hash": result[6],
                "block_index": result[7],
                "status": result[8],
                "verified": True
            }
        return None
    
    def revoke_certificate(self, cert_hash: str, validator_id: str, 
                          reason: str) -> bool:
        """Revoke a certificate (create revocation record)"""
        if not self.is_valid_authority(validator_id):
            return False
        
        # Create revocation record
        revocation_data = {
            "type": "revocation",
            "cert_hash": cert_hash,
            "revoked_by": validator_id,
            "reason": reason,
            "revocation_date": datetime.now().isoformat()
        }
        
        # Add to pending and mine immediately for revocations
        self.pending_certificates.append(revocation_data)
        self.mine_pending_certificates(validator_id)
        
        # Update certificate status in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE certificates SET status = 'revoked' WHERE cert_hash = ?
        ''', (cert_hash,))
        conn.commit()
        conn.close()
        
        return True
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verify validator authority (except genesis)
            if current_block.validator != "system":
                if not self.is_valid_authority(current_block.validator):
                    return False
        
        return True
    
    def get_chain_info(self) -> Dict:
        """Get blockchain statistics"""
        total_certificates = 0
        total_revocations = 0
        
        for block in self.chain:
            if "certificates" in block.data:
                for cert in block.data["certificates"]:
                    if cert.get("type") == "certificate":
                        total_certificates += 1
                    elif cert.get("type") == "revocation":
                        total_revocations += 1
        
        return {
            "total_blocks": len(self.chain),
            "total_certificates": total_certificates,
            "total_revocations": total_revocations,
            "total_authorities": len(self.authorities),
            "chain_valid": self.is_chain_valid(),
            "latest_block_hash": self.get_latest_block().hash if self.chain else None
        }
    
    def load_from_database(self):
        """Load blockchain from database on startup"""
        if not os.path.exists(self.db_path):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load authorities
        cursor.execute('SELECT * FROM authorities WHERE status = "active"')
        authorities = cursor.fetchall()
        for auth in authorities:
            self.authorities[auth[0]] = {
                "institution_name": auth[1],
                "public_key": auth[2],
                "status": auth[3],
                "registered_date": auth[4]
            }
        
        # Load blocks
        cursor.execute('SELECT * FROM blocks ORDER BY index')
        blocks = cursor.fetchall()
        self.chain = []
        
        for block_data in blocks:
            block = Block(
                index=block_data[0],
                timestamp=block_data[1],
                data=json.loads(block_data[2]),
                previous_hash=block_data[3],
                validator=block_data[4]
            )
            # Override calculated hash with stored hash
            block.hash = block_data[5]
            self.chain.append(block)
        
        conn.close()
    
    def export_chain(self, filename: str = None) -> str:
        """Export blockchain to JSON file"""
        if not filename:
            filename = f"blockchain_export_{int(time.time())}.json"
        
        export_data = {
            "blockchain": [block.to_dict() for block in self.chain],
            "authorities": self.authorities,
            "export_timestamp": datetime.now().isoformat(),
            "chain_info": self.get_chain_info()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
'''

# Write the blockchain code to file
with open('blockchain.py', 'w') as f:
    f.write(blockchain_code)

print("✅ Created blockchain.py - Core blockchain implementation with PoA consensus")
print("Features included:")
print("- Block structure with academic certificate data")
print("- Proof-of-Authority consensus for institutions")
print("- SQLite database persistence")
print("- Certificate verification and revocation")
print("- Genesis block creation")
print("- Chain validation logic")
import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3


# ---------------------------
# Block Class
# ---------------------------
class Block:
    def __init__(self, block_index: int, timestamp: float, data: Dict,
                 previous_hash: str, validator: str = None, hash_value: str = None):
        self.block_index = block_index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.validator = validator
        self.hash = hash_value if hash_value else self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "block_index": self.block_index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "block_index": self.block_index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "hash": self.hash
        }


# ---------------------------
# AcademicBlockchain Class
# ---------------------------
class AcademicBlockchain:
    def __init__(self, db_path="academic_blockchain.db"):
        self.db_path = db_path
        self.chain: List[Block] = []
        self.pending_certificates: List[Dict] = []
        self.authorities: Dict[str, Dict] = {}
        self.init_database()
        self.load_from_database()
        if len(self.chain) == 0:
            self.create_genesis_block()

    # ---------------------------
    # Database Initialization
    # ---------------------------
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_index INTEGER PRIMARY KEY,
                timestamp REAL,
                data TEXT,
                previous_hash TEXT,
                validator TEXT,
                hash TEXT
            )
        ''')

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
                FOREIGN KEY (block_index) REFERENCES blocks(block_index)
            )
        ''')

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

    # ---------------------------
    # Genesis Block
    # ---------------------------
    def create_genesis_block(self):
        genesis_data = {
            "type": "genesis",
            "message": "Academic Certificate Verification System Genesis Block",
            "created_by": "system",
            "timestamp": datetime.now().isoformat()
        }
        genesis_block = Block(0, time.time(), genesis_data, "0", "system")
        self.chain.append(genesis_block)
        self.save_block_to_db(genesis_block)

    # ---------------------------
    # Load Chain from Database
    # ---------------------------
    def load_from_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT block_index, timestamp, data, previous_hash, validator, hash FROM blocks ORDER BY block_index')
        rows = cursor.fetchall()

        self.chain = []
        for row in rows:
            block_index, timestamp, data_json, previous_hash, validator, hash_val = row
            data = json.loads(data_json)
            block = Block(block_index, float(timestamp), data, previous_hash, validator, hash_val)
            self.chain.append(block)

        # Load authorities from DB
        cursor.execute('SELECT authority_id, institution_name, public_key, status, registered_date FROM authorities')
        rows = cursor.fetchall()
        self.authorities = {}
        for row in rows:
            authority_id, name, key, status, reg_date = row
            self.authorities[authority_id] = {
                "institution_name": name,
                "public_key": key,
                "status": status,
                "registered_date": reg_date
            }

        conn.close()

    # ---------------------------
    # Save Block to Database
    # ---------------------------
    def save_block_to_db(self, block: Block):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (block_index, timestamp, data, previous_hash, validator, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (block.block_index, block.timestamp, json.dumps(block.data),
              block.previous_hash, block.validator, block.hash))
        conn.commit()
        conn.close()

    # ---------------------------
    # Save Certificate
    # ---------------------------
    def save_certificate_to_db(self, cert: Dict, block_index: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cert_id = cert.get("cert_hash", "")
        cursor.execute('''
            INSERT OR REPLACE INTO certificates 
            (cert_id, student_name, student_id, degree, institution, issue_date, cert_hash, block_index, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cert_id, cert.get("student_name"), cert.get("student_id"),
              cert.get("degree"), cert.get("institution"), cert.get("issue_date"),
              cert.get("cert_hash"), block_index, "valid"))
        conn.commit()
        conn.close()

    # ---------------------------
    # Authorities
    # ---------------------------
    def add_authority(self, authority_id: str, institution_name: str, public_key: str) -> bool:
        if authority_id in self.authorities:
            return False
        authority = {
            "institution_name": institution_name,
            "public_key": public_key,
            "status": "active",
            "registered_date": datetime.now().isoformat()
        }
        self.authorities[authority_id] = authority

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO authorities 
            (authority_id, institution_name, public_key, status, registered_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (authority_id, institution_name, public_key, authority["status"], authority["registered_date"]))
        conn.commit()
        conn.close()
        return True

    def is_valid_authority(self, authority_id: str) -> bool:
        return authority_id in self.authorities and self.authorities[authority_id]["status"] == "active"

    # ---------------------------
    # Certificates
    # ---------------------------
    def add_certificate(self, certificate_data: Dict, validator_id: str) -> bool:
        if not self.is_valid_authority(validator_id):
            return False

        certificate_data["validator"] = validator_id
        certificate_data["submission_time"] = datetime.now().isoformat()
        certificate_data["type"] = "certificate"

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
        if not self.is_valid_authority(validator_id):
            return None
        if not self.pending_certificates:
            return None

        previous_block = self.chain[-1] if self.chain else None
        new_index = previous_block.block_index + 1 if previous_block else 0

        block_data = {
            "certificates": self.pending_certificates.copy(),
            "mined_by": validator_id,
            "transaction_count": len(self.pending_certificates)
        }

        new_block = Block(
            block_index=new_index,
            timestamp=time.time(),
            data=block_data,
            previous_hash=previous_block.hash if previous_block else "0",
            validator=validator_id
        )

        self.chain.append(new_block)
        self.save_block_to_db(new_block)

        for cert in self.pending_certificates:
            self.save_certificate_to_db(cert, new_block.block_index)

        self.pending_certificates = []
        return new_block

    # ---------------------------
    # Verification and Revocation
    # ---------------------------
    def verify_certificate(self, cert_hash: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM certificates WHERE cert_hash = ?', (cert_hash,))
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

    def revoke_certificate(self, cert_hash: str, validator_id: str, reason: str) -> bool:
        if not self.is_valid_authority(validator_id):
            return False

        revocation_data = {
            "type": "revocation",
            "cert_hash": cert_hash,
            "revoked_by": validator_id,
            "reason": reason,
            "revocation_date": datetime.now().isoformat()
        }

        self.pending_certificates.append(revocation_data)
        self.mine_pending_certificates(validator_id)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE certificates SET status = "revoked" WHERE cert_hash = ?', (cert_hash,))
        conn.commit()
        conn.close()

        return True

    # ---------------------------
    # Chain Validation
    # ---------------------------
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.validator != "system":
                if not self.is_valid_authority(current_block.validator):
                    return False
        return True

    # ---------------------------
    # Utilities
    # ---------------------------
    def get_latest_block(self) -> Optional[Block]:
        return self.chain[-1] if self.chain else None

    def get_chain_info(self) -> Dict:
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

    def print_chain(self):
        print("\n--- Blockchain ---")
        for block in self.chain:
            print(f"Block Index : {block.block_index}")
            print(f"Timestamp   : {datetime.fromtimestamp(block.timestamp).isoformat()}")
            print(f"Validator   : {block.validator}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash        : {block.hash}")
            print(f"Data        : {json.dumps(block.data, indent=4)}")
            print("----------------------------")

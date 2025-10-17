# Create requirements.txt file
requirements = """Flask==2.3.3
Flask-CORS==4.0.0
cryptography==41.0.7
qrcode[pil]==7.4.2
Pillow==10.0.1
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

# Create README.md documentation
readme_content = """# 🎓 Decentralized Academic Certificate Verification System

A comprehensive Python-based blockchain project for secure, tamper-proof academic certificate management using Proof-of-Authority consensus.

## 🌟 Features

### 🧱 Core Blockchain
- **Custom Proof-of-Authority (PoA) Consensus**: Only authorized institutions can validate transactions
- **Block Structure**: Index, timestamp, certificate data, previous hash, and validator
- **Genesis Block Creation**: Automatic initialization of the blockchain
- **Chain Validation**: Complete blockchain integrity verification
- **SQLite Persistence**: Reliable data storage with database backup

### 📜 Certificate Management
- **Digital Certificate Issuance**: Universities can issue signed certificates
- **RSA Digital Signatures**: 2048-bit RSA encryption for certificate authenticity
- **Certificate Verification**: Hash-based lookup for instant verification
- **Certificate Revocation**: Tamper-proof revocation system with reasons
- **Privacy Protection**: Optional PII encryption and hash-only verification

### 👥 User Role System
- **University Admins**: Issue, verify, and revoke certificates (authenticated)
- **Students**: View and share their certificates securely
- **Employers/Third Parties**: Verify certificate authenticity instantly
- **System Admin**: Manage university registrations and system settings

### 🔐 Security & Privacy
- **RSA Key Management**: Secure wallet system for each user
- **Digital Signatures**: Non-repudiation through cryptographic signatures
- **Hash-based Verification**: Verify authenticity without exposing data
- **Authority-based Access**: Only authorized institutions can issue certificates

### 🌐 Web Interface
- **Flask REST API**: Complete API for all blockchain operations
- **Responsive Frontend**: Modern web interface for easy interaction
- **QR Code Generation**: Quick certificate sharing and verification
- **Real-time Stats**: Live blockchain statistics and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
academic-blockchain/
├── blockchain.py              # Core blockchain implementation
├── wallet.py                  # RSA wallet and digital signature system
├── certificate_issuer.py     # Certificate issuance and management logic
├── app.py                    # Flask web application and API
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── academic_blockchain.db   # SQLite database (auto-generated)
└── wallets/                 # Wallet storage directory (auto-generated)
    └── [wallet_id]/
        ├── private_key.pem
        ├── public_key.pem
        └── wallet_data.json
```

## 🎯 How to Use

### 1. Register an Institution
```bash
curl -X POST http://localhost:5000/api/institutions/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "institution_name": "Massachusetts Institute of Technology",
    "authority_id": "mit"
  }'
```

### 2. Issue a Certificate
```bash
curl -X POST http://localhost:5000/api/certificates/issue \\
  -H "Content-Type: application/json" \\
  -d '{
    "authority_id": "mit",
    "student_name": "Alice Johnson",
    "student_id": "MIT2024001",
    "degree": "Bachelor of Computer Science",
    "institution": "Massachusetts Institute of Technology",
    "issue_date": "2024-06-15",
    "grade": "Magna Cum Laude"
  }'
```

### 3. Verify a Certificate
```bash
curl http://localhost:5000/api/certificates/verify/[CERTIFICATE_HASH]
```

### 4. Search Certificates
```bash
curl "http://localhost:5000/api/certificates/search?student_name=Alice Johnson"
```

## 🔧 API Endpoints

### Blockchain Management
- `GET /api/blockchain/info` - Get blockchain statistics
- `GET /api/blockchain/export` - Export blockchain data

### Institution Management
- `POST /api/institutions/register` - Register new institution
- `GET /api/institutions/list` - List all institutions
- `GET /api/institutions/{id}/statistics` - Get institution stats

### Certificate Operations
- `POST /api/certificates/issue` - Issue new certificate
- `GET /api/certificates/verify/{hash}` - Verify certificate
- `GET /api/certificates/search` - Search certificates
- `POST /api/certificates/revoke` - Revoke certificate

### Wallet Management
- `GET /api/wallets/list` - List all wallets

## 🏗️ Technical Architecture

### Blockchain Layer
- **Consensus Algorithm**: Proof-of-Authority (PoA)
- **Block Time**: Variable (on-demand mining)
- **Data Structure**: JSON-based block storage
- **Persistence**: SQLite database with JSON columns

### Cryptographic Layer
- **Digital Signatures**: RSA-PSS with SHA-256
- **Key Size**: 2048-bit RSA keys
- **Hashing**: SHA-256 for certificate hashes
- **Signature Padding**: PSS with MGF1

### Application Layer
- **Backend**: Flask 2.3.3 with CORS support
- **Frontend**: Vanilla JavaScript with modern CSS
- **Database**: SQLite 3 with JSON1 extension
- **QR Codes**: qrcode library with PIL

## 🧪 Sample Data

The application comes with pre-registered sample institutions:
- **MIT** (Authority ID: `mit`)
- **Stanford University** (Authority ID: `stanford`)  
- **Harvard University** (Authority ID: `harvard`)

You can immediately start issuing certificates using these institutions.

## 🛡️ Security Features

### Cryptographic Security
- **RSA-2048 Digital Signatures**: Industry-standard encryption
- **SHA-256 Hashing**: Collision-resistant hash function
- **PSS Padding**: Probabilistic signature scheme for enhanced security
- **Non-repudiation**: Cryptographic proof of certificate authenticity

### Blockchain Security
- **Immutable Records**: Tamper-proof certificate storage
- **Authority Verification**: Only registered institutions can issue
- **Chain Validation**: Complete blockchain integrity checks
- **Revocation Tracking**: Transparent certificate invalidation

### Privacy Protection
- **Hash-based Verification**: Verify without exposing personal data
- **Optional PII Encryption**: Protect sensitive student information
- **Role-based Access**: Different permissions for different user types

## 🚀 Advanced Features

### QR Code Integration
- Automatic QR code generation for certificates
- Instant verification through QR scanning
- Mobile-friendly verification interface

### Real-time Monitoring
- Live blockchain statistics
- Certificate issuance tracking
- Institution activity monitoring

### Data Export
- JSON export of complete blockchain
- Certificate batch export for institutions
- Audit trail generation

## 🛠️ Development & Extension

### Adding New Features
The modular architecture makes it easy to extend:

1. **New Consensus Mechanisms**: Modify `blockchain.py`
2. **Additional Cryptography**: Extend `wallet.py`
3. **Custom Certificate Types**: Update `certificate_issuer.py`
4. **New API Endpoints**: Add routes to `app.py`

### Database Schema
The system uses SQLite with three main tables:
- `blocks`: Blockchain block storage
- `certificates`: Certificate lookup index
- `authorities`: Institution registry

### Configuration
Key configuration options in `app.py`:
- Database path
- Flask secret key
- CORS settings
- Default key sizes

## 📱 Mobile & Integration

### REST API
Complete REST API enables integration with:
- Mobile applications
- External verification systems
- University information systems
- Employment platforms

### QR Code Support
Mobile-friendly QR codes allow:
- Instant certificate verification
- Offline certificate sharing
- Easy integration with mobile apps

## 🔄 Future Enhancements

### Planned Features
- **Docker containerization** for easy deployment
- **IPFS integration** for distributed certificate storage
- **Zero-knowledge proofs** for privacy-preserving verification
- **Multi-signature support** for institutional oversight
- **Batch certificate processing** for graduation ceremonies
- **Certificate templates** with custom fields
- **Email notifications** for certificate events
- **Audit logging** with compliance reports

### Scalability
- **Layer 2 solutions** for high-throughput scenarios
- **Database sharding** for large-scale deployments
- **Caching layers** for improved performance
- **Load balancing** for production environments

## 🤝 Contributing

We welcome contributions! Areas where you can help:
- Additional consensus mechanisms
- Enhanced privacy features
- Mobile application development
- Performance optimizations
- Security audits
- Documentation improvements

## ⚠️ Important Notes

### Security Considerations
- This is a demo/educational implementation
- In production, use proper key management (HSM, key escrow)
- Implement proper authentication and authorization
- Use HTTPS for all communications
- Regular security audits recommended

### Production Deployment
For production use:
1. Enable key encryption with strong passwords
2. Use environment variables for secrets
3. Implement proper logging and monitoring
4. Set up regular database backups
5. Use production-grade web server (Gunicorn, uWSGI)

## 📄 License

This project is provided as an educational example. Use responsibly and ensure proper security measures for production deployments.

## 🆘 Support

For questions, issues, or contributions:
1. Check the API documentation in the code
2. Review the demo functions in each module
3. Test with the provided sample data
4. Ensure all dependencies are properly installed

---

**Built with ❤️ using Python, Flask, and Blockchain Technology**

*Securing Academic Integrity through Decentralized Verification*
"""

with open('README.md', 'w') as f:
    f.write(readme_content)

print("✅ Created requirements.txt and README.md successfully!")
print("📁 Complete project structure:")
print("- blockchain.py (Core blockchain with PoA consensus)")
print("- wallet.py (RSA digital signatures and key management)")
print("- certificate_issuer.py (Certificate issuance and management)")
print("- app.py (Flask web application with frontend)")
print("- requirements.txt (Python dependencies)")
print("- README.md (Complete documentation)")
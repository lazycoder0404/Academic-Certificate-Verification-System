
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
import qrcode
import io
import base64
import hashlib

# Import our custom modules
from blockchain import AcademicBlockchain
from wallet import WalletManager
from certificate_issuer import CertificateIssuer

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'academic-blockchain-secret-key-2024'

# Initialize blockchain components
blockchain = AcademicBlockchain()
wallet_manager = WalletManager()
certificate_issuer = CertificateIssuer(blockchain, wallet_manager)

# Load existing blockchain data
blockchain.load_from_database()

# Simple HTML template for the frontend
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Certificate Verification System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; }
        .card { background: white; border-radius: 10px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .form-group { margin-bottom: 1rem; }
        .form-control { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .alert { padding: 12px; border-radius: 5px; margin-bottom: 1rem; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .tabs { display: flex; margin-bottom: 1rem; }
        .tab { padding: 12px 24px; background: #e9ecef; border: none; cursor: pointer; }
        .tab.active { background: #667eea; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }
        .qr-code { text-align: center; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Academic Certificate Verification System</h1>
            <p>Decentralized blockchain-based certificate management with Proof-of-Authority consensus</p>
        </div>

        <!-- Blockchain Stats -->
        <div class="stats">
            <div class="stat-card">
                <h3>Total Blocks</h3>
                <p id="totalBlocks">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>Total Certificates</h3>
                <p id="totalCerts">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>Active Institutions</h3>
                <p id="totalInstitutions">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>Chain Status</h3>
                <p id="chainStatus">Loading...</p>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('verify')">🔍 Verify Certificate</button>
            <button class="tab" onclick="showTab('issue')">📜 Issue Certificate</button>
            <button class="tab" onclick="showTab('register')">🏛️ Register Institution</button>
            <button class="tab" onclick="showTab('search')">🔎 Search Certificates</button>
        </div>

        <!-- Verify Certificate Tab -->
        <div id="verify" class="tab-content active">
            <div class="card">
                <h2>Verify Academic Certificate</h2>
                <div class="form-group">
                    <label>Certificate Hash:</label>
                    <input type="text" id="certHash" class="form-control" placeholder="Enter certificate hash to verify">
                </div>
                <button class="btn" onclick="verifyCertificate()">Verify Certificate</button>
                <div id="verifyResult"></div>
            </div>
        </div>

        <!-- Issue Certificate Tab -->
        <div id="issue" class="tab-content">
            <div class="card">
                <h2>Issue New Certificate</h2>
                <form id="issueForm">
                    <div class="form-group">
                        <label>Institution ID:</label>
                        <input type="text" id="authorityId" class="form-control" placeholder="e.g., mit, stanford">
                    </div>
                    <div class="form-group">
                        <label>Student Name:</label>
                        <input type="text" id="studentName" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Student ID:</label>
                        <input type="text" id="studentId" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Degree:</label>
                        <input type="text" id="degree" class="form-control" placeholder="e.g., Bachelor of Computer Science">
                    </div>
                    <div class="form-group">
                        <label>Institution:</label>
                        <input type="text" id="institution" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Issue Date:</label>
                        <input type="date" id="issueDate" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Grade (Optional):</label>
                        <input type="text" id="grade" class="form-control" placeholder="e.g., Magna Cum Laude">
                    </div>
                    <button type="button" class="btn" onclick="issueCertificate()">Issue Certificate</button>
                </form>
                <div id="issueResult"></div>
            </div>
        </div>

        <!-- Register Institution Tab -->
        <div id="register" class="tab-content">
            <div class="card">
                <h2>Register Academic Institution</h2>
                <div class="form-group">
                    <label>Institution Name:</label>
                    <input type="text" id="institutionName" class="form-control">
                </div>
                <div class="form-group">
                    <label>Institution ID (Optional):</label>
                    <input type="text" id="institutionId" class="form-control" placeholder="Leave empty for auto-generation">
                </div>
                <button class="btn" onclick="registerInstitution()">Register Institution</button>
                <div id="registerResult"></div>
            </div>
        </div>

        <!-- Search Certificates Tab -->
        <div id="search" class="tab-content">
            <div class="card">
                <h2>Search Certificates</h2>
                <div class="form-group">
                    <label>Student Name:</label>
                    <input type="text" id="searchName" class="form-control">
                </div>
                <div class="form-group">
                    <label>Institution:</label>
                    <input type="text" id="searchInstitution" class="form-control">
                </div>
                <button class="btn" onclick="searchCertificates()">Search</button>
                <div id="searchResults"></div>
            </div>
        </div>
    </div>

    <script>
        // Tab functionality
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // Load blockchain stats
        async function loadStats() {
            try {
                const response = await fetch('/api/blockchain/info');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('totalBlocks').textContent = data.info.total_blocks;
                    document.getElementById('totalCerts').textContent = data.info.total_certificates;
                    document.getElementById('totalInstitutions').textContent = data.info.total_authorities;
                    document.getElementById('chainStatus').textContent = data.info.chain_valid ? '✅ Valid' : '❌ Invalid';
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Verify certificate
        async function verifyCertificate() {
            const certHash = document.getElementById('certHash').value;
            if (!certHash) {
                showResult('verifyResult', 'Please enter a certificate hash', false);
                return;
            }

            try {
                const response = await fetch('/api/certificates/verify/' + certHash);
                const data = await response.json();

                if (data.success) {
                    const cert = data.certificate;
                    showResult('verifyResult', `
                        <div class="alert-success">
                            <h3>✅ Certificate Verified</h3>
                            <p><strong>Student:</strong> ${cert.student_name}</p>
                            <p><strong>Degree:</strong> ${cert.degree}</p>
                            <p><strong>Institution:</strong> ${cert.institution}</p>
                            <p><strong>Issue Date:</strong> ${cert.issue_date}</p>
                            <p><strong>Status:</strong> ${cert.status}</p>
                            <p><strong>Block Index:</strong> ${cert.block_index}</p>
                        </div>
                    `, true);
                } else {
                    showResult('verifyResult', data.error, false);
                }
            } catch (error) {
                showResult('verifyResult', 'Verification failed: ' + error.message, false);
            }
        }

        // Issue certificate
        async function issueCertificate() {
            const formData = {
                student_name: document.getElementById('studentName').value,
                student_id: document.getElementById('studentId').value,
                degree: document.getElementById('degree').value,
                institution: document.getElementById('institution').value,
                issue_date: document.getElementById('issueDate').value,
                grade: document.getElementById('grade').value
            };
            const authorityId = document.getElementById('authorityId').value;

            if (!authorityId || !formData.student_name || !formData.degree) {
                showResult('issueResult', 'Please fill in required fields', false);
                return;
            }

            try {
                const response = await fetch('/api/certificates/issue', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({authority_id: authorityId, ...formData})
                });
                const data = await response.json();

                if (data.success) {
                    showResult('issueResult', `
                        <div class="alert-success">
                            <h3>✅ Certificate Issued Successfully</h3>
                            <p><strong>Certificate Hash:</strong> ${data.certificate_hash}</p>
                            <p><strong>Transaction ID:</strong> ${data.transaction_id}</p>
                            <div class="qr-code">
                                <img src="data:image/png;base64,${data.qr_code}" alt="Certificate QR Code">
                                <p>QR Code for Certificate Verification</p>
                            </div>
                        </div>
                    `, true);
                    document.getElementById('issueForm').reset();
                } else {
                    showResult('issueResult', data.error, false);
                }
            } catch (error) {
                showResult('issueResult', 'Issuance failed: ' + error.message, false);
            }
        }

        // Register institution
        async function registerInstitution() {
            const name = document.getElementById('institutionName').value;
            const id = document.getElementById('institutionId').value;

            if (!name) {
                showResult('registerResult', 'Please enter institution name', false);
                return;
            }

            try {
                const response = await fetch('/api/institutions/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({institution_name: name, authority_id: id})
                });
                const data = await response.json();

                if (data.success) {
                    showResult('registerResult', `
                        <div class="alert-success">
                            <h3>✅ Institution Registered</h3>
                            <p><strong>Authority ID:</strong> ${data.authority_id}</p>
                            <p><strong>Wallet ID:</strong> ${data.wallet_id}</p>
                        </div>
                    `, true);
                    document.getElementById('institutionName').value = '';
                    document.getElementById('institutionId').value = '';
                } else {
                    showResult('registerResult', data.error, false);
                }
            } catch (error) {
                showResult('registerResult', 'Registration failed: ' + error.message, false);
            }
        }

        // Search certificates
        async function searchCertificates() {
            const name = document.getElementById('searchName').value;
            const institution = document.getElementById('searchInstitution').value;

            if (!name && !institution) {
                showResult('searchResults', 'Please enter search criteria', false);
                return;
            }

            try {
                const params = new URLSearchParams();
                if (name) params.append('student_name', name);
                if (institution) params.append('institution', institution);

                const response = await fetch('/api/certificates/search?' + params.toString());
                const data = await response.json();

                if (data.success) {
                    if (data.certificates.length > 0) {
                        let html = '<div class="alert-success"><h3>Search Results:</h3>';
                        data.certificates.forEach(cert => {
                            html += `
                                <div style="border: 1px solid #ddd; padding: 1rem; margin: 1rem 0; border-radius: 5px;">
                                    <p><strong>Student:</strong> ${cert.student_name}</p>
                                    <p><strong>Degree:</strong> ${cert.degree}</p>
                                    <p><strong>Institution:</strong> ${cert.institution}</p>
                                    <p><strong>Issue Date:</strong> ${cert.issue_date}</p>
                                    <p><strong>Status:</strong> ${cert.status}</p>
                                    <p><strong>Hash:</strong> ${cert.cert_hash}</p>
                                </div>
                            `;
                        });
                        html += '</div>';
                        showResult('searchResults', html, true);
                    } else {
                        showResult('searchResults', 'No certificates found', false);
                    }
                } else {
                    showResult('searchResults', data.error, false);
                }
            } catch (error) {
                showResult('searchResults', 'Search failed: ' + error.message, false);
            }
        }

        // Utility function to show results
        function showResult(elementId, message, isSuccess) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert ${isSuccess ? 'alert-success' : 'alert-danger'}">${message}</div>`;
        }

        // Load stats on page load
        loadStats();
        setInterval(loadStats, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

# API Routes

@app.route('/api/blockchain/info')
def blockchain_info():
    try:
        info = blockchain.get_chain_info()
        return jsonify({"success": True, "info": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/institutions/register', methods=['POST'])
def register_institution():
    try:
        data = request.get_json()
        institution_name = data.get('institution_name')
        authority_id = data.get('authority_id')

        if not institution_name:
            return jsonify({"success": False, "error": "Institution name is required"})

        result = certificate_issuer.register_institution(institution_name, authority_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/institutions/list')
def list_institutions():
    try:
        authorities = {}
        for authority_id, authority_info in blockchain.authorities.items():
            authorities[authority_id] = {
                "institution_name": authority_info["institution_name"],
                "status": authority_info["status"],
                "registered_date": authority_info["registered_date"]
            }
        return jsonify({"success": True, "institutions": authorities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/certificates/issue', methods=['POST'])
def issue_certificate():
    try:
        data = request.get_json()
        authority_id = data.pop('authority_id', None)

        if not authority_id:
            return jsonify({"success": False, "error": "Authority ID is required"})

        result = certificate_issuer.issue_certificate(authority_id, data)

        # Generate QR code for the certificate hash
        if result["success"]:
            cert_hash = result["certificate_hash"]
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"VERIFY:{cert_hash}")
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()

            result["qr_code"] = qr_base64

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/certificates/verify/<cert_hash>')
def verify_certificate(cert_hash):
    try:
        result = certificate_issuer.verify_certificate_by_hash(cert_hash)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/certificates/search')
def search_certificates():
    try:
        search_criteria = {}
        for key in ['student_name', 'student_id', 'degree', 'institution']:
            value = request.args.get(key)
            if value:
                search_criteria[key] = value

        if not search_criteria:
            return jsonify({"success": False, "error": "No search criteria provided"})

        certificates = certificate_issuer.search_certificates(search_criteria)
        return jsonify({"success": True, "certificates": certificates})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/certificates/revoke', methods=['POST'])
def revoke_certificate():
    try:
        data = request.get_json()
        authority_id = data.get('authority_id')
        cert_hash = data.get('cert_hash')
        reason = data.get('reason', 'No reason provided')

        if not authority_id or not cert_hash:
            return jsonify({"success": False, "error": "Authority ID and certificate hash are required"})

        result = certificate_issuer.revoke_certificate(authority_id, cert_hash, reason)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/institutions/<authority_id>/statistics')
def institution_statistics(authority_id):
    try:
        result = certificate_issuer.get_institution_statistics(authority_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/blockchain/export')
def export_blockchain():
    try:
        filename = blockchain.export_chain()
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/wallets/list')
def list_wallets():
    try:
        wallets = wallet_manager.list_wallets()
        return jsonify({"success": True, "wallets": wallets})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🎓 Academic Certificate Verification System")
    print("=" * 50)
    print("Starting Flask application...")
    print("Frontend: http://localhost:5000")
    print("API Base: http://localhost:5000/api/")
    print("=" * 50)

    # Initialize sample data for demo
    try:
        # Register sample institutions
        print("Setting up sample institutions...")

        # MIT
        mit_result = certificate_issuer.register_institution("Massachusetts Institute of Technology", "mit")
        if mit_result["success"]:
            print(f"✅ MIT registered as authority: {mit_result['authority_id']}")

        # Stanford
        stanford_result = certificate_issuer.register_institution("Stanford University", "stanford")
        if stanford_result["success"]:
            print(f"✅ Stanford registered as authority: {stanford_result['authority_id']}")

        # Harvard
        harvard_result = certificate_issuer.register_institution("Harvard University", "harvard")
        if harvard_result["success"]:
            print(f"✅ Harvard registered as authority: {harvard_result['authority_id']}")

    except Exception as e:
        print(f"⚠️ Error setting up sample data: {e}")

    print("\n🚀 Application ready! Open http://localhost:5000 in your browser")

    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)

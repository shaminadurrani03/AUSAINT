from flask import Blueprint, request, jsonify, send_file
from models.report import Report
from extensions import db
from middleware.auth import require_auth
from services.credential_leak_service import CredentialLeakService
from services.network_intelligence_service import NetworkIntelligenceService
from services.sherlock_service import SherlockService
import uuid
import os
import requests
from datetime import datetime
import traceback
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intelligence_bp = Blueprint('intelligence', __name__)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize services
credential_leak_service = CredentialLeakService()
network_intelligence_service = NetworkIntelligenceService()
sherlock_service = SherlockService()

@intelligence_bp.route('/reports', methods=['GET'])
@require_auth
def get_reports():
    try:
        logger.info(f"Getting reports for user: {request.user_id}")
        reports = Report.query.filter_by(user_id=request.user_id).order_by(Report.created_at.desc()).all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error getting reports: {str(e)}\n{error_details}")
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/reports/<report_id>', methods=['GET'])
@require_auth
def get_report(report_id):
    try:
        logger.info(f"Getting report {report_id} for user: {request.user_id}")
        report = Report.query.filter_by(id=report_id, user_id=request.user_id).first_or_404()
        return jsonify(report.to_dict())
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error getting report: {str(e)}\n{error_details}")
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/reports', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
async def create_report():
    try:
        logger.info("Received report creation request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        report_type = data.get('report_type')
        target = data.get('target')
        
        if not report_type or not target:
            logger.error("Missing required fields")
            return jsonify({'error': 'Report type and target are required'}), 400
            
        # Create new report
        report_id = str(uuid.uuid4())
        report = Report(
            id=report_id,
            user_id=request.user_id,
            report_type=report_type,
            target=target,
            status='processing'
        )
        db.session.add(report)
        db.session.commit()
        
        # Process report based on type
        try:
            if report_type == 'credential_leak':
                result = await credential_leak_service.check_credential_leaks(target)
            elif report_type == 'ip_lookup':
                result = await network_intelligence_service.lookup_ip(target)
            elif report_type == 'domain_analysis':
                result = await network_intelligence_service.analyze_domain(target)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Update report with results
            report.status = 'completed'
            report.result = result
            db.session.commit()
            
            return jsonify({
                'success': True,
                'report_id': report_id,
                'status': 'completed',
                'result': result
            })
            
        except Exception as e:
            # Update report with error
            report.status = 'failed'
            report.result = {'error': str(e)}
            db.session.commit()
            raise
            
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error creating report: {str(e)}\n{error_details}")
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/credential-leak', methods=['POST'])
@limiter.limit("10 per minute")
def check_credential_leak():
    try:
        logger.info("Received credential leak check request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'email' not in data:
            return jsonify({"error": "Email is required"}), 400
            
        email = data['email']
        logger.info(f"Checking credential leaks for email: {email}")
        
        result = credential_leak_service.check_leaks(email)
        logger.info(f"Leak check results: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in credential leak check: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/reports/<report_id>/download', methods=['GET'])
@require_auth
def download_report(report_id):
    try:
        logger.info(f"Downloading report {report_id} for user: {request.user_id}")
        report = Report.query.filter_by(id=report_id, user_id=request.user_id).first_or_404()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            # Write report data to the file
            report_data = {
                'report_id': report.id,
                'report_type': report.report_type,
                'target': report.target,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'result': report.result
            }
            json.dump(report_data, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        # Generate filename
        filename = f"report_{report.report_type}_{report.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Send the file
        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error downloading report: {str(e)}\n{error_details}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

@intelligence_bp.route('/netint/ip', methods=['GET'])
@limiter.limit("30 per minute")
def lookup_ip():
    try:
        ip = request.args.get('ip')
        if not ip:
            return jsonify({"error": "IP address is required"}), 400
            
        result = network_intelligence_service.lookup_ip(ip)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in IP lookup: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/netint/domain/whois', methods=['GET'])
@limiter.limit("30 per minute")
def lookup_whois():
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
            
        result = network_intelligence_service.lookup_whois(domain)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in WHOIS lookup: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/netint/domain/subdomains', methods=['GET'])
@limiter.limit("30 per minute")
def find_subdomains():
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
            
        result = network_intelligence_service.find_subdomains(domain)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in subdomain search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/netint/domain/dns', methods=['GET'])
@limiter.limit("30 per minute")
def lookup_dns():
    try:
        domain = request.args.get('domain')
        record_type = request.args.get('type', 'A')
        
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
            
        result = network_intelligence_service.lookup_dns(domain, record_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in DNS lookup: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/netint/domain/analyze', methods=['GET'])
@limiter.limit("20 per minute")
def analyze_domain():
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
            
        result = network_intelligence_service.analyze_domain(domain)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in domain analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@intelligence_bp.route('/sherlock', methods=['POST'])
@limiter.limit("10 per minute")
async def search_username():
    try:
        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify({"error": "Username is required"}), 400
            
        username = data['username'].strip()
        if not username:
            return jsonify({"error": "Username cannot be empty"}), 400
            
        # Validate username format
        if not all(c.isalnum() or c in '._-' for c in username):
            return jsonify({"error": "Invalid username format"}), 400
            
        result = await sherlock_service.search_username(username)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in username search: {str(e)}")
        return jsonify({"error": str(e)}), 500 
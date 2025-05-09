from flask import Blueprint, request, jsonify
from models.report import Report
from extensions import db
from middleware.auth import require_auth
from services.credential_leak_service import CredentialLeakService
import uuid
import os
import requests
from datetime import datetime
import traceback
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intelligence_bp = Blueprint('intelligence', __name__)
limiter = Limiter(key_func=get_remote_address)

# Initialize service
credential_leak_service = CredentialLeakService()

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

@intelligence_bp.route('/credential-leak', methods=['POST'])
@limiter.limit("10 per minute")
async def credential_leak_check():
    try:
        logger.info("Received credential leak check request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        email = data.get('email')
        password = data.get('password')  # Optional
        
        if not email:
            logger.error("No email provided in request")
            return jsonify({'error': 'Email is required'}), 400

        # Check for credential leaks
        logger.info(f"Checking credential leaks for email: {email}")
        leak_results = await credential_leak_service.check_credential_leaks(email)
        logger.info(f"Leak check results: {leak_results}")
        
        # If password is provided, check for password leaks
        password_results = None
        if password:
            logger.info("Checking password leaks")
            password_results = await credential_leak_service.check_password_leak(password)
            logger.info(f"Password check results: {password_results}")

        return jsonify({
            'status': 'completed',
            'result': {
                'email_leaks': leak_results,
                'password_leak': password_results
            }
        })

    except Exception as e:
        error_details = str(e)
        logger.error(f"Error in credential_leak_check: {error_details}")
        return jsonify({
            'success': False,
            'error': error_details
        }), 500 
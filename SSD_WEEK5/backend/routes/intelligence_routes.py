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
@require_auth
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

        # Create a new report
        report = Report(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            report_type='credential_leak',
            target=email,
            status='processing',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        logger.info(f"Created new report with ID: {report.id}")
        
        db.session.add(report)
        db.session.commit()
        logger.info("Report saved to database")

        try:
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

            if leak_results.get('success'):
                report.status = 'completed'
                report.result = {
                    'email_leaks': leak_results,
                    'password_leak': password_results
                }
                logger.info("Report completed successfully")
            else:
                report.status = 'failed'
                report.result = {
                    'error': leak_results.get('error', 'Failed to check credential leaks'),
                    'details': traceback.format_exc()
                }
                logger.error(f"Report failed: {report.result}")
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error during leak check: {str(e)}\n{error_details}")
            report.status = 'failed'
            report.result = {
                'error': str(e),
                'details': error_details
            }

        db.session.commit()
        logger.info("Updated report in database")
        
        return jsonify({
            'id': report.id,
            'status': report.status,
            'result': report.result
        })

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in credential_leak_check: {str(e)}\n{error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500 
from flask import Blueprint, request, jsonify
from models.report import Report
from extensions import db
from middleware.auth import require_auth
import uuid
import os
import requests
from datetime import datetime

intelligence_bp = Blueprint('intelligence', __name__)

@intelligence_bp.route('/reports', methods=['GET'])
@require_auth
def get_reports():
    reports = Report.query.filter_by(user_id=request.user_id).order_by(Report.created_at.desc()).all()
    return jsonify([{
        'id': report.id,
        'report_type': report.report_type,
        'target': report.target,
        'status': report.status,
        'result': report.result,
        'created_at': report.created_at.isoformat(),
        'updated_at': report.updated_at.isoformat()
    } for report in reports])

@intelligence_bp.route('/reports/<report_id>', methods=['GET'])
@require_auth
def get_report(report_id):
    report = Report.query.filter_by(id=report_id, user_id=request.user_id).first_or_404()
    return jsonify({
        'id': report.id,
        'report_type': report.report_type,
        'target': report.target,
        'status': report.status,
        'result': report.result,
        'created_at': report.created_at.isoformat(),
        'updated_at': report.updated_at.isoformat()
    })

@intelligence_bp.route('/intelligence/email', methods=['POST'])
@require_auth
def email_intelligence():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    report = Report(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        report_type='email',
        target=email,
        status='processing'
    )
    db.session.add(report)
    db.session.commit()

    # Call Supabase function
    try:
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/functions/v1/email_phone_intelligence",
            json={'email': email},
            headers={'Authorization': f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"}
        )
        if response.status_code == 200:
            report.status = 'completed'
            report.result = response.json()
        else:
            report.status = 'failed'
            report.result = {'error': 'Failed to process email intelligence'}
    except Exception as e:
        report.status = 'failed'
        report.result = {'error': str(e)}

    db.session.commit()
    return jsonify({
        'id': report.id,
        'status': report.status
    })

@intelligence_bp.route('/intelligence/ip', methods=['POST'])
@require_auth
def ip_intelligence():
    data = request.get_json()
    ip = data.get('ip')
    if not ip:
        return jsonify({'error': 'IP address is required'}), 400

    report = Report(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        report_type='ip',
        target=ip,
        status='processing'
    )
    db.session.add(report)
    db.session.commit()

    # Call Supabase function
    try:
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/functions/v1/ip_domain_intelligence",
            json={'ip': ip},
            headers={'Authorization': f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"}
        )
        if response.status_code == 200:
            report.status = 'completed'
            report.result = response.json()
        else:
            report.status = 'failed'
            report.result = {'error': 'Failed to process IP intelligence'}
    except Exception as e:
        report.status = 'failed'
        report.result = {'error': str(e)}

    db.session.commit()
    return jsonify({
        'id': report.id,
        'status': report.status
    })

@intelligence_bp.route('/intelligence/social', methods=['POST'])
@require_auth
def social_intelligence():
    data = request.get_json()
    username = data.get('username')
    platform = data.get('platform')
    if not username or not platform:
        return jsonify({'error': 'Username and platform are required'}), 400

    report = Report(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        report_type='social',
        target=f"{platform}:{username}",
        status='processing'
    )
    db.session.add(report)
    db.session.commit()

    # Call Supabase function
    try:
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/functions/v1/social_media_intelligence",
            json={'username': username, 'platform': platform},
            headers={'Authorization': f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"}
        )
        if response.status_code == 200:
            report.status = 'completed'
            report.result = response.json()
        else:
            report.status = 'failed'
            report.result = {'error': 'Failed to process social media intelligence'}
    except Exception as e:
        report.status = 'failed'
        report.result = {'error': str(e)}

    db.session.commit()
    return jsonify({
        'id': report.id,
        'status': report.status
    })

@intelligence_bp.route('/intelligence/web', methods=['POST'])
@require_auth
def web_intelligence():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    report = Report(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        report_type='web',
        target=url,
        status='processing'
    )
    db.session.add(report)
    db.session.commit()

    # Call Supabase function
    try:
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/functions/v1/web_scraping",
            json={'url': url},
            headers={'Authorization': f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"}
        )
        if response.status_code == 200:
            report.status = 'completed'
            report.result = response.json()
        else:
            report.status = 'failed'
            report.result = {'error': 'Failed to process web scraping'}
    except Exception as e:
        report.status = 'failed'
        report.result = {'error': str(e)}

    db.session.commit()
    return jsonify({
        'id': report.id,
        'status': report.status
    }) 
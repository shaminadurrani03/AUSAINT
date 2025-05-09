from flask import Blueprint, request, jsonify
from services.network_intelligence_service import NetworkIntelligenceService
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
network_intelligence_bp = Blueprint('network_intelligence', __name__)

# Initialize service
network_service = NetworkIntelligenceService()

@network_intelligence_bp.route('/api/netint/ip', methods=['GET'])
async def lookup_ip():
    """
    Lookup IP geolocation information
    """
    try:
        ip = request.args.get('ip')
        if not ip:
            return jsonify({
                'success': False,
                'error': 'IP address is required'
            }), 400

        result = await network_service.lookup_ip(ip)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in IP lookup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@network_intelligence_bp.route('/api/netint/domain/whois', methods=['GET'])
async def lookup_whois():
    """
    Lookup WHOIS information for a domain
    """
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({
                'success': False,
                'error': 'Domain is required'
            }), 400

        result = await network_service.lookup_whois(domain)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in WHOIS lookup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@network_intelligence_bp.route('/api/netint/domain/subdomains', methods=['GET'])
async def find_subdomains():
    """
    Find subdomains for a domain
    """
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({
                'success': False,
                'error': 'Domain is required'
            }), 400

        result = await network_service.find_subdomains(domain)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in subdomain enumeration endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@network_intelligence_bp.route('/api/netint/domain/dns', methods=['GET'])
async def lookup_dns():
    """
    Lookup DNS records for a domain
    """
    try:
        domain = request.args.get('domain')
        record_type = request.args.get('type', 'A')
        
        if not domain:
            return jsonify({
                'success': False,
                'error': 'Domain is required'
            }), 400

        result = await network_service.lookup_dns(domain, record_type)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in DNS lookup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@network_intelligence_bp.route('/api/netint/domain/analyze', methods=['GET'])
async def analyze_domain():
    """
    Perform comprehensive domain analysis
    """
    try:
        domain = request.args.get('domain')
        if not domain:
            return jsonify({
                'success': False,
                'error': 'Domain is required'
            }), 400

        result = await network_service.analyze_domain(domain)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in domain analysis endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 
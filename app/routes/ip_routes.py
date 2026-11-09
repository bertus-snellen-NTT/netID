"""
IP Address routes for the netID Flask application
Handles all IP-related endpoints
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.ip_service import (
    validate_ip_address,
    get_reverse_dns,
    get_ip_geolocation,
    get_ip_network_info
)

ip_routes = Blueprint('ip', __name__, template_folder='../templates')


@ip_routes.route('/')
def ip_index():
    """IP service landing page."""
    return render_template('ip/index.html')


@ip_routes.route('/validate', methods=['GET', 'POST'])
def ip_validate():
    """Validate an IP address."""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '')
    else:
        ip_address = request.args.get('ip_address', '')
    
    if ip_address:
        result = validate_ip_address(ip_address)
        return render_template('ip/validate.html', result=result)
    
    return render_template('ip/validate.html', result=None)


@ip_routes.route('/reverse-dns', methods=['GET', 'POST'])
def ip_reverse_dns():
    """Perform reverse DNS lookup on an IP address."""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '')
    else:
        ip_address = request.args.get('ip_address', '')
    
    if ip_address:
        dns_result = get_reverse_dns(ip_address)
        validation = validate_ip_address(ip_address)
        return render_template('ip/reverse_dns.html',
                             ip_address=ip_address,
                             dns_result=dns_result,
                             validation=validation)
    
    return render_template('ip/reverse_dns.html',
                         ip_address=None,
                         dns_result=None,
                         validation=None)


@ip_routes.route('/geolocation', methods=['GET', 'POST'])
def ip_geolocation():
    """Get geolocation information for an IP address."""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '')
    else:
        ip_address = request.args.get('ip_address', '')
    
    if ip_address:
        geo_result = get_ip_geolocation(ip_address)
        validation = validate_ip_address(ip_address)
        return render_template('ip/geolocation.html',
                             ip_address=ip_address,
                             geo_result=geo_result,
                             validation=validation)
    
    return render_template('ip/geolocation.html',
                         ip_address=None,
                         geo_result=None,
                         validation=None)


@ip_routes.route('/network', methods=['GET', 'POST'])
def ip_network():
    """Get network information for an IP address."""
    if request.method == 'POST':
        ip_address = request.form.get('ip_address', '')
        prefix_length = request.form.get('prefix_length', '24')
    else:
        ip_address = request.args.get('ip_address', '')
        prefix_length = request.args.get('prefix_length', '24')
    
    try:
        prefix_length = int(prefix_length)
    except ValueError:
        prefix_length = 24
    
    if ip_address:
        network_result = get_ip_network_info(ip_address, prefix_length)
        validation = validate_ip_address(ip_address)
        return render_template('ip/network.html',
                             ip_address=ip_address,
                             prefix_length=prefix_length,
                             network_result=network_result,
                             validation=validation)
    
    return render_template('ip/network.html',
                         ip_address=None,
                         prefix_length=24,
                         network_result=None,
                         validation=None)


@ip_routes.route('/api/validate', methods=['GET', 'POST'])
def api_ip_validate():
    """API endpoint for IP validation."""
    if request.method == 'POST':
        data = request.get_json()
        ip_address = data.get('ip_address', '') if data else ''
    else:
        ip_address = request.args.get('ip_address', '')
    
    if ip_address:
        result = validate_ip_address(ip_address)
        return jsonify(result)
    
    return jsonify({'error': 'No IP address provided'}), 400

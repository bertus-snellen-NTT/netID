"""
MAC Address routes for the netID Flask application
Handles all MAC-related endpoints
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.mac_service import (
    validate_mac_address,
    get_mac_info,
    format_mac_address,
    get_mac_vendor
)

mac_routes = Blueprint('mac', __name__, template_folder='../templates')


@mac_routes.route('/')
def mac_index():
    """MAC service landing page."""
    return render_template('mac/index.html')


@mac_routes.route('/validate', methods=['GET', 'POST'])
def mac_validate():
    """Validate a MAC address."""
    if request.method == 'POST':
        mac_address = request.form.get('mac_address', '')
    else:
        mac_address = request.args.get('mac_address', '')
    
    if mac_address:
        result = validate_mac_address(mac_address)
        return render_template('mac/validate.html', result=result)
    
    return render_template('mac/validate.html', result=None)


@mac_routes.route('/info', methods=['GET', 'POST'])
def mac_info():
    """Get detailed information about a MAC address."""
    if request.method == 'POST':
        mac_address = request.form.get('mac_address', '')
    else:
        mac_address = request.args.get('mac_address', '')
    
    if mac_address:
        validation = validate_mac_address(mac_address)
        if validation['valid']:
            info = get_mac_info(validation['normalized'])
            return render_template('mac/info.html',
                                 mac_address=mac_address,
                                 validation=validation,
                                 info=info)
        else:
            return render_template('mac/info.html',
                                 mac_address=mac_address,
                                 validation=validation,
                                 info=None)
    
    return render_template('mac/info.html',
                         mac_address=None,
                         validation=None,
                         info=None)


@mac_routes.route('/format', methods=['GET', 'POST'])
def mac_format():
    """Format a MAC address."""
    if request.method == 'POST':
        mac_address = request.form.get('mac_address', '')
        separator = request.form.get('separator', ':')
        uppercase = request.form.get('uppercase', 'true').lower() == 'true'
    else:
        mac_address = request.args.get('mac_address', '')
        separator = request.args.get('separator', ':')
        uppercase = request.args.get('uppercase', 'true').lower() == 'true'
    
    if mac_address:
        validation = validate_mac_address(mac_address)
        formatted = format_mac_address(mac_address, separator, uppercase) if validation['valid'] else None
        return render_template('mac/format.html',
                             mac_address=mac_address,
                             separator=separator,
                             uppercase=uppercase,
                             validation=validation,
                             formatted=formatted)
    
    return render_template('mac/format.html',
                         mac_address=None,
                         separator=':',
                         uppercase=True,
                         validation=None,
                         formatted=None)


@mac_routes.route('/vendor', methods=['GET', 'POST'])
def mac_vendor():
    """Get vendor information for a MAC address."""
    if request.method == 'POST':
        mac_address = request.form.get('mac_address', '')
    else:
        mac_address = request.args.get('mac_address', '')
    
    if mac_address:
        validation = validate_mac_address(mac_address)
        vendor_result = get_mac_vendor(mac_address) if validation['valid'] else {'error': 'Invalid MAC address'}
        return render_template('mac/vendor.html',
                             mac_address=mac_address,
                             validation=validation,
                             vendor_result=vendor_result)
    
    return render_template('mac/vendor.html',
                         mac_address=None,
                         validation=None,
                         vendor_result=None)


@mac_routes.route('/api/validate', methods=['GET', 'POST'])
def api_mac_validate():
    """API endpoint for MAC validation."""
    if request.method == 'POST':
        data = request.get_json()
        mac_address = data.get('mac_address', '') if data else ''
    else:
        mac_address = request.args.get('mac_address', '')
    
    if mac_address:
        result = validate_mac_address(mac_address)
        return jsonify(result)
    
    return jsonify({'error': 'No MAC address provided'}), 400

"""
BGP AS routes for the netID Flask application
Handles all BGP-related endpoints
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.bgp_service import (
    validate_as_number,
    get_as_info,
    get_as_prefixes,
    get_as_peers,
    get_as_path
)

bgp_routes = Blueprint('bgp', __name__, template_folder='../templates')


@bgp_routes.route('/')
def bgp_index():
    """BGP service landing page."""
    return render_template('bgp/index.html')


@bgp_routes.route('/validate', methods=['GET', 'POST'])
def bgp_validate():
    """Validate a BGP AS number."""
    if request.method == 'POST':
        as_number = request.form.get('as_number', '')
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        result = validate_as_number(as_number)
        return render_template('bgp/validate.html', result=result)
    
    return render_template('bgp/validate.html', result=None)


@bgp_routes.route('/info', methods=['GET', 'POST'])
def bgp_info():
    """Get detailed information about a BGP AS."""
    if request.method == 'POST':
        as_number = request.form.get('as_number', '')
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        validation = validate_as_number(as_number)
        if validation['valid']:
            info = get_as_info(validation['asn'])
            return render_template('bgp/info.html',
                                 as_number=as_number,
                                 validation=validation,
                                 info=info)
        else:
            return render_template('bgp/info.html',
                                 as_number=as_number,
                                 validation=validation,
                                 info=None)
    
    return render_template('bgp/info.html',
                         as_number=None,
                         validation=None,
                         info=None)


@bgp_routes.route('/prefixes', methods=['GET', 'POST'])
def bgp_prefixes():
    """Get IP prefixes for a BGP AS."""
    if request.method == 'POST':
        as_number = request.form.get('as_number', '')
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        validation = validate_as_number(as_number)
        if validation['valid']:
            prefixes_result = get_as_prefixes(validation['asn'])
            return render_template('bgp/prefixes.html',
                                 as_number=as_number,
                                 validation=validation,
                                 prefixes_result=prefixes_result)
        else:
            return render_template('bgp/prefixes.html',
                                 as_number=as_number,
                                 validation=validation,
                                 prefixes_result=None)
    
    return render_template('bgp/prefixes.html',
                         as_number=None,
                         validation=None,
                         prefixes_result=None)


@bgp_routes.route('/peers', methods=['GET', 'POST'])
def bgp_peers():
    """Get BGP peers for an AS."""
    if request.method == 'POST':
        as_number = request.form.get('as_number', '')
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        validation = validate_as_number(as_number)
        if validation['valid']:
            peers_result = get_as_peers(validation['asn'])
            return render_template('bgp/peers.html',
                                 as_number=as_number,
                                 validation=validation,
                                 peers_result=peers_result)
        else:
            return render_template('bgp/peers.html',
                                 as_number=as_number,
                                 validation=validation,
                                 peers_result=None)
    
    return render_template('bgp/peers.html',
                         as_number=None,
                         validation=None,
                         peers_result=None)


@bgp_routes.route('/path', methods=['GET', 'POST'])
def bgp_path():
    """Get AS path information for a BGP AS."""
    if request.method == 'POST':
        as_number = request.form.get('as_number', '')
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        validation = validate_as_number(as_number)
        if validation['valid']:
            path_result = get_as_path(validation['asn'])
            return render_template('bgp/path.html',
                                 as_number=as_number,
                                 validation=validation,
                                 path_result=path_result)
        else:
            return render_template('bgp/path.html',
                                 as_number=as_number,
                                 validation=validation,
                                 path_result=None)
    
    return render_template('bgp/path.html',
                         as_number=None,
                         validation=None,
                         path_result=None)


@bgp_routes.route('/api/validate', methods=['GET', 'POST'])
def api_bgp_validate():
    """API endpoint for AS number validation."""
    if request.method == 'POST':
        data = request.get_json()
        as_number = data.get('as_number', '') if data else ''
    else:
        as_number = request.args.get('as_number', '')
    
    if as_number:
        result = validate_as_number(as_number)
        return jsonify(result)
    
    return jsonify({'error': 'No AS number provided'}), 400

"""
Main routes for the netID Flask application
Handles the landing page and general navigation
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.ip_service import get_all_ip_functions
from app.services.mac_service import get_all_mac_functions
from app.services.bgp_service import get_all_bgp_functions

main_routes = Blueprint('main', __name__, template_folder='../templates')


@main_routes.route('/', methods=['GET', 'POST'])
@main_routes.route('/index', methods=['GET', 'POST'])
def index():
    """Landing page showing all available functions."""
    ip_functions = get_all_ip_functions()
    mac_functions = get_all_mac_functions()
    bgp_functions = get_all_bgp_functions()
    
    # Handle form submission from the search form
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        search_type = request.form.get('type', 'auto')
        
        if query:
            if search_type == 'auto':
                if is_valid_ip_format(query):
                    session['last_ip'] = query
                    return redirect(url_for('main.select_ip_tool'))
                elif is_valid_mac_format(query):
                    return redirect(url_for('mac.mac_validate', mac_address=query))
                elif is_valid_as_format(query):
                    return redirect(url_for('bgp.bgp_validate', as_number=query))
                else:
                    return redirect(url_for('ip.ip_validate', ip_address=query))
            elif search_type == 'ip':
                session['last_ip'] = query
                return redirect(url_for('main.select_ip_tool'))
            elif search_type == 'mac':
                return redirect(url_for('mac.mac_validate', mac_address=query))
            elif search_type == 'bgp':
                return redirect(url_for('bgp.bgp_validate', as_number=query))
    
    return render_template('index.html',
                         ip_functions=ip_functions,
                         mac_functions=mac_functions,
                         bgp_functions=bgp_functions)


@main_routes.route('/about')
def about():
    """About page with information about the application."""
    return render_template('about.html')


@main_routes.route('/select-ip-tool', methods=['GET', 'POST'])
def select_ip_tool():
    """Show selection of IP tools for a specific IP address."""
    ip_address = session.get('last_ip', '')
    
    if not ip_address:
        return redirect(url_for('main.index'))
    
    ip_functions = get_all_ip_functions()
    
    if request.method == 'POST':
        selected_tool = request.form.get('tool')
        if selected_tool:
            # Redirect to the appropriate tool with the IP
            route_map = {
                'validate_ip_address': 'ip.ip_validate',
                'get_reverse_dns': 'ip.ip_reverse_dns',
                'get_ip_geolocation': 'ip.ip_geolocation',
                'get_ip_network_info': 'ip.ip_network',
                'get_ip_whois_info': 'ip.ip_whois'
            }
            endpoint = route_map.get(selected_tool)
            if endpoint:
                return redirect(url_for(endpoint, ip_address=ip_address))
    
    return render_template('select_ip_tool.html',
                         ip_address=ip_address,
                         ip_functions=ip_functions)


@main_routes.route('/clear-ip')
def clear_ip():
    """Clear the stored IP address from session."""
    session.pop('last_ip', None)
    return redirect(url_for('main.index'))


def is_valid_ip_format(query: str) -> bool:
    """Check if a string looks like an IP address."""
    import ipaddress
    try:
        ipaddress.ip_address(query)
        return True
    except ValueError:
        return False


def is_valid_mac_format(query: str) -> bool:
    """Check if a string looks like a MAC address."""
    import re
    mac_patterns = [
        r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$',
        r'^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$',
        r'^([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})$',
        r'^([0-9A-Fa-f]{12})$',
    ]
    for pattern in mac_patterns:
        if re.match(pattern, query):
            return True
    return False


def is_valid_as_format(query: str) -> bool:
    """Check if a string looks like an AS number."""
    import re
    as_pattern = r'^(as)?\d+$'
    return bool(re.match(as_pattern, query, re.IGNORECASE))

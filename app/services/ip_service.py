"""
IP Address Service Module
Provides discrete functions for IP address operations
"""

import ipaddress
import socket
import subprocess
from typing import Dict, Any, Optional, List


def validate_ip_address(ip_str: str) -> Dict[str, Any]:
    """Validate an IP address and return information about it."""
    result = {
        'input': ip_str,
        'valid': False,
        'type': None,
        'version': None,
        'error': None,
        'info': {}
    }
    
    try:
        ip = ipaddress.ip_address(ip_str)
        result['valid'] = True
        result['type'] = 'IPv4' if ip.version == 4 else 'IPv6'
        result['version'] = ip.version
        
        if ip.version == 4:
            result['info'] = {
                'is_private': ip.is_private,
                'is_loopback': ip.is_loopback,
                'is_link_local': ip.is_link_local,
                'is_multicast': ip.is_multicast,
                'is_reserved': ip.is_reserved,
                'packed': ip.packed.hex(),
                'integer': int(ip),
                'reverse_dns': get_reverse_dns(ip_str)
            }
        else:
            result['info'] = {
                'is_private': ip.is_private,
                'is_loopback': ip.is_loopback,
                'is_link_local': ip.is_link_local,
                'is_multicast': ip.is_multicast,
                'is_reserved': ip.is_reserved,
                'packed': ip.packed.hex(),
                'integer': int(ip),
                'compressed': ip.compressed,
                'exploded': ip.exploded
            }
            
    except ValueError as e:
        result['error'] = str(e)
    
    return result


def get_reverse_dns(ip_str: str) -> Optional[str]:
    """Perform reverse DNS lookup on an IP address."""
    try:
        return socket.gethostbyaddr(ip_str)[0]
    except (socket.herror, socket.gaierror):
        return None


def get_ip_geolocation(ip_str: str) -> Dict[str, Any]:
    """Get geolocation information for an IP address."""
    return {
        'ip': ip_str,
        'country': 'Unknown (API required)',
        'region': 'Unknown (API required)',
        'city': 'Unknown (API required)',
        'latitude': None,
        'longitude': None,
        'isp': 'Unknown (API required)',
        'organization': 'Unknown (API required)',
        'note': 'This function requires an external geolocation API'
    }


def get_ip_network_info(ip_str: str, prefix_len: int = 24) -> Dict[str, Any]:
    """Get network information for an IP address with a given prefix length."""
    result = {
        'input': ip_str,
        'prefix_length': prefix_len,
        'error': None,
        'network': None,
        'broadcast': None,
        'first_host': None,
        'last_host': None,
        'total_hosts': None
    }
    
    try:
        network = ipaddress.ip_network(f"{ip_str}/{prefix_len}", strict=False)
        result['network'] = str(network)
        result['broadcast'] = str(network.broadcast_address) if network.version == 4 else None
        result['first_host'] = str(network.network_address + 1) if network.version == 4 else None
        result['last_host'] = str(network.broadcast_address - 1) if network.version == 4 else None
        result['total_hosts'] = network.num_addresses
        
    except ValueError as e:
        result['error'] = str(e)
    
    return result


def get_ip_whois_info(ip_str: str) -> Dict[str, Any]:
    """
    Get WHOIS information for a public IP address.
    
    For public IPs, this function:
    1. Checks if the IP is public (not private/reserved)
    2. Queries IANA WHOIS to find the appropriate RIR
    3. Follows up with the RIR's WHOIS server for detailed information
    
    Args:
        ip_str: The IP address to lookup
        
    Returns:
        Dictionary containing WHOIS information
    """
    result = {
        'ip': ip_str,
        'is_public': False,
        'registrar': None,
        'rir': None,
        'rir_server': None,
        'details': {},
        'raw_iana': None,
        'raw_rir': None,
        'error': None
    }
    
    # First validate and check if public
    validation = validate_ip_address(ip_str)
    if not validation['valid']:
        result['error'] = 'Invalid IP address'
        return result
    
    # Check if it's a public IP
    info = validation.get('info', {})
    is_public = not any([
        info.get('is_private', False),
        info.get('is_loopback', False),
        info.get('is_link_local', False),
        info.get('is_multicast', False),
        info.get('is_reserved', False)
    ])
    
    if not is_public:
        result['is_public'] = False
        result['error'] = 'IP address is not public (private/reserved)'
        return result
    
    result['is_public'] = True
    
    # Query IANA WHOIS
    iana_result = query_whois_server('whois.iana.org', ip_str)
    if iana_result.get('error'):
        result['error'] = f"IANA WHOIS query failed: {iana_result['error']}"
        return result
    
    result['raw_iana'] = iana_result.get('raw', '')
    
    # Parse IANA response to find RIR
    rir_info = parse_iana_response(iana_result.get('raw', ''))
    result['rir'] = rir_info.get('rir')
    result['rir_server'] = rir_info.get('server')
    result['registrar'] = rir_info.get('registrar')
    
    if not rir_info.get('server'):
        result['error'] = 'Could not determine RIR from IANA response'
        return result
    
    # Query the RIR's WHOIS server
    rir_result = query_whois_server(rir_info.get('server'), ip_str)
    if rir_result.get('error'):
        result['error'] = f"RIR WHOIS query failed: {rir_result['error']}"
        return result
    
    result['raw_rir'] = rir_result.get('raw', '')
    result['details'] = parse_rir_response(rir_result.get('raw', ''), rir_info.get('rir', ''))
    
    return result


def query_whois_server(server: str, query: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Query a WHOIS server.
    
    Args:
        server: WHOIS server hostname
        query: Query string (IP address or domain)
        timeout: Connection timeout in seconds
        
    Returns:
        Dictionary with 'raw' response or 'error'
    """
    import socket
    
    result = {'raw': None, 'error': None}
    
    try:
        # Create a socket connection to the WHOIS server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((server, 43))
        
        # Send the query
        s.sendall(f"{query}\r\n".encode('utf-8'))
        
        # Receive the response
        response = b''
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        
        s.close()
        result['raw'] = response.decode('utf-8', errors='ignore')
        
    except socket.gaierror as e:
        result['error'] = f"DNS resolution failed: {e}"
    except socket.timeout:
        result['error'] = f"Connection timeout after {timeout} seconds"
    except ConnectionRefusedError:
        result['error'] = "Connection refused by WHOIS server"
    except Exception as e:
        result['error'] = f"WHOIS query failed: {e}"
    
    return result


def parse_iana_response(response: str) -> Dict[str, Any]:
    """
    Parse IANA WHOIS response to extract RIR information.
    
    Args:
        response: Raw IANA WHOIS response
        
    Returns:
        Dictionary with RIR information
    """
    result = {
        'rir': None,
        'server': None,
        'registrar': None,
        'allocation': None
    }
    
    if not response:
        return result
    
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%') or line.startswith('#'):
            continue
        
        # Look for referral lines
        if 'refer:' in line.lower():
            # Example: refer:        whois.arin.net
            parts = line.split(':', 1)
            if len(parts) > 1:
                referral = parts[1].strip()
                result['server'] = referral
                
                # Determine RIR from server
                if 'arin' in referral.lower():
                    result['rir'] = 'ARIN'
                    result['registrar'] = 'ARIN (American Registry for Internet Numbers)'
                elif 'ripe' in referral.lower():
                    result['rir'] = 'RIPE NCC'
                    result['registrar'] = 'RIPE NCC (Reseaux IP Europeens)'
                elif 'apnic' in referral.lower():
                    result['rir'] = 'APNIC'
                    result['registrar'] = 'APNIC (Asia-Pacific Network Information Centre)'
                elif 'lacnic' in referral.lower():
                    result['rir'] = 'LACNIC'
                    result['registrar'] = 'LACNIC (Latin American and Caribbean IP Address Regional Registry)'
                elif 'afrinic' in referral.lower():
                    result['rir'] = 'AFRINIC'
                    result['registrar'] = 'AFRINIC (African Network Information Centre)'
        
        # Look for allocation/assignment lines
        if 'inetnum:' in line.lower() or 'netname:' in line.lower() or 'desc:' in line.lower():
            if 'allocation' not in result or not result['allocation']:
                result['allocation'] = line
    
    return result


def parse_rir_response(response: str, rir: str) -> Dict[str, Any]:
    """
    Parse RIR WHOIS response to extract useful information.
    
    Args:
        response: Raw RIR WHOIS response
        rir: The RIR name (ARIN, RIPE, APNIC, etc.)
        
    Returns:
        Dictionary with parsed information
    """
    result = {
        'netname': None,
        'inetnum': None,
        'country': None,
        'organization': None,
        'abuse_contact': None,
        'created': None,
        'updated': None,
        'status': None,
        'allocation_size': None,
        'raw_fields': {}
    }
    
    if not response:
        return result
    
    lines = response.split('\n')
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%') or line.startswith('#') or line.startswith('remarks:'):
            continue
        
        # Check for key: value patterns
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()
            
            result['raw_fields'][key] = value
            
            # Map common fields
            if key == 'netname':
                result['netname'] = value
            elif key == 'inetnum' or key == 'inet6num' or key == 'cidr':
                result['inetnum'] = value
            elif key == 'country':
                result['country'] = value
            elif key == 'organisation' or key == 'org-name' or key == 'owner' or key == 'descr':
                if not result['organization']:
                    result['organization'] = value
            elif key == 'abuse-c' or key == 'abuse-mailbox':
                result['abuse_contact'] = value
            elif key == 'created':
                result['created'] = value
            elif key == 'last-modified' or key == 'updated':
                result['updated'] = value
            elif key == 'status':
                result['status'] = value
            elif key == 'allocated' or key == 'allocation':
                result['allocation_size'] = value
    
    return result


def get_all_ip_functions() -> list:
    """Return a list of all available IP functions."""
    return [
        {
            'name': 'validate_ip_address',
            'description': 'Validate an IP address and get basic information',
            'parameters': ['ip_address'],
            'endpoint': '/ip/validate'
        },
        {
            'name': 'get_reverse_dns',
            'description': 'Perform reverse DNS lookup on an IP address',
            'parameters': ['ip_address'],
            'endpoint': '/ip/reverse-dns'
        },
        {
            'name': 'get_ip_geolocation',
            'description': 'Get geolocation information for an IP address',
            'parameters': ['ip_address'],
            'endpoint': '/ip/geolocation'
        },
        {
            'name': 'get_ip_network_info',
            'description': 'Get network information for an IP address',
            'parameters': ['ip_address', 'prefix_length'],
            'endpoint': '/ip/network'
        },
        {
            'name': 'get_ip_whois_info',
            'description': 'Get WHOIS information for a public IP address (IANA + RIR lookup)',
            'parameters': ['ip_address'],
            'endpoint': '/ip/whois'
        }
    ]

"""
IP Address Service Module
Provides discrete functions for IP address operations
"""

import ipaddress
import socket
from typing import Dict, Any, Optional


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
        }
    ]

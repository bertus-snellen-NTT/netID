"""
BGP AS Service Module
Provides discrete functions for BGP Autonomous System operations
"""

import re
from typing import Dict, Any


def validate_as_number(as_str: str) -> Dict[str, Any]:
    """Validate a BGP Autonomous System number."""
    result = {
        'input': as_str,
        'valid': False,
        'asn': None,
        'type': None,
        'error': None,
        'info': {}
    }
    
    clean = as_str.upper().replace('AS', '').strip()
    
    try:
        asn = int(clean)
        
        if 0 <= asn <= 65535:
            result['valid'] = True
            result['asn'] = asn
            result['type'] = '2-byte'
            result['info'] = get_as_info(asn)
        elif 65536 <= asn <= 4294967295:
            result['valid'] = True
            result['asn'] = asn
            result['type'] = '4-byte'
            result['info'] = get_as_info(asn)
        else:
            result['error'] = 'ASN out of valid range (0-4294967295)'
            
    except ValueError:
        result['error'] = 'Invalid ASN format - must be a number'
    
    return result


def get_as_info(asn: int) -> Dict[str, Any]:
    """Get information about a BGP Autonomous System."""
    known_as = {
        1: {'name': 'LVLT-1', 'description': 'Level 3 Communications', 'country': 'US', 'type': 'Tier 1'},
        15169: {'name': 'Google', 'description': 'Google LLC', 'country': 'US', 'type': 'Content'},
        16509: {'name': 'Amazon', 'description': 'Amazon.com', 'country': 'US', 'type': 'Content'},
        3356: {'name': 'Level3', 'description': 'Level 3 Communications', 'country': 'US', 'type': 'Tier 1'},
        6453: {'name': 'TATA', 'description': 'Tata Communications', 'country': 'IN', 'type': 'Tier 1'},
        6939: {'name': 'Hurricane Electric', 'description': 'Hurricane Electric', 'country': 'US', 'type': 'Tier 1'},
        7018: {'name': 'AT&T', 'description': 'AT&T Services', 'country': 'US', 'type': 'Tier 1'},
        2914: {'name': 'NTT', 'description': 'NTT America', 'country': 'US', 'type': 'Tier 1'},
    }
    
    info = known_as.get(asn, {'name': 'Unknown', 'description': 'Unknown', 'country': 'Unknown', 'type': 'Unknown'})
    asn_size = '2-byte' if asn <= 65535 else '4-byte'
    
    return {
        'asn': asn,
        'asn_size': asn_size,
        'name': info.get('name', 'Unknown'),
        'description': info.get('description', 'Unknown'),
        'country': info.get('country', 'Unknown'),
        'type': info.get('type', 'Unknown'),
        'is_private': asn in [64512, 65534] or (64512 <= asn <= 65534),
        'is_reserved': asn == 0 or asn == 65535 or (65536 <= asn <= 65551)
    }


def get_as_prefixes(asn: int) -> Dict[str, Any]:
    """Get IP prefixes announced by a BGP AS."""
    return {
        'asn': asn,
        'ipv4_prefixes': [],
        'ipv6_prefixes': [],
        'total_prefixes': 0,
        'note': 'This function requires a BGP API for real data'
    }


def get_as_peers(asn: int) -> Dict[str, Any]:
    """Get BGP peers for an AS."""
    return {
        'asn': asn,
        'peers': [],
        'peer_count': 0,
        'note': 'This function requires a BGP API for real peer data'
    }


def get_as_path(asn: int) -> Dict[str, Any]:
    """Get sample AS paths for an AS."""
    return {
        'asn': asn,
        'as_paths': [],
        'note': 'This function requires a BGP API for real AS path data'
    }


def get_all_bgp_functions() -> list:
    """Return a list of all available BGP AS functions."""
    return [
        {
            'name': 'validate_as_number',
            'description': 'Validate a BGP AS number and get basic information',
            'parameters': ['as_number'],
            'endpoint': '/bgp/validate'
        },
        {
            'name': 'get_as_info',
            'description': 'Get detailed information about a BGP AS',
            'parameters': ['as_number'],
            'endpoint': '/bgp/info'
        },
        {
            'name': 'get_as_prefixes',
            'description': 'Get IP prefixes announced by a BGP AS',
            'parameters': ['as_number'],
            'endpoint': '/bgp/prefixes'
        },
        {
            'name': 'get_as_peers',
            'description': 'Get BGP peers for an AS',
            'parameters': ['as_number'],
            'endpoint': '/bgp/peers'
        },
        {
            'name': 'get_as_path',
            'description': 'Get sample AS paths for an AS',
            'parameters': ['as_number'],
            'endpoint': '/bgp/path'
        }
    ]

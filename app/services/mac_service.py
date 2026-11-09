"""
MAC Address Service Module
Provides discrete functions for MAC address operations
"""

import re
from typing import Dict, Any, Optional


def validate_mac_address(mac_str: str) -> Dict[str, Any]:
    """Validate a MAC address and return information about it."""
    result = {
        'input': mac_str,
        'valid': False,
        'format': None,
        'normalized': None,
        'error': None,
        'info': {}
    }
    
    mac_formats = [
        r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$',
        r'^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$',
        r'^([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})$',
        r'^([0-9A-Fa-f]{12})$',
        r'^([0-9A-Fa-f]{2}[:]){7}([0-9A-Fa-f]{2})$',
        r'^([0-9A-Fa-f]{2}[-]){7}([0-9A-Fa-f]{2})$',
    ]
    
    normalized = None
    for fmt in mac_formats:
        if re.match(fmt, mac_str):
            clean = re.sub(r'[^0-9A-Fa-f]', '', mac_str)
            if len(clean) == 12:
                normalized = ':'.join([clean[i:i+2] for i in range(0, 12, 2)]).upper()
                result['format'] = 'MAC-48/EUI-48'
            elif len(clean) == 16:
                normalized = ':'.join([clean[i:i+2] for i in range(0, 16, 2)]).upper()
                result['format'] = 'EUI-64'
            
            result['valid'] = True
            result['normalized'] = normalized
            result['info'] = get_mac_info(normalized)
            break
    
    if not result['valid']:
        result['error'] = 'Invalid MAC address format'
    
    return result


def get_mac_info(mac_str: str) -> Dict[str, Any]:
    """Get information about a MAC address."""
    clean = re.sub(r'[^0-9A-Fa-f]', '', mac_str).upper()
    oui = clean[:6] if len(clean) >= 6 else clean
    
    known_ouis = {
        '000C29': 'VMware', '005056': 'VMware', '000569': 'VMware',
        '0003FF': 'Microsoft', '001C42': 'Parallels', '001D0F': 'Samsung',
        '001E68': 'Apple', '00215A': 'Hewlett Packard', '002312': 'Dell',
        '00254B': 'Apple', '0050F2': 'Microsoft', '080027': 'Cadmus Computer Systems',
        '08002B': 'Digital Equipment Corporation', '08005A': 'IBM',
        '3C5AB4': 'Google', '3C970E': 'Wistron InfoComm(Kunshan)Co.,Ltd.',
        '3CD92B': 'Hewlett Packard', '54EE75': 'Apple', '606BBD': 'Samsung Electronics Co.,Ltd',
        '7831C1': 'Apple', '784F43': 'Apple', '843835': 'Apple',
        'A483E7': 'Microsoft', 'B827EB': 'Raspberry Pi Foundation',
        'C82A14': 'Apple', 'D83062': 'Apple', 'E0DB55': 'Dell', 'F01898': 'Apple',
    }
    
    manufacturer = known_ouis.get(oui, 'Unknown')
    first_byte = int(clean[:2], 16)
    is_multicast = (first_byte & 0x01) == 1
    is_local = ((first_byte >> 1) & 0x01) == 1
    
    return {
        'oui': f"{oui[:2]}:{oui[2:4]}:{oui[4:6]}",
        'manufacturer': manufacturer,
        'is_multicast': is_multicast,
        'is_local': is_local,
        'length': len(clean),
        'type': 'EUI-48' if len(clean) == 12 else 'EUI-64'
    }


def format_mac_address(mac_str: str, separator: str = ':', uppercase: bool = True) -> Optional[str]:
    """Format a MAC address with a specific separator."""
    validation = validate_mac_address(mac_str)
    if not validation['valid']:
        return None
    
    clean = re.sub(r'[^0-9A-Fa-f]', '', mac_str)
    
    if separator == ':':
        formatted = ':'.join([clean[i:i+2] for i in range(0, len(clean), 2)])
    elif separator == '-':
        formatted = '-'.join([clean[i:i+2] for i in range(0, len(clean), 2)])
    elif separator == '.':
        formatted = '.'.join([clean[i:i+4] for i in range(0, len(clean), 4)])
    else:
        formatted = clean
    
    return formatted.upper() if uppercase else formatted.lower()


def get_mac_vendor(mac_str: str) -> Dict[str, Any]:
    """Get vendor information for a MAC address."""
    validation = validate_mac_address(mac_str)
    if not validation['valid']:
        return {'error': 'Invalid MAC address'}
    
    info = validation['info']
    return {
        'mac': mac_str,
        'oui': info.get('oui'),
        'manufacturer': info.get('manufacturer'),
        'note': 'This function requires an OUI database for complete information'
    }


def get_all_mac_functions() -> list:
    """Return a list of all available MAC functions."""
    return [
        {
            'name': 'validate_mac_address',
            'description': 'Validate a MAC address and get basic information',
            'parameters': ['mac_address'],
            'endpoint': '/mac/validate'
        },
        {
            'name': 'get_mac_info',
            'description': 'Get detailed information about a MAC address',
            'parameters': ['mac_address'],
            'endpoint': '/mac/info'
        },
        {
            'name': 'format_mac_address',
            'description': 'Format a MAC address with a specific separator',
            'parameters': ['mac_address', 'separator', 'uppercase'],
            'endpoint': '/mac/format'
        },
        {
            'name': 'get_mac_vendor',
            'description': 'Get vendor information for a MAC address',
            'parameters': ['mac_address'],
            'endpoint': '/mac/vendor'
        }
    ]

"""
Utility functions for common operations across the application.
"""
from typing import Optional


def get_selection_key(rel_id: int) -> str:
    """
    Convert a relative ID (1-36) to a selection key string.
    
    Args:
        rel_id: Relative ID from 1 to 36
        
    Returns:
        String representation: '1'-'9' for 1-9, '0' for 10, 'a'-'z' for 11-36
    """
    if 1 <= rel_id <= 9:
        return str(rel_id)
    elif rel_id == 10:
        return "0"
    elif 11 <= rel_id <= 36:
        return chr(ord('a') + (rel_id - 11))
    else:
        return "?"


def parse_selection_key(key_val: int) -> Optional[int]:
    """
    Parse an ASCII key value to a relative selection ID.
    
    Args:
        key_val: ASCII value of the pressed key
        
    Returns:
        Relative ID (1-36) or None if not a valid selection key
    """
    # Check for numeric keys 1-9
    if ord('1') <= key_val <= ord('9'):
        return key_val - ord('0')
    
    # Check for '0' (represents 10)
    elif key_val == ord('0'):
        return 10
    
    # Check for lowercase letters a-z (11-36)
    elif ord('a') <= key_val <= ord('z'):
        return 11 + (key_val - ord('a'))
    
    # Not a valid selection key
    return None

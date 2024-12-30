from pricechecker.config import MIN_SCAN_LENGTH, MAX_SCAN_LENGTH

def handle_scan(scan_input: str) -> tuple[str | None, str | None]:
    """
    Process and validate scanner input
    Returns: (processed_value, error_message)
    """
    try:
        # Basic cleaning
        cleaned = scan_input.strip()
        
        # Remove scanner artifacts
        cleaned = cleaned.replace('\r', '').replace('\n', '')
        
        # Validate length
        if len(cleaned) < MIN_SCAN_LENGTH:
            return None, f"Scan too short (minimum {MIN_SCAN_LENGTH} characters)"
            
        if len(cleaned) > MAX_SCAN_LENGTH:
            return None, f"Scan too long (maximum {MAX_SCAN_LENGTH} characters)"
            
        # Validate characters
        if not cleaned.isprintable():
            return None, "Contains invalid characters"
            
        return cleaned, None
        
    except Exception as e:
        return None, f"Error processing scan: {str(e)}"
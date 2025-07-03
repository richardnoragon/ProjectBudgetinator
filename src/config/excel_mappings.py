"""Excel cell mapping configurations for ProjectBudgetinator."""

from typing import Dict, Any

# Partner worksheet cell mappings
PARTNER_CELL_MAPPINGS: Dict[str, str] = {
    "project_partner_number": "D2:E2",
    "partner_identification_code": "D4:E4",
    "partner_acronym": "D3:E3",
    "name_of_beneficiary": "D13",
    "country": "D5:E5",
    "role": "D6:E6",
    # WP fields (cells C18 through Q18)
    "wp1": "C18",
    "wp2": "D18",
    "wp3": "E18",
    "wp4": "F18",
    "wp5": "G18",
    "wp6": "H18",
    "wp7": "I18",
    "wp8": "J18",
    "wp9": "K18",
    "wp10": "L18",
    "wp11": "M18",
    "wp12": "N18",
    "wp13": "O18",
    "wp14": "P18",
    "wp15": "Q18"
}

# Field validation rules
FIELD_VALIDATION = {
    "wp": {
        "type": float,
        "min_value": 0.0,
        "max_value": 1000000.0,  # Adjust max value as needed
        "error_message": "WP value must be a non-negative number less than {max_value}"
    },
    "partner_identification_code": {
        "required": True,
        "min_length": 3,
        "max_length": 50,
        "error_message": "Partner ID must be between {min_length} and {max_length} characters"
    },
    "name_of_beneficiary": {
        "required": True,
        "min_length": 2,
        "max_length": 100,
        "error_message": "Beneficiary name must be between {min_length} and {max_length} characters"
    },
    "country": {
        "required": True,
        "min_length": 2,
        "max_length": 100,
        "error_message": "Country must be between {min_length} and {max_length} characters"
    }
}

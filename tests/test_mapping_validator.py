import pytest
from ui.components.mapping import MappingValidator
from config.settings import REQUIRED_INTERNAL_COLUMNS


def test_mapping_validator_with_empty_dict():
    validator = MappingValidator(REQUIRED_INTERNAL_COLUMNS)
    result = validator.validate_mapping({})
    assert not result['is_valid']
    assert len(result['missing_columns']) > 0


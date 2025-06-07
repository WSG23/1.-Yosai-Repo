import pytest

from utils.validators import CSVValidator, MappingValidator
from core.exceptions import ValidationError
from config import FILE_LIMITS, REQUIRED_INTERNAL_COLUMNS


def test_validate_file_size_passes():
    small_size = FILE_LIMITS['max_file_size'] - 1
    assert CSVValidator.validate_file_size(small_size)


def test_validate_file_size_raises():
    big_size = FILE_LIMITS['max_file_size'] + 1
    with pytest.raises(ValidationError):
        CSVValidator.validate_file_size(big_size)


def test_mapping_completeness_passes():
    mapping = {k: k for k in REQUIRED_INTERNAL_COLUMNS.keys()}
    is_complete, missing = MappingValidator.validate_mapping_completeness(mapping)
    assert is_complete
    assert missing == []


def test_mapping_completeness_missing_keys():
    mapping = {}
    is_complete, missing = MappingValidator.validate_mapping_completeness(mapping)
    assert not is_complete
    assert set(missing) == set(REQUIRED_INTERNAL_COLUMNS.keys())


def test_mapping_uniqueness_raises_on_duplicates():
    mapping = {'a': 'Timestamp', 'b': 'Timestamp'}
    with pytest.raises(ValidationError):
        MappingValidator.validate_mapping_uniqueness(mapping)

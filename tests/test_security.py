from utils.secure_validator import validate_upload_security


def test_basic_security():
    valid_csv = "user_id,door_id,timestamp\n1,101,2023-01-01 10:00:00\n2,102,2023-01-01 10:05:00"
    result = validate_upload_security(valid_csv.encode('utf-8'), 'test.csv')
    assert result['is_valid']

    malicious_exe = b'\x4D\x5A\x90\x00' + b'fake data'
    result = validate_upload_security(malicious_exe, 'fake.csv')
    assert not result['is_valid']

    script_csv = "<script>alert('xss')</script>\nuser_id,door_id\n1,101"
    result = validate_upload_security(script_csv.encode('utf-8'), 'script.csv')
    assert not result['is_valid']

    valid_content = "user_id,door_id\n1,101"
    result = validate_upload_security(valid_content.encode('utf-8'), 'test.exe')
    assert not result['is_valid']


def test_json_security():
    # Valid JSON
    valid_json = '{"user_id": 1, "door_id": 101, "timestamp": "2023-01-01 10:00:00"}'
    result = validate_upload_security(valid_json.encode('utf-8'), 'test.json')
    assert result['is_valid']

    # Malicious JSON with prototype pollution
    malicious_json = '{"__proto__": {"isAdmin": true}, "user_id": 1}'
    result = validate_upload_security(malicious_json.encode('utf-8'), 'malicious.json')
    assert not result['is_valid']

    # Excessive nesting
    deeply_nested = '{"a":' * 15 + '{}' + '}' * 15
    result = validate_upload_security(deeply_nested.encode('utf-8'), 'nested.json')
    assert not result['is_valid']

    # Invalid JSON
    invalid_json = '{"user_id": 1, "door_id": 101'
    result = validate_upload_security(invalid_json.encode('utf-8'), 'invalid.json')
    assert not result['is_valid']

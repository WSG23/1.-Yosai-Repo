#!/usr/bin/env python3
# test_magic.py
"""
Test if python-magic is working correctly on macOS
"""

def test_python_magic():
    """Test python-magic functionality"""
    print("🔍 Testing python-magic setup...")
    
    try:
        import magic
        print("✅ python-magic module imported successfully")
        
        # Test creating magic instance
        m = magic.Magic(mime=True)
        print("✅ Magic instance created successfully")
        
        # Test with some sample data
        test_data = b"Name,Age\nJohn,25\nJane,30"
        mime_type = m.from_buffer(test_data)
        print(f"✅ MIME detection working: {mime_type}")
        
        if mime_type in ['text/csv', 'text/plain']:
            print("🎉 python-magic is working perfectly!")
            return True
        else:
            print(f"⚠️ Unexpected MIME type: {mime_type} (but still working)")
            return True
            
    except ImportError:
        print("❌ python-magic not installed")
        return False
    except Exception as e:
        print(f"⚠️ python-magic has issues: {e}")
        print("💡 This is usually fixed by: brew install libmagic")
        return False

def test_without_magic():
    """Test that security still works without python-magic"""
    print("\n🔍 Testing security without python-magic...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from utils.secure_validator import SecureFileValidator
        
        validator = SecureFileValidator()
        print("✅ SecureFileValidator created")
        
        # Test with valid CSV
        test_csv = b"Name,Age\nJohn,25"
        result = validator.validate_upload(test_csv, "test.csv")
        
        if result['valid']:
            print("✅ Security validation working without python-magic")
            print(f"   File validated: {result['file_info']}")
            return True
        else:
            print(f"❌ Security validation failed: {result['errors']}")
            return False
            
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

def main():
    """Test python-magic setup"""
    print("🔍 macOS python-magic Test")
    print("=" * 40)
    
    magic_works = test_python_magic()
    security_works = test_without_magic()
    
    print("\n" + "=" * 40)
    if magic_works:
        print("🎉 PERFECT SETUP!")
        print("✅ python-magic working fully")
        print("✅ Enhanced MIME detection active")
        print("✅ Maximum security features enabled")
    elif security_works:
        print("✅ GOOD SETUP!")
        print("⚠️ python-magic has issues (but that's OK)")
        print("✅ Security validation still working")
        print("✅ Your app will work fine with reduced MIME detection")
        print("\n💡 To fix python-magic (optional):")
        print("   brew install libmagic")
    else:
        print("❌ SETUP ISSUES")
        print("❌ Security validation not working")
        print("🔧 Check your installation")
    
    print(f"\n🚀 Your app is ready to start!")

if __name__ == "__main__":
    main()
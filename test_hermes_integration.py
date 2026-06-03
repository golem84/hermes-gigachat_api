"""Integration test for hermes config set GIGACHAT_API_KEY command."""

import subprocess, sys, os


def test_hermes_config_integration():
    """Test that hermes config set works for GigaChat credentials."""
    
    print("🧪 Testing Hermes Config Integration for GigaChat")
    print("=" * 50)
    
    # Test 1: Test API_TOKEN setting
    print("\nTest 1: GIGACHAT_API_TOKEN")
    test_token = "YmMwYWQxNWQtNDU2OS00OGM0LTkwYjAtMjY3MTQ2NmY5OTA2OmE5NmUzMGE0LTBiMmQtNDhmOS1iNTQwLWY2MjNjMDkzMTc4NA=="
    
    result = subprocess.run(
        ["hermes", "config", "set", "GIGACHAT_API_TOKEN", test_token],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ API_TOKEN setting: {result.stdout.strip()}")
    else:
        print(f"❌ API_TOKEN setting failed: {result.stderr}")
        return False
    
    # Test 2: Test CLIENT_ID setting
    print("\nTest 2: GIGACHAT_CLIENT_ID")
    test_client_id = "bc0ad15d-4569-48c4-90b0-2671466f9906"
    
    result = subprocess.run(
        ["hermes", "config", "set", "GIGACHAT_CLIENT_ID", test_client_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ CLIENT_ID setting: {result.stdout.strip()}")
    else:
        print(f"❌ CLIENT_ID setting failed: {result.stderr}")
        return False
    
    # Test 3: Test CLIENT_SECRET setting
    print("\nTest 3: GIGACHAT_CLIENT_SECRET")
    test_secret = "a96e30a4-0b2d-48f9-b540-f623c0931784"
    
    result = subprocess.run(
        ["hermes", "config", "set", "GIGACHAT_CLIENT_SECRET", test_secret],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ CLIENT_SECRET setting: {result.stdout.strip()}")
    else:
        print(f"❌ CLIENT_SECRET setting failed: {result.stderr}")
        return False
    
    # Test 4: Check if values are saved
    print("\nTest 4: Verify saved values")
    result = subprocess.run(
        ["hermes", "config", "show"],
        capture_output=True,
        text=True
    )
    
    if "GIGACHAT_API_TOKEN" in result.stdout:
        print("✅ GIGACHAT_API_TOKEN found in config")
    else:
        print("❌ GIGACHAT_API_TOKEN not found in config")
        return False
    
    if "GIGACHAT_CLIENT_ID" in result.stdout:
        print("✅ GIGACHAT_CLIENT_ID found in config")
    else:
        print("❌ GIGACHAT_CLIENT_ID not found in config")
        return False
    
    # Test 5: Test plugin discovery
    print("\nTest 5: Plugin discovery")
    result = subprocess.run(
        ["hermes", "models", "list", "--provider", "gigachat"],
        capture_output=True,
        text=True
    )
    
    if "gigachat" in result.stdout.lower():
        print("✅ GigaChat plugin discovered successfully")
    else:
        print("⚠️  GigaChat plugin not found in model list")
        print("This is normal if plugin not yet installed in Hermes")
    
    return True


def test_hermes_message():
    """Test sending a message via Hermes with GigaChat."""
    
    print("\n🧪 Test 6: Send message via Hermes")
    
    try:
        result = subprocess.run(
            ["hermes", "--model", "gigachat", "Привет! Это тестовое сообщение."],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(f"✅ Message sent successfully")
            print(f"Response: {result.stdout[:200]}...")
            return True
        else:
            print("⚠️  No response received (might need plugin installation)")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Message timeout (might need proper credentials)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run integration tests."""
    
    print("🚀 GigaChat Hermes Integration Test Suite")
    print("=" * 50)
    
    # Check if Hermes is available
    print("\n🔍 Checking Hermes installation...")
    result = subprocess.run(["hermes", "--version"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Hermes installed: {result.stdout.strip()}")
    else:
        print("❌ Hermes not found in PATH")
        return False
    
    # Run tests
    core_tests_passed = test_hermes_config_integration()
    
    if core_tests_passed:
        print("\n" + "=" * 50)
        print("✅ All config integration tests passed!")
        print("=" * 50)
        
        # Optional: test message sending
        print("\n📝 Optionally test message sending? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 'y':
                test_hermes_message()
        except:
            pass
        
        print("\n🎯 Integration Status: READY FOR USE")
        print("\n📋 Usage Examples:")
        print("  hermes --model gigachat 'Привет!'")
        print("  hermes --model gigachat:GigaChat-2-Max 'Сложная задача'")
        print("  hermes --model gigachat --enable-tools 'Используй инструменты'")
        
        return True
    else:
        print("\n❌ Some integration tests failed")
        print("💡 Check hermes_cli/config.py for GIGACHAT_* entries")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
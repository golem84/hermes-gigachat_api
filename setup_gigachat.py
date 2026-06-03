"""Quick GigaChat setup script for Hermes users."""

import os, sys, base64, json


def setup_gigachat():
    """Interactive setup for GigaChat credentials."""
    
    print("🚀 GigaChat Quick Setup for Hermes")
    print("=" * 40)
    
    print("\nChoose setup method:")
    print("1. Enter API_TOKEN directly (recommended, fastest)")
    print("2. Generate from Client ID + Secret")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        setup_with_api_token()
    elif choice == "2":
        setup_with_client_credentials()
    elif choice == "3":
        print("Setup cancelled.")
    else:
        print("Invalid choice.")
        sys.exit(1)


def setup_with_api_token():
    """Setup using pre-generated API token."""
    print("\n🔑 API Token Setup")
    print("Get your token from: https://developers.sber.ru/")
    
    api_token = input("Enter GIGACHAT_API_TOKEN: ").strip()
    
    if not api_token:
        print("❌ Token cannot be empty!")
        sys.exit(1)
    
    # Validate base64 format
    try:
        decoded = base64.b64decode(api_token).decode('utf-8')
        if ':' in decoded:
            print(f"✅ Token looks valid (decodes to {decoded[:30]}...)")
        else:
            print("⚠️  Token doesn't look like client_id:secret format, but proceeding...")
    except Exception:
        print("⚠️  Token may not be valid base64, but proceeding...")
    
    # Save to .env
    save_to_env('GIGACHAT_API_TOKEN', api_token)
    
    print("\n✅ Setup complete!")
    print("💡 You can now use: hermes --model gigachat")


def setup_with_client_credentials():
    """Setup using client ID and secret."""
    print("\n🔑 Client Credentials Setup")
    print("Get your credentials from: https://developers.sber.ru/")
    
    client_id = input("Enter GIGACHAT_CLIENT_ID: ").strip()
    client_secret = input("Enter GIGACHAT_CLIENT_SECRET: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Secret are required!")
        sys.exit(1)
    
    # Generate API token
    api_token = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()
    
    print(f"\n🔄 Generated API token: {api_token[:20]}...")
    
    # Save both to .env
    save_to_env('GIGACHAT_CLIENT_ID', client_id)
    save_to_env('GIGACHAT_CLIENT_SECRET', client_secret)
    save_to_env('GIGACHAT_API_TOKEN', api_token)
    
    print("\n✅ Setup complete! All credentials saved.")
    print("💡 You can now use: hermes --model gigachat")


def save_to_env(key, value):
    """Save value to Hermes .env file."""
    try:
        # Try to find Hermes config directory
        hermes_home = os.path.expanduser("~/.hermes")
        env_file = os.path.join(hermes_home, ".env")
        
        # Read existing .env
        existing_lines = []
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                existing_lines = f.readlines()
        
        # Update or append
        updated = False
        for i, line in enumerate(existing_lines):
            if line.startswith(f"{key}="):
                existing_lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            existing_lines.append(f"{key}={value}\n")
        
        # Write back
        os.makedirs(hermes_home, exist_ok=True)
        with open(env_file, 'w') as f:
            f.writelines(existing_lines)
        
        print(f"✅ Saved {key} to {env_file}")
        
    except Exception as e:
        print(f"⚠️  Could not save {key} to .env: {e}")
        print(f"💡 Use: hermes config set {key} {value}")


def test_connection():
    """Test GigaChat connection."""
    print("\n🧪 Testing GigaChat connection...")
    
    try:
        import requests
        import uuid
        
        api_token = os.getenv("GIGACHAT_API_TOKEN")
        
        if not api_token:
            print("❌ GIGACHAT_API_TOKEN not found in environment")
            print("💡 Setup credentials first using: setup_gigachat.py")
            return False
        
        # Try to get a token
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json', 
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {api_token}'
        }
        data = b'scope=GIGACHAT_API_PERS'
        
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            print("💡 GigaChat is ready for use!")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Error: {response.text[:100]}")
            return False
            
    except ImportError:
        print("⚠️  requests library not installed: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GigaChat Setup for Hermes")
    parser.add_argument("--quick", action="store_true", help="Quick setup with API token")
    parser.add_argument("--client-creds", action="store_true", help="Setup with Client ID + Secret")
    parser.add_argument("--test", action="store_true", help="Test existing connection")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_connection()
        sys.exit(0 if success else 1)
    elif args.quick:
        setup_with_api_token()
    elif args.client_creds:
        setup_with_client_credentials()
    else:
        setup_gigachat()
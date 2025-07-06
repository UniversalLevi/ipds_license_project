#!/bin/bash

echo "🔧 Fixing indentation issues..."

# Fix the specific agent_cli.py file
cd client/agent
sed -i 's/\t/    /g' agent_cli.py

# Fix specific problematic lines
sed -i 's/^    hw_fingerprint = self.hardware_fingerprint.generate_fingerprint()/                hw_fingerprint = self.hardware_fingerprint.generate_fingerprint()/' agent_cli.py
sed -i 's/^    print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")/                print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    print(f"{Fore.CYAN}🔗 API CONNECTION TEST{Style.RESET_ALL}")/            print(f"{Fore.CYAN}🔗 API CONNECTION TEST{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    print(f"{Fore.YELLOW}🔄 Testing connection to: {self.api_url}{Style.RESET_ALL}")/            print(f"{Fore.YELLOW}🔄 Testing connection to: {self.api_url}{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    print(f"{Fore.GREEN}✅ API connection successful!{Style.RESET_ALL}")/                print(f"{Fore.GREEN}✅ API connection successful!{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    print(f"{Fore.RED}❌ API connection failed{Style.RESET_ALL}")/                print(f"{Fore.RED}❌ API connection failed{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    print(f"{Fore.RED}❌ API connection test failed: {e}{Style.RESET_ALL}")/            print(f"{Fore.RED}❌ API connection test failed: {e}{Style.RESET_ALL}")/' agent_cli.py
sed -i 's/^    fingerprint = self.hardware_fingerprint.generate_fingerprint()/                fingerprint = self.hardware_fingerprint.generate_fingerprint()/' agent_cli.py
sed -i 's/^    print(f"{Fore.WHITE}Fingerprint: {Fore.CYAN}{fingerprint}{Style.RESET_ALL}")/                print(f"{Fore.WHITE}Fingerprint: {Fore.CYAN}{fingerprint}{Style.RESET_ALL}")/' agent_cli.py

echo "✅ Fixed indentation issues in agent_cli.py"
echo "🚀 Now try running: cd client && ./start_client.sh" 
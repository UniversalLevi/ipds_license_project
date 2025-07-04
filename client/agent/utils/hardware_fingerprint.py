"""
Hardware fingerprinting utilities for the agent
"""

import platform
import subprocess
import hashlib
import uuid
import re
from typing import Dict, List, Optional

class HardwareFingerprint:
    """Hardware fingerprinting for license protection"""
    
    def __init__(self):
        """Initialize hardware fingerprinting"""
        self.system = platform.system().lower()
    
    def get_mac_addresses(self) -> List[str]:
        """Get MAC addresses of network interfaces"""
        mac_addresses = []
        
        try:
            if self.system == "windows":
                # Windows: use ipconfig
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract MAC addresses from ipconfig output
                    mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                    mac_addresses = re.findall(mac_pattern, result.stdout)
                    # Clean up the matches
                    mac_addresses = [''.join(mac) for mac in mac_addresses]
            
            elif self.system == "linux":
                # Linux: use ip link
                result = subprocess.run(['ip', 'link'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract MAC addresses from ip link output
                    mac_pattern = r'([0-9a-f]{2}:){5}[0-9a-f]{2}'
                    mac_addresses = re.findall(mac_pattern, result.stdout)
            
            elif self.system == "darwin":  # macOS
                # macOS: use ifconfig
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract MAC addresses from ifconfig output
                    mac_pattern = r'([0-9a-f]{2}:){5}[0-9a-f]{2}'
                    mac_addresses = re.findall(mac_pattern, result.stdout)
        
        except Exception as e:
            print(f"Warning: Could not get MAC addresses: {e}")
        
        # Remove duplicates and filter out invalid MACs
        valid_macs = []
        for mac in mac_addresses:
            if mac and mac != "00:00:00:00:00:00" and mac not in valid_macs:
                valid_macs.append(mac)
        
        return valid_macs
    
    def get_cpu_info(self) -> Dict[str, str]:
        """Get CPU information"""
        cpu_info = {}
        
        try:
            if self.system == "windows":
                # Windows: use wmic
                result = subprocess.run(['wmic', 'cpu', 'get', 'ProcessorId'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        cpu_info['processor_id'] = lines[1].strip()
            
            elif self.system == "linux":
                # Linux: read from /proc/cpuinfo
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        content = f.read()
                        # Extract processor ID or serial
                        processor_match = re.search(r'processor\s+:\s+(\d+)', content)
                        if processor_match:
                            cpu_info['processor_id'] = processor_match.group(1)
                except FileNotFoundError:
                    pass
            
            elif self.system == "darwin":  # macOS
                # macOS: use system_profiler
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract processor info
                    processor_match = re.search(r'Processor Name:\s+(.+)', result.stdout)
                    if processor_match:
                        cpu_info['processor_name'] = processor_match.group(1).strip()
        
        except Exception as e:
            print(f"Warning: Could not get CPU info: {e}")
        
        return cpu_info
    
    def get_disk_info(self) -> List[Dict[str, str]]:
        """Get disk information"""
        disks = []
        
        try:
            if self.system == "windows":
                # Windows: use wmic
                result = subprocess.run(['wmic', 'diskdrive', 'get', 'SerialNumber'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        serial = line.strip()
                        if serial:
                            disks.append({'serial': serial})
            
            elif self.system == "linux":
                # Linux: use lsblk or read from /sys
                try:
                    result = subprocess.run(['lsblk', '-no', 'SERIAL'], capture_output=True, text=True)
                    if result.returncode == 0:
                        serials = result.stdout.strip().split('\n')
                        for serial in serials:
                            if serial:
                                disks.append({'serial': serial})
                except FileNotFoundError:
                    pass
            
            elif self.system == "darwin":  # macOS
                # macOS: use diskutil
                result = subprocess.run(['diskutil', 'info', '/dev/disk0'], capture_output=True, text=True)
                if result.returncode == 0:
                    serial_match = re.search(r'Serial Number:\s+(.+)', result.stdout)
                    if serial_match:
                        disks.append({'serial': serial_match.group(1).strip()})
        
        except Exception as e:
            print(f"Warning: Could not get disk info: {e}")
        
        return disks
    
    def get_system_uuid(self) -> Optional[str]:
        """Get system UUID"""
        try:
            if self.system == "windows":
                # Windows: use wmic
                result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        return lines[1].strip()
            
            elif self.system == "linux":
                # Linux: read from /sys/class/dmi/id/product_uuid
                try:
                    with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                        return f.read().strip()
                except FileNotFoundError:
                    pass
            
            elif self.system == "darwin":  # macOS
                # macOS: use system_profiler
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
                if result.returncode == 0:
                    uuid_match = re.search(r'Hardware UUID:\s+(.+)', result.stdout)
                    if uuid_match:
                        return uuid_match.group(1).strip()
        
        except Exception as e:
            print(f"Warning: Could not get system UUID: {e}")
        
        return None
    
    def generate_fingerprint(self) -> str:
        """Generate a comprehensive hardware fingerprint"""
        fingerprint_parts = []
        
        # Get MAC addresses (primary identifier)
        mac_addresses = self.get_mac_addresses()
        if mac_addresses:
            # Use the first non-loopback MAC address
            primary_mac = mac_addresses[0] if mac_addresses else "00:00:00:00:00:00"
            fingerprint_parts.append(f"MAC:{primary_mac}")
        
        # Get CPU info
        cpu_info = self.get_cpu_info()
        if cpu_info.get('processor_id'):
            fingerprint_parts.append(f"CPU:{cpu_info['processor_id']}")
        elif cpu_info.get('processor_name'):
            # Hash the processor name for consistency
            cpu_hash = hashlib.md5(cpu_info['processor_name'].encode()).hexdigest()[:16]
            fingerprint_parts.append(f"CPU:{cpu_hash}")
        
        # Get disk info
        disks = self.get_disk_info()
        if disks and disks[0].get('serial'):
            fingerprint_parts.append(f"DISK:{disks[0]['serial']}")
        
        # Get system UUID
        system_uuid = self.get_system_uuid()
        if system_uuid:
            fingerprint_parts.append(f"UUID:{system_uuid}")
        
        # If we couldn't get any hardware info, generate a fallback
        if not fingerprint_parts:
            # Use a combination of system info
            fallback = f"FALLBACK:{platform.node()}-{platform.machine()}-{platform.processor()}"
            fingerprint_parts.append(fallback)
        
        # Join all parts with pipe separator
        fingerprint = "|".join(fingerprint_parts)
        
        return fingerprint

# Global instance
hardware_fingerprint = HardwareFingerprint() 
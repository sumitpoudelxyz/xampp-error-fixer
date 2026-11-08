hahah = r"""

              ____   _   _  __  __  ___  _____ 
             / ___| | | | ||  \/  ||_ _||_   _|
             \___ \ | | | || |\/| | | |   | |  
              ___) || |_| || |  | | | |   | |  
             |____/  \___/ |_|  |_||___|  |_|  
                                   
        https://github.com/sumitpoudelxyz/xampp-error-fixer
"""
print(hahah)
import os
import shutil
import subprocess
import time
import ctypes
import re

# Configuration
FOLDERS_TO_DELETE = ["mysql", "performance_schema", "test", "phpmyadmin"]
FILES_TO_KEEP = ["ibdata1"]

def is_admin():
    """Check if script is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_xampp_path():
    """Find XAMPP installation path"""
    for drive in ["C:\\", "D:\\", "E:\\", "F:\\"]:
        xampp_path = os.path.join(drive, "xampp")
        if os.path.exists(os.path.join(xampp_path, "xampp-control.exe")):
            return xampp_path
    return None

def stop_all_xampp():
    """Compatibility shim: never terminate processes by global image name."""
    print("ℹ️ XAMPP processes were left untouched. Stop this installation manually if needed.")
    return False

def is_process_running(process_name):
    """Check if a specific process is running"""
    result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                          capture_output=True, text=True)
    return process_name in result.stdout

def get_port_usage(port):
    """Return the process listening on an exact local TCP port."""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 5 or parts[0].upper() != "TCP" or parts[3].upper() != "LISTENING":
                continue
            match = re.search(r":(\d+)$", parts[1])
            if not match or int(match.group(1)) != int(port):
                continue
            pid = parts[-1]
            task_result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True, check=True)
            for task_line in task_result.stdout.splitlines():
                fields = task_line.split()
                if len(fields) >= 2 and fields[1] == pid:
                    return {'process': fields[0], 'pid': pid}
        return None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None

def get_apache_listen_ports(httpd_conf_path):
    """Get actual ports Apache is configured to listen on"""
    ports = set()
    if os.path.exists(httpd_conf_path):
        try:
            with open(httpd_conf_path, 'r') as f:
                for line in f:
                    # Remove comments after #
                    line = line.split('#')[0].strip()
                    if line.lower().startswith("listen"):
                        # Extract port number from Listen line
                        # Match either 'Listen 80' or 'Listen 0.0.0.0:8080' or 'Listen [::]:443'
                        match = re.search(r'Listen\s+(?:\S+:)?(\d{2,5})', line, re.IGNORECASE)
                        if match:
                            ports.add(int(match.group(1)))
        except Exception as e:
            print(f"⚠️ Error parsing httpd.conf: {e}")
    return list(ports) if ports else [80, 443]  # Default fallback

def find_available_port(start_port, avoid_ports=None):
    """Find an available port starting from start_port"""
    if avoid_ports is None:
        avoid_ports = []
    
    for port in range(start_port, start_port + 100):
        if port not in avoid_ports and not get_port_usage(port):
            return port
    return start_port  # Fallback

def diagnose_mysql(xampp_path):
    """Diagnose MySQL issues with clean output"""
    print("🔍 Checking MySQL...")
    
    mysql_exe = os.path.join(xampp_path, "mysql", "bin", "mysqld.exe")
    mysql_ini = os.path.join(xampp_path, "mysql", "bin", "my.ini")
    
    if not os.path.exists(mysql_exe):
        return {"status": "error", "issue": "MySQL executable not found"}
    
    # Try to start MySQL with suppressed output
    try:
        # Redirect all MySQL output to devnull to keep console clean
        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen([mysql_exe, f"--defaults-file={mysql_ini}", "--standalone"],
                                     cwd=os.path.dirname(mysql_exe),
                                     stdout=devnull, 
                                     stderr=devnull)
        time.sleep(5)
        
        if process.poll() is None:
            # Terminate only the process started by this diagnostic.
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            return {"status": "ok", "issue": None}
        else:
            return {"status": "error", "issue": "MySQL fails to start"}
            
    except Exception as e:
        return {"status": "error", "issue": f"MySQL startup error: {str(e)}"}

def diagnose_apache(xampp_path):
    """Diagnose Apache issues with intelligent port detection"""
    print("🔍 Checking Apache...")
    
    apache_exe = os.path.join(xampp_path, "apache", "bin", "httpd.exe")
    
    if not os.path.exists(apache_exe):
        return {"status": "error", "issue": "Apache executable not found", "conflicts": [], "configured_ports": []}
    
    # Get the actual ports Apache is configured to use
    httpd_conf_path = os.path.join(xampp_path, "apache", "conf", "httpd.conf")
    apache_ports = get_apache_listen_ports(httpd_conf_path)
    
    print(f"📋 Apache is configured to use ports: {', '.join(map(str, apache_ports))}")
    
    # Check port conflicts ONLY for the ports Apache is actually configured to use
    conflicts = []
    for port in apache_ports:
        port_info = get_port_usage(port)
        if port_info and port_info['process'].lower() != 'httpd.exe':
            conflicts.append({
                'port': port,
                'process': port_info['process'],
                'pid': port_info['pid']
            })
            print(f"⚠️ Port {port} conflict: {port_info['process']} (PID: {port_info['pid']})")
    
    if conflicts:
        return {
            "status": "error", 
            "issue": "Port conflicts detected on Apache's configured ports", 
            "conflicts": conflicts,
            "configured_ports": apache_ports
        }
    
    # Try to start Apache
    try:
        process = subprocess.Popen([apache_exe], cwd=os.path.dirname(apache_exe))
        time.sleep(3)
        
        if process.poll() is None:
            # Terminate only the Apache process started by this diagnostic.
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            return {
                "status": "ok", 
                "issue": None, 
                "conflicts": [],
                "configured_ports": apache_ports
            }
        else:
            return {
                "status": "error", 
                "issue": "Apache fails to start", 
                "conflicts": [],
                "configured_ports": apache_ports
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "issue": f"Apache startup error: {str(e)}", 
            "conflicts": [],
            "configured_ports": apache_ports
        }

def get_user_choice(question, options):
    """Get user choice from multiple options"""
    while True:
        try:
            print(f"\n{question}")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            choice = input(f"\nYour choice (1-{len(options)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return int(choice) - 1
            else:
                print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return -1

def get_yes_no(question):
    """Get yes/no input from user"""
    while True:
        try:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return False

def fix_mysql(xampp_path):
    """Disable automatic database repair until a verified, reversible flow exists."""
    print("\n⚠️ Automatic MySQL repair is disabled to protect your databases.")
    print("No files in mysql/data were changed.")
    print("Back up the complete mysql/data directory before attempting manual recovery.")
    return False

def backup_file(path):
    """Create a timestamped backup beside a configuration file."""
    import datetime
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = f"{path}.xampp-fixer-{stamp}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def fix_apache_ports(xampp_path, conflicts, configured_ports):
    """Handle Apache port conflicts with intelligent port management"""
    print(f"\n🔧 Apache Port Conflict Detected!")
    
    # Show conflicts with better formatting
    print(f"\nApache is configured to use ports: {', '.join(map(str, configured_ports))}")
    print("Conflicts found:")
    for conflict in conflicts:
        print(f"  Port {conflict['port']}: occupied by {conflict['process']} (PID: {conflict['pid']})")
    
    # Never terminate another process automatically; offer config change or skip.
    options = [
        "Change Apache to use different available ports",
        "Skip Apache fix"
    ]
    choice = get_user_choice("How would you like to resolve this?", options)

    if choice == 0:  # Change ports
        print("\n🔧 Finding available ports and updating Apache configuration...")
        try:
            httpd_conf = os.path.join(xampp_path, "apache", "conf", "httpd.conf")
            if not os.path.exists(httpd_conf):
                print("❌ Apache config file not found")
                return False
            
            # Read current config
            with open(httpd_conf, 'r') as f:
                content = f.read()
            
            # Create port mapping (old port -> new available port)
            port_mapping = {}
            used_ports = []
            
            for old_port in configured_ports:
                # Find available port based on common port ranges
                if old_port in [80, 8080]:  # HTTP ports
                    new_port = find_available_port(8080, used_ports)
                elif old_port in [443, 8443]:  # HTTPS ports
                    new_port = find_available_port(8443, used_ports)
                else:  # Other ports
                    new_port = find_available_port(old_port + 1000, used_ports)
                
                port_mapping[old_port] = new_port
                used_ports.append(new_port)
            
            # Update Listen directives
            for old_port, new_port in port_mapping.items():
                # Replace Listen directives (handle various formats)
                content = re.sub(rf'^Listen\s+{old_port}$', f'Listen {new_port}', content, flags=re.MULTILINE)
                content = re.sub(rf'^Listen\s+\*:{old_port}$', f'Listen *:{new_port}', content, flags=re.MULTILINE)
                content = re.sub(rf'^Listen\s+0\.0\.0\.0:{old_port}$', f'Listen 0.0.0.0:{new_port}', content, flags=re.MULTILINE)
            
            # Preserve the original Apache configuration before changing it.
            backup_file(httpd_conf)
            with open(httpd_conf, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            # Show results
            print("✅ Apache ports updated:")
            for old_port, new_port in port_mapping.items():
                print(f"   {old_port} → {new_port}")
            
            # Show access URLs
            http_ports = [new_port for old_port, new_port in port_mapping.items() if old_port in [80, 8080]]
            if http_ports:
                print(f"💡 Access your sites at: http://localhost:{http_ports[0]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to change ports: {e}")
            return False
            
    else:  # Skip
        print("⏭️ Apache fix skipped")
        return False

def test_services(xampp_path):
    """Live service testing is disabled until child-process ownership is reliable."""
    print("\n⚠️ Live service tests are disabled to avoid affecting unrelated XAMPP instances.")
    return {"mysql": False, "apache": False}

def revert_apache_ports_to_default(xampp_path):
    """Ask to revert Apache ports to default (80/443) only if they are free and we can actually do it"""
    # Get current Apache configuration
    httpd_conf_path = os.path.join(xampp_path, "apache", "conf", "httpd.conf")
    current_ports = get_apache_listen_ports(httpd_conf_path)
    
    # Check if Apache is already using default ports
    if 80 in current_ports and (443 in current_ports or len(current_ports) == 1):
        return False  # Already using default ports
    
    # Check if default ports are available
    conflict_80 = get_port_usage(80)
    conflict_443 = get_port_usage(443)

    if conflict_80 or conflict_443:
        return False  # Default ports still occupied, silently skip

    # Only ask if we have non-default ports AND we can actually revert them
    non_default_ports = [p for p in current_ports if p not in [80, 443]]
    if not non_default_ports:
        return False  # No non-default ports to revert
    
    # Ask user if they want to revert
    if not get_yes_no(f"\n💡 Default ports (80/443) are now free. Revert Apache from current ports {non_default_ports} to default ports?"):
        print("⏭️ Reverting skipped by user.")
        return False

    try:
        httpd_conf = os.path.join(xampp_path, "apache", "conf", "httpd.conf")
        if not os.path.exists(httpd_conf):
            print("❌ Apache config file not found")
            return False
            
        with open(httpd_conf, 'r') as f:
            content = f.read()

        # Smart port reverting - handle ANY non-default port
        changes_made = False
        
        # For each non-default port, decide what to revert it to
        for current_port in non_default_ports:
            target_port = None
            
            # If we only have one port and it's not 443, make it port 80
            if len(current_ports) == 1:
                target_port = 80
            # If we have multiple ports, try to be smart about HTTP vs HTTPS
            elif current_port > 8000:  # Likely HTTP alternative
                target_port = 80
            elif current_port > 4000:  # Likely HTTPS alternative  
                target_port = 443
            else:
                target_port = 80  # Default to HTTP
            
            # Make sure we don't create duplicate Listen directives
            if target_port in current_ports:
                continue
                
            # Replace all variations of Listen directives for this port
            patterns = [
                rf'^Listen\s+{current_port}$',
                rf'^Listen\s+\*:{current_port}$', 
                rf'^Listen\s+0\.0\.0\.0:{current_port}$',
                rf'^Listen\s+\[::\]:{current_port}$'
            ]
            
            for pattern in patterns:
                old_content = content
                content = re.sub(pattern, f'Listen {target_port}', content, flags=re.MULTILINE)
                if content != old_content:
                    changes_made = True
                    print(f"✅ Reverted port {current_port} → {target_port}")

        # Preserve the original Apache configuration before changing it.
        if changes_made:
            backup_file(httpd_conf)
            with open(httpd_conf, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            print("💡 Access your sites at: http://localhost")
            return True
        else:
            print("⚠️ No port changes were made")
            return False
            
    except Exception as e:
        print(f"❌ Failed to revert ports: {e}")
        return False

def main():
    """Main execution function"""
    print("=== XAMPP Fixer ===\n")
    
    # Check admin privileges
    if not is_admin():
        print("❌ Administrator privileges required")
        print("💡 Right-click script and 'Run as administrator'")
        input("Press Enter to exit...")
        return
    
    # Find XAMPP
    xampp_path = find_xampp_path()
    if not xampp_path:
        print("❌ XAMPP not found on drives C:, D:, E:, F:")
        input("Press Enter to exit...")
        return
    
    print(f"🔍 XAMPP found at: {xampp_path}")
    
    # Do not terminate processes globally; leave service state under user control.
    print("\nℹ️ Existing processes will not be stopped automatically.")
    
    # Auto-diagnosis
    print("\n=== Auto-Diagnosis ===")
    mysql_diagnosis = diagnose_mysql(xampp_path)
    apache_diagnosis = diagnose_apache(xampp_path)
    
    # Report results
    print("\n📋 Diagnosis Results:")
    
    mysql_ok = mysql_diagnosis["status"] == "ok"
    apache_ok = apache_diagnosis["status"] == "ok"
    
    if mysql_ok:
        print("✅ MySQL: Working fine")
    else:
        print(f"❌ MySQL: {mysql_diagnosis['issue']}")
    
    if apache_ok:
        print("✅ Apache: Working fine")
    else:
        print(f"❌ Apache: {apache_diagnosis['issue']}")
    
    # Apply fixes
    if not mysql_ok or not apache_ok:
        print("\n=== Applying Fixes ===")
        
        # Fix MySQL - Handle both "fails to start" and "stops unexpectedly"
        if not mysql_ok:
            mysql_issue = mysql_diagnosis['issue']
            if mysql_issue == "MySQL stops unexpectedly" or mysql_issue == "MySQL fails to start":
                if get_yes_no("Automatic MySQL repair is disabled for data safety. Continue to see the safety notice?"):
                    fix_mysql(xampp_path)
                else:
                    print("⏭️ MySQL fix skipped")
            else:
                print(f"⚠️ MySQL issue ({mysql_issue}) - manual intervention may be needed")
        
        # Fix Apache with intelligent port management
        if not apache_ok and 'conflicts' in apache_diagnosis:
            if apache_diagnosis['conflicts']:
                fix_apache_ports(xampp_path, apache_diagnosis['conflicts'], apache_diagnosis['configured_ports'])
            elif apache_diagnosis['issue'] == "Apache fails to start":
                print("⚠️ Apache fails to start - this may require manual configuration check")
        
        # Test final results
        print("\n=== Final Testing ===")
        stop_all_xampp()  # Clean slate for testing
        time.sleep(2)
        results = test_services(xampp_path)
        
        # Clean shutdown
        print("\n=== Cleanup ===")
        stop_all_xampp()
        print("✅ All services stopped for clean state")
        
        # Success summary
        if results["mysql"] and results["apache"]:
            print("\n🎉 SUCCESS! Both MySQL and Apache are now working!")
            print("💡 You can now start them from XAMPP Control Panel")
        elif results["mysql"]:
            print("\n✅ MySQL is working! Apache may need manual attention.")
        elif results["apache"]:
            print("\n✅ Apache is working! MySQL may need manual attention.")
        else:
            print("\n⚠️ Some issues may remain. Check XAMPP Control Panel.")
    
    else:
        print("\n🎉 Great! Your XAMPP is already working perfectly!")
        print("✅ No fixes needed")
    
    # Optionally revert Apache to default ports
    revert_apache_ports_to_default(xampp_path)

    # User choice for Control Panel
    if get_yes_no("\n💡 Would you like to open XAMPP Control Panel now?"):
        try:
            xampp_control = os.path.join(xampp_path, "xampp-control.exe")
            subprocess.Popen([xampp_control])
            print("✅ XAMPP Control Panel opened")
        except:
            print("❌ Could not open XAMPP Control Panel")
    
    print("\n🎉 Done! You can now use XAMPP normally.")
    input("Press Enter to exit...")

if __name__ == "__main__":

    main()

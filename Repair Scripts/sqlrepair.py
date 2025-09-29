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
    """Stop all XAMPP processes completely"""
    print("🛑 Stopping all XAMPP processes...")
    processes = ["httpd.exe", "mysqld.exe", "xampp-control.exe"]
    
    for process in processes:
        try:
            subprocess.run(['taskkill', '/F', '/IM', process], 
                         capture_output=True, check=False)
        except:
            pass
    
    time.sleep(3)
    print("✅ All XAMPP processes stopped")

def is_mysql_running():
    """Check if MySQL process is running"""
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mysqld.exe'],
                          capture_output=True, text=True)
    return "mysqld.exe" in result.stdout

def start_mysql_only(xampp_path):
    """Start only MySQL service"""
    print("🚀 Starting MySQL...")
    
    mysql_exe = os.path.join(xampp_path, "mysql", "bin", "mysqld.exe")
    mysql_ini = os.path.join(xampp_path, "mysql", "bin", "my.ini")
    
    if not os.path.exists(mysql_exe):
        print("❌ MySQL executable not found")
        return False
    
    try:
        subprocess.Popen([mysql_exe, f"--defaults-file={mysql_ini}", "--standalone"],
                        cwd=os.path.dirname(mysql_exe))
        time.sleep(5)
        
        if is_mysql_running():
            print("✅ MySQL started successfully")
            return True
        else:
            print("❌ MySQL failed to start")
            return False
    except Exception as e:
        print(f"❌ Error starting MySQL: {e}")
        return False

def test_mysql_stability():
    """Test if MySQL stays running for 15 seconds"""
    print("🔍 Testing MySQL stability...")
    
    for i in range(1, 4):
        time.sleep(5)
        if not is_mysql_running():
            print(f"❌ MySQL crashed after {i*5} seconds!")
            return False
        print(f"⏳ MySQL stable... ({i*5}s)")
    
    print("✅ MySQL remained stable for 15 seconds")
    return True

def get_user_input(question):
    """Get user input with basic error handling"""
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

def backup_data_folder(data_path):
    """Create backup of MySQL data folder"""
    print("📦 Creating backup...")
    
    parent_dir = os.path.dirname(data_path)
    backup_path = os.path.join(parent_dir, "Old-data")
    
    try:
        if os.path.exists(backup_path):
            if get_user_input("Old backup exists. Replace it?"):
                shutil.rmtree(backup_path)
            else:
                # Create timestamped backup
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(parent_dir, f"backup_{timestamp}")
        
        shutil.copytree(data_path, backup_path)
        print(f"✅ Backup created: {os.path.basename(backup_path)}")
        time.sleep(2)
        return backup_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def clean_data_folder(data_path):
    """Clean problematic files from data folder"""
    print("🧹 Cleaning data folder...")
    
    try:
        for item in os.listdir(data_path):
            full_path = os.path.join(data_path, item)
            
            if os.path.isdir(full_path) and item in FOLDERS_TO_DELETE:
                shutil.rmtree(full_path, ignore_errors=True)
                print(f"🗑️ Removed folder: {item}")
            elif os.path.isfile(full_path) and item not in FILES_TO_KEEP:
                try:
                    os.remove(full_path)
                    print(f"🗑️ Removed file: {item}")
                except:
                    print(f"⚠️ Could not remove: {item}")
        
        print("✅ Data folder cleaned")
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Cleaning failed: {e}")

def restore_from_backup(backup_path, data_path):
    """Restore data from backup (excluding ibdata1)"""
    print("📂 Restoring from backup...")
    
    try:
        for item in os.listdir(backup_path):
            if item in FILES_TO_KEEP:
                continue  # Skip ibdata1
                
            src = os.path.join(backup_path, item)
            dst = os.path.join(data_path, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"✅ Restored folder: {item}")
            else:
                shutil.copy2(src, dst)
                print(f"✅ Restored file: {item}")
        
        print("✅ Restore completed")
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")

def main():
    """Main execution function"""
    print("=== XAMPP MySQL Fixer ===\n")
    
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
    
    # Setup paths
    data_path = os.path.join(xampp_path, "mysql", "data")
    backup_path = os.path.join(xampp_path, "mysql", "backup")
    
    # Step 1: Clean start
    stop_all_xampp()
    
    # Step 2: Test MySQL
    print("\n=== Testing MySQL ===")
    if not start_mysql_only(xampp_path):
        print("❌ MySQL won't start - proceeding with fix...")
        mysql_broken = True
    else:
        mysql_broken = not test_mysql_stability()
    
    # Step 3: Check if fix is needed
    if not mysql_broken:
        print("\n🎉 Great! MySQL is working perfectly!")
        print("✅ No fix needed - your XAMPP is healthy")
    else:
        print("\n⚠️ MySQL has the 'stopped unexpectedly' error")
        
        if not get_user_input("Proceed with the fix? This will restore your databases"):
            print("❌ Fix cancelled")
        else:
            # Step 4: Execute fix
            print("\n=== Executing Fix ===")
            stop_all_xampp()
            
            backup_folder = backup_data_folder(data_path)
            if backup_folder:
                clean_data_folder(data_path)
                restore_from_backup(backup_path, data_path)
                
                # Step 5: Test fix
                print("\n=== Testing Fix ===")
                if start_mysql_only(xampp_path) and test_mysql_stability():
                    print("\n🎯 SUCCESS! MySQL fix completed!")
                    print("✅ MySQL is now working without errors")
                else:
                    print("\n⚠️ Fix completed but MySQL may still have issues")
            else:
                print("❌ Fix aborted - backup failed")
    
    # Step 6: Clean shutdown
    print("\n=== Cleanup ===")
    stop_all_xampp()
    print("✅ All XAMPP services stopped for clean state")
    
    # Step 7: User choice
    if get_user_input("\n💡 Would you like to open XAMPP Control Panel now?"):
        try:
            xampp_control = os.path.join(xampp_path, "xampp-control.exe")
            subprocess.Popen([xampp_control])
            print("✅ XAMPP Control Panel opened")
        except:
            print("❌ Could not open XAMPP Control Panel")
    
    print("\n🎉 Done! You can now use your databases normally.")
    input("Press Enter to exit...")

if __name__ == "__main__":

    main()

import requests
import subprocess
import os
import time
import shutil
import ast

def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        release_info = response.json()
        return release_info['tag_name']
    else:
        return None

def update_package(owner, repo):
    latest_version = get_latest_release(owner, repo)
    if latest_version:
        installed_version = get_installed_version()
        if installed_version != latest_version:
            # Backup Data/ folder
            backup_data_folder()
            
            # Construct URL for downloading the released version
            package_url = f"https://github.com/{owner}/{repo}/archive/{latest_version}.tar.gz"
            # Download the package
            print(f"Downloading {repo} version {latest_version} from GitHub...")
            subprocess.run(["pip", "install", "--upgrade", package_url])
            print("Package updated successfully!")
            # Reboot the Raspberry Pi
            print("Rebooting the system...")
            os.system("sudo reboot")
        else:
            print("Package is already up to date.")
    else:
        print("Failed to fetch the latest release information.")
        # Print error message and exit
        print("Unable to update package as latest version information is not available.")

def get_installed_version():
    # Assuming setup.py is in the same directory as update.py
    setup_file_path = os.path.join(os.path.dirname(__file__), "setup.py")
    if os.path.exists(setup_file_path):
        with open(setup_file_path, "r") as setup_file:
            setup_code = setup_file.read()
            setup_ast = ast.parse(setup_code)
            for node in setup_ast.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if hasattr(target, "id") and target.id == "version":
                            return node.value.s
    return None

def backup_data_folder():
    data_folder = os.path.join(os.path.dirname(__file__), "Data")
    if os.path.exists(data_folder):
        # Create a backup folder
        backup_folder = os.path.join(os.path.dirname(__file__), "Data_Backup")
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        # Copy data to backup folder
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                shutil.copy2(os.path.join(root, file), backup_folder)

if __name__ == "__main__":
    # Replace these with your GitHub repository details
    owner = "aiembed"
    repo = "DriveNav"
    
    # Check for updates every 24 hours
    while True:
        update_package(owner, repo)
        # Wait for 24 hours before checking for updates again
        time.sleep(24 * 60 * 60)  # 24 hours in seconds

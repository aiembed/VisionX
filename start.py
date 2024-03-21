import os
import subprocess
import shutil
import time

def install_requirements():
    # Import GPG key manually (if necessary)
    subprocess.run(["sudo", "apt-key", "adv", "--keyserver", "keyserver.ubuntu.com", "--recv-keys", "B53DC80D13EDEF05"])

    # Run apt-get update and install required packages with sudo
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip", "python3-picamera"])

def create_systemd_service(script_path):
    # Create systemd service file with elevated privileges for apt-get commands
    service_content = f"""\
[Unit]
Description=My Python Script

[Service]
Type=simple
ExecStartPre=sudo /bin/bash -c 'apt-get update && apt-get install -y python3-pip python3-picamera'
ExecStart=/usr/bin/python3 {script_path}
Restart=always
RestartSec=10
User=pi

[Install]
WantedBy=multi-user.target
"""
    service_file_path = "/etc/systemd/system/start.service"
    with open(service_file_path, "w") as service_file:
        service_file.write(service_content)
    return service_file_path

def copy_main_script():
    # Copy main.py to destination directory if it doesn't exist
    main_script_path = os.path.join(os.path.dirname(__file__), "main.py")
    destination_path = "/home/pi/start.py"
    
    if not os.path.exists(destination_path):
        shutil.copy(main_script_path, destination_path)
        subprocess.run(["sudo", "chmod", "+x", destination_path])
        subprocess.run(["sudo", "chown", "pi:pi", destination_path])
        print("main.py copied to destination directory.")
    else:
        print("main.py already exists in the destination directory.")

def execute_main_script():
    # Reload systemd daemon to load the newly created service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    # Enable and start the systemd service
    subprocess.run(["sudo", "systemctl", "enable", "start.service"])
    subprocess.run(["sudo", "systemctl", "start", "start.service"])
    print("Setup completed.")

def main():
    # Install requirements
    install_requirements()

    # Create systemd service file
    script_path = "/home/pi/start.py"  # Update with the path to your Python script
    service_file_path = create_systemd_service(script_path)

    # Copy main.py to destination directory if needed
    copy_main_script()

    # Execute main.py after reboot
    execute_main_script()

    # Loop to keep the script running
    while True:
        time.sleep(1)  # Sleep to avoid high CPU usage

if __name__ == "__main__":
    main()

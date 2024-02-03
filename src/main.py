import click
import requests
import os
import json
import hashlib
from tqdm import tqdm

# Function to clear the screen
def clear_screen():
    """Function to reset the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def toggle_show_full_source_info():
    """Function to toggle the 'show_full_source_info' option in the config."""
    config = load_config()

    # Toggle the option
    config["show_full_source_info"] = not config.get("show_full_source_info", False)

    # Save the updated config
    save_config(config)

    print(f"Show Full Source Information set to: {config['show_full_source_info']}")

def toggle_show_beta_installers():
    """Function to toggle the 'show_beta_installers' option in the config."""
    config = load_config()

    # Toggle the option
    config["show_beta_installers"] = not config.get("show_beta_installers", False)

    # Save the updated config
    save_config(config)

    print(f"Show Beta Installers set to: {config['show_beta_installers']}")

def load_config():
    """Function to load the config from data/config.json."""
    config_path = os.path.join("data", "config.json")
    config = {}

    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)

        print("Config loaded successfully.")
    else:
        print("Config file not found. Creating a new one.")
        save_config(config)

    return config

def save_config(config):
    """Function to save the config to data/config.json."""
    config_path = os.path.join("data", "config.json")

    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

    print("Config saved successfully.")

# Function to download a file from a given URL
def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
        print(f"\nDownload completed. File saved to: {destination}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

# Function to extract the filename from a given URL
def extract_filename_from_url(url):
    """Extracts the filename from a given URL."""
    return os.path.basename(url)

# Function to sort packages by size
def sort_packages_by_size(packages):
    """Sorts the packages by size in descending order."""
    return sorted(packages, key=lambda x: x.get("size", 0), reverse=True)

def pycheck():
    """Function to check if python3 is available, otherwise fallback to python."""
    try:
        # Try running python3 to see if it's available
        os.system("python3 -V")
        return "python3"
    except Exception:
        # If python3 is not available, use python
        return "python"

@click.command()
def main():
    """Main entry point for DarwinFetch."""
    print("Loading configuration!")
    config = load_config()

    # Create the 'downloads' directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)

    while True:
        clear_screen()
        print("Welcome to DarwinFetch!")
        print("Copyright (c) 2023 RoyalGraphX")
        print("Python x86_64 Pre-Release 0.0.10\n")
        print("Menu:")
        print("1. Download Offline Installer")
        print("2. Download RecoveryOS Installer")
        print("3. Update Sources")
        print("4. Settings")
        print("5. Exit")

        choice = click.prompt("Enter your choice", type=int)

        if choice == 1:
            download_offline_installer()
        elif choice == 2:
            download_recovery_installer()
        elif choice == 3:
            update_sources()
        elif choice == 4:
            settings_menu()
        elif choice == 5:
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.")
        
        # Pause to show the result before clearing the screen again
        click.pause()

# Function to download a full offline installer
def download_offline_installer():
    """Function to handle downloading the full Offline Installer."""
    clear_screen()

    # Check if offline sources are up to date
    if not check_sources("offline"):
        print("Sources are either out of date or don't exist. Consider updating your sources.")
        return  # Exit the function if offline sources are not up to date

    # Fetch the config dynamically
    config = load_config()

    # Call parse_offline_sources to display available sources and take into account the user config
    parse_offline_sources(config)

    # Get user input to choose a source
    choice = click.prompt("Enter the number of the source to download (or 'c' to cancel)", type=str)

    # Check if the user wants to cancel
    if choice.lower() == 'c':
        print("Download canceled.")
        return

    try:
        # Convert the user input to an integer
        choice = int(choice)

        # Read offline sources from the JSON file
        sources_file_path = os.path.join("data", "offline_sources.json")

        if os.path.exists(sources_file_path):
            with open(sources_file_path, 'r') as file:
                sources_data = json.load(file)

            # Validate the user's choice
            if 1 <= choice <= len(sources_data):
                selected_source = sources_data[choice - 1]

                # Placeholder code: Print information about the selected source
                name = selected_source.get("name", "Unknown Name")
                version = selected_source.get("version", "Unknown Version")
                build = selected_source.get("build", "Unknown Build")
                identifier = selected_source.get("identifier", "Unknown Identifier")
                date = selected_source.get("date", "Unknown Date")
                beta = selected_source.get("beta", "Unknown Status")

                print(f"\nSelected Source: {name} {version} ({build}) - {identifier} ({date})")

                # Create a new folder in 'downloads' based on version and build
                folder_name = f"{version}_{build}"
                folder_path = os.path.join("downloads", folder_name)
                os.makedirs(folder_path, exist_ok=True)

                # Get the packages from the selected source
                packages = selected_source.get("packages", [])

                if packages:
                    # Sort packages by size in descending order
                    sorted_packages = sort_packages_by_size(packages)

                    # Download each package into the created folder
                    for package in sorted_packages:
                        package_url = package.get("url", "Unknown URL")
                        package_filename = extract_filename_from_url(package_url)
                        package_destination = os.path.join(folder_path, package_filename)

                        print(f"Downloading: {package_filename}")
                        print(f"URL: {package_url}")

                        # Download the package file
                        download_file(package_url, package_destination)

                        print(f"Downloaded to: {package_destination}")
                else:
                    print("No packages available for this source.")
            else:
                print("Invalid choice. Please enter a valid source number.")
        else:
            print("No sources available.")

    except ValueError:
        print("Invalid input. Please enter a valid source number or 'c' to cancel.")

def download_recovery_installer():
    """Function to handle downloading the RecoveryOS Installer."""
    clear_screen()

    # Check if recovery sources are up to date
    if not check_sources("recovery"):
        print("Sources are either out of date or don't exist. Consider updating your sources.")
        return  # Exit the function if recovery sources are not up to date

    # Fetch the config dynamically
    config = load_config()

    # Call parse_recovery_sources to display available sources and take into account the user config
    parse_recovery_sources(config)

    # Get user input to choose a source
    choice = click.prompt("Enter the number of the source to download (or 'c' to cancel)", type=str)

    # Check if the user wants to cancel
    if choice.lower() == 'c':
        print("Download canceled.")
        return

    try:
        # Convert the user input to an integer
        choice = int(choice)

        # Read recovery sources from the JSON file
        sources_file_path = os.path.join("data", "recovery_sources.json")

        if os.path.exists(sources_file_path):
            with open(sources_file_path, 'r') as file:
                sources_data = json.load(file)

            # Validate the user's choice
            if 1 <= choice <= len(sources_data):
                selected_source = sources_data[choice - 1]

                # Placeholder code: Print information about the selected source
                name = selected_source.get("name", "Unknown Name")
                version = selected_source.get("version", "Unknown Version")
                build = selected_source.get("build", "Unknown Build")
                identifier = selected_source.get("identifier", "Unknown Identifier")

                print(f"\nSelected Source: {name} {version} ({build}) - {identifier}")

                # Run the macrecovery.py script with the provided command
                command = selected_source.get("command", "")
                if command:
                    print(f"Running command: {command}")

                     # Determine the Python command using pycheck
                    python_command = pycheck()

                    # Execute the command
                    os.system(f"{python_command} src/macrecovery.py {command}")

                    print("Command execution completed.")
                else:
                    print("No command available for this source.")
            else:
                print("Invalid choice. Please enter a valid source number.")
        else:
            print("No sources available.")

    except ValueError:
        print("Invalid input. Please enter a valid source number or 'c' to cancel.")

# Function to update sources
def update_sources():
    """Function to handle updating sources."""
    clear_screen()
    print("Updating offline and recovery sources...")

    # URL for the offline and recovery sources JSON files
    offline_sources_url = "https://raw.githubusercontent.com/royalgraphx/DarwinFetch/main/data/offline_sources.json"
    recovery_sources_url = "https://raw.githubusercontent.com/royalgraphx/DarwinFetch/main/data/recovery_sources.json"

    # Check if offline source needs updating
    offline_destination = os.path.join("data", "offline_sources.json")
    if not check_sources("offline"):
        download_file(offline_sources_url, offline_destination)
        print(f"Offline sources updated. File saved to {offline_destination}.")
    else:
        print("Offline sources are already up to date.")

    # Check if recovery source needs updating
    recovery_destination = os.path.join("data", "recovery_sources.json")
    if not check_sources("recovery"):
        download_file(recovery_sources_url, recovery_destination)
        print(f"Recovery sources updated. File saved to {recovery_destination}.")
    else:
        print("Recovery sources are already up to date.")

# Function to check if the local source file matches the remote source file
def check_sources(source_type):
    """Function to check if the local source file matches the remote source file."""
    # URL for the source JSON file
    source_url = None
    local_destination = None
    if source_type == "offline":
        source_url = "https://raw.githubusercontent.com/royalgraphx/DarwinFetch/main/data/offline_sources.json"
        local_destination = os.path.join("data", "offline_sources.json")
    elif source_type == "recovery":
        source_url = "https://raw.githubusercontent.com/royalgraphx/DarwinFetch/main/data/recovery_sources.json"
        local_destination = os.path.join("data", "recovery_sources.json")
    else:
        print("Invalid source type.")
        return False

    try:
        # Check if the local file exists
        if not os.path.exists(local_destination):
            return False

        # Download the remote source file temporarily
        response = requests.get(source_url, stream=True)
        response.raise_for_status()

        # Calculate SHA-256 hash of the downloaded content
        remote_hash = hashlib.sha256(response.content).hexdigest()

        # Calculate SHA-256 hash of the local source file
        with open(local_destination, 'rb') as local_file:
            local_hash = hashlib.sha256(local_file.read()).hexdigest()

        # Compare hashes and return the result
        return remote_hash == local_hash

    except requests.exceptions.RequestException as e:
        print(f"Error checking source: {e}")
        return False

def settings_menu():
    """Function to handle settings."""
    while True:
        clear_screen()
        print("Settings Menu:")
        print("1. Toggle Show Full Source Information")
        print("2. Toggle Show Beta Installers")
        print("3. Back to Main Menu")

        choice = click.prompt("Enter your choice", type=int)

        if choice == 1:
            toggle_show_full_source_info()
        if choice == 2:
            toggle_show_beta_installers()
        elif choice == 3:
            break
        else:
            print("Invalid choice. Please enter a valid option.")

        # Pause to show the result before clearing the screen again
        click.pause()

# parse_offline_sources function based on config
def parse_offline_sources(config):
    """Function to parse and display sources."""
    print("Available Sources:")

    # Read sources from the JSON file
    sources_file_path = os.path.join("data", "offline_sources.json")

    if os.path.exists(sources_file_path):
        with open(sources_file_path, 'r') as file:
            sources_data = json.load(file)

        # Iterate over each entry and display the information
        for index, source in enumerate(sources_data, start=1):
            name = source.get("name", "Unknown Name")
            version = source.get("version", "Unknown Version")
            build = source.get("build", "Unknown Build")
            identifier = source.get("identifier", "Unknown Identifier")
            date = source.get("date", "Unknown Date")
            beta = source.get("beta", "Unknown Status")

            # Skip displaying entries with beta: true if show_beta_installers is False
            if not config["show_beta_installers"] and beta:
                continue

            print(f"{index}. {name} {version}")
            # print(f"    Build: {build} Released:{date} Beta: {beta}")

            if config["show_full_source_info"]:
                # Display further information for the source

                # Display packages within the source entry
                packages = source.get("packages", [])
                if packages:
                    print("    Packages:")

                    # Sort the packages by size
                    sorted_packages = sort_packages_by_size(packages)

                    for package in sorted_packages:
                        package_url = package.get("url", "Unknown URL")
                        package_size = package.get("size", "Unknown Size")

                        # Use the function to extract the filename from the URL
                        filename = extract_filename_from_url(package_url)

                        print(f"        - {filename} - {package_size} bytes")

                    print()  # Add a blank line between sources if show_full_source_info is true

            elif config["show_full_source_info"]:
                print()  # Add a blank line between sources if show_full_source_info is true

    else:
        print("No sources available.")

# parse_recovery_sources function based on config
def parse_recovery_sources(config):
    """Function to parse and display recoveryOS sources."""
    print("Available Sources:")

    # Read sources from the JSON file
    sources_file_path = os.path.join("data", "recovery_sources.json")

    if os.path.exists(sources_file_path):
        with open(sources_file_path, 'r') as file:
            sources_data = json.load(file)

        # Iterate over each entry and display the information
        for index, source in enumerate(sources_data, start=1):
            name = source.get("name", "Unknown Name")
            version = source.get("version", "Unknown Version")
            build = source.get("build", "Unknown Build")
            identifier = source.get("identifier", "Unknown Identifier")
            beta = source.get("beta", "Unknown Status")
            command = source.get("command", "Unknown Command")

            # Skip displaying entries with beta: true if show_beta_installers is False
            if not config["show_beta_installers"] and beta:
                continue

            print(f"{index}. {name} {version}")

            if config["show_full_source_info"]:
                # Display further information for the source
                print("    Source Information:")
                for key, value in source.items():
                    if key not in ["name", "version"]:
                        print(f"        - {key}: {value}")
                print()  # Add a blank line between sources if show_full_source_info is true

    else:
        print("No sources available.")

if __name__ == "__main__":
    main()
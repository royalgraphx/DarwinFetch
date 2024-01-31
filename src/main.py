import click
import requests
import os
import json
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
        print("Python x86_64 Pre-Release 0.0.4\n")
        print("Menu:")
        print("1. Download Full Installer")
        print("2. Download RecoveryOS Installer")
        print("3. Update Sources")
        print("4. Settings")
        print("5. Exit")

        choice = click.prompt("Enter your choice", type=int)

        if choice == 1:
            download_full_installer()
        elif choice == 2:
            download_recoveryos_installer()
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
def download_full_installer():
    """Function to handle downloading the Full Installer."""
    clear_screen()

    # Fetch the config dynamically
    config = load_config()

    # Call parse_sources to display available sources based on config
    parse_sources(config)

    # Get user input to choose a source
    choice = click.prompt("Enter the number of the source to download (or 'c' to cancel)", type=str)

    # Check if the user wants to cancel
    if choice.lower() == 'c':
        print("Download canceled.")
        return

    try:
        # Convert the user input to an integer
        choice = int(choice)

        # Read sources from the JSON file
        sources_file_path = os.path.join("data", "sources.json")

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

def download_recoveryos_installer():
    """Function to handle downloading the RecoveryOS Installer. This is still TO DO."""
    clear_screen()

    url = "https://example.com/recoveryos_installer.zip"
    destination = os.path.join("downloads", "recoveryos_installer.zip")
    download_file(url, destination)

    print(f"RecoveryOS Installer downloaded to {destination}.")

# Function to update sources
def update_sources():
    """Function to handle updating sources."""
    clear_screen()
    print("Updating sources...")

    # URL for the sources JSON file
    sources_url = "https://raw.githubusercontent.com/royalgraphx/DarwinFetch/main/data/sources.json"

    # Download the JSON file and save it to 'data/sources.json'
    destination = os.path.join("data", "sources.json")
    download_file(sources_url, destination)

    print(f"Sources updated. File saved to {destination}.")

    # Pause to show the result before clearing the screen again
    click.pause()

def settings_menu():
    """Function to handle settings."""
    while True:
        clear_screen()
        print("Settings Menu:")
        print("1. Toggle Show Full Source Information")
        print("2. Back to Main Menu")

        choice = click.prompt("Enter your choice", type=int)

        if choice == 1:
            toggle_show_full_source_info()
        elif choice == 2:
            break
        else:
            print("Invalid choice. Please enter a valid option.")

        # Pause to show the result before clearing the screen again
        click.pause()

# Updated parse_sources function based on config
def parse_sources(config):
    """Function to parse and display sources."""
    print("Available Sources:")

    # Read sources from the JSON file
    sources_file_path = os.path.join("data", "sources.json")

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

if __name__ == "__main__":
    main()
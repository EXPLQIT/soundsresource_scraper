import requests
import os
import subprocess
from bs4 import BeautifulSoup

destination_folder = "GAME\\SOUNDS\\GO\\HERE"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, '_')
    return name

def process_category(category_name, soup, game_folder):
    print(f"Processing category: {category_name}")
    category_sounds = get_sounds_in_category(soup, category_name)
    if category_sounds:
        for sound_name, sound_link in category_sounds.items():
            sound_name = sanitize_filename(sound_name)
            sound_id = sound_link.strip('/').split('/')[-1]
            zip_file_name = f"{sound_name}.zip"
            zip_path = os.path.join(game_folder, zip_file_name)

            print(f"Downloading sound: {sound_name}")
            download_sound(sound_id, game_folder, zip_file_name)

            extract_folder = os.path.join(game_folder, sound_name)
            extract_zip(zip_path, extract_folder)
    else:
        print(f"No sounds found in the '{category_name}' category.")

def extract_zip(zip_path, extract_to):
    # Ensure the extraction path exists
    os.makedirs(extract_to, exist_ok=True)
    seven_zip_executable = r"PATH\TO\7ZIP\EXE"  # Adjust as necessary for your system
    try:
        # Call the 7z executable to extract the file
        subprocess.check_call([seven_zip_executable, 'x', zip_path, f'-o{extract_to}', '-y'])
        print(f"Extracted successfully to: {extract_to}")
        # Delete the zip file after extraction
        os.remove(zip_path)
        print(f"Removed ZIP file: {zip_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting: {e}")

def download_sound(sound_id, destination_folder, file_name):
    file_name = sanitize_filename(file_name)
    download_url = f"https://www.sounds-resource.com/download/{sound_id}/"
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        os.makedirs(destination_folder, exist_ok=True)
        file_path = os.path.join(destination_folder, file_name)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully: {file_path}")
    else:
        print("Failed to download the file. Status code:", response.status_code)
        
def select_game(game_links):
    if not game_links:
        return None
    
    choice = input("Enter the number of the game you want to download: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(game_links):
            selected_game = list(game_links.keys())[choice - 1]
            return selected_game
        else:
            print("Invalid choice. Please enter a valid number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def select_category(categories):
    if not categories:
        return None
    
    print("Categories found:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")
    
    choice = input("Enter the number of the category you want to explore: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(categories):
            return categories[choice - 1]
        else:
            print("Invalid choice. Please enter a valid number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def get_sounds_in_category(soup, category_name):
    # Find the container for the specified category, like 'Characters'
    category_container = soup.find('div', class_='sect-name', string=lambda text: text and category_name in text)
    if category_container:
        # Find the next table that contains the links to sounds
        sound_table = category_container.find_next('table', class_='display altrow')
        if sound_table:
            sound_links = sound_table.find_all('a')
            # Extract the text and the href from each link
            sounds = {sound_link.text: sound_link['href'] for sound_link in sound_links if sound_link.text}
            return sounds
    print(f"No sound table found for category '{category_name}'.")
    return None

def search_game_sounds(game_name):
    base_url = "https://www.sounds-resource.com"
    search_url = f"{base_url}/search/?q={game_name}"
    
    # Send a GET request to the search URL
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('table', class_='display altrow')
        
        if results:
            print("Results found:")
            game_links = {}
            count = 1
            search_terms = game_name.lower().split()  # Split the search string into individual words
            for table in results:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        title_col = cols[0]
                        title_link = title_col.find('a')
                        if title_link:
                            title = title_link.text.strip()
                            # Check if the title contains all the search terms
                            if all(term in title.lower() for term in search_terms):
                                url = base_url + title_link['href']
                                if title not in game_links:
                                    game_links[title] = url
                                    print(f"{count}. {title} - {url}")
                                    count += 1
                        else:
                            print("Title link not found.")
            return game_links
        else:
            print("No results found.")
            return None
    else:
        print("Failed to fetch search results.")
        return None

def main():
    while True:
        game_name = input("Enter the name of the game or type 'exit' to end: ")
        if game_name.lower() == 'exit':
            break

        game_links = search_game_sounds(game_name)
        if not game_links:
            print("No game found with the provided name, try again.")
            continue

        while True:
            selected_game_name = select_game(game_links)
            if not selected_game_name:
                break  # This goes back to the "Enter the name of the game" prompt.

            categories_url = game_links[selected_game_name]
            response = requests.get(categories_url)
            if response.status_code != 200:
                print("Failed to fetch categories. Please try again.")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            category_tags = soup.find_all('div', class_='section')
            categories = [tag.find('div', class_='sect-name').text.strip() for tag in category_tags]

            while True:
                print(f"Categories found for {selected_game_name}:")
                for i, category in enumerate(categories, start=1):
                    print(f"{i}. {category}")
                print(f"{i+1}. Download all categories")
                print("Type 'all' to download all categories, 'back' to select another game, or 'exit' to end:")

                category_choice = input("Choose an option: ")
                if category_choice.lower() == 'exit':
                    return  # Exits the program completely.
                elif category_choice.lower() == 'back':
                    break  # Exits to the game selection.
                elif category_choice.lower() == 'all':
                    for category in categories:
                        process_category(category, soup, os.path.join(destination_folder, selected_game_name.replace(':', '').replace('/', ' or ')))
                elif category_choice.isdigit() and 1 <= int(category_choice) <= len(categories):
                    selected_category = categories[int(category_choice) - 1]
                    process_category(selected_category, soup, os.path.join(destination_folder, selected_game_name.replace(':', '').replace('/', ' or ')))
                else:
                    print("Invalid input. Please enter a number, 'all', 'back', or 'exit'.")

                another = input("Do you want to select another category or game? (yes/no): ")
                if another.lower() != 'yes':
                    break  # Exits to the game selection loop.

if __name__ == "__main__":
    main()

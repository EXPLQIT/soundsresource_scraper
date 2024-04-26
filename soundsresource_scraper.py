import requests
import os
import subprocess
from bs4 import BeautifulSoup

destination_folder = "GAME\\SOUNDS\\GO\\HERE"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    return ''.join(c if c not in invalid else '_' for c in name)

def get_sounds_in_category(soup, category_name):
    category_container = soup.find('div', class_='sect-name', string=lambda text: text and category_name in text)
    if category_container:
        sound_table = category_container.find_next('table', class_='display altrow')
        if sound_table:
            sound_links = sound_table.find_all('a')
            sounds = {sound_link.text: sound_link['href'] for sound_link in sound_links if sound_link.text}
            return sounds
    print(f"No sound table found for category '{category_name}'.")
    return None

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
    os.makedirs(extract_to, exist_ok=True)
    seven_zip_executable = r"PATH\TO\7ZIP\EXE"
    try:
        subprocess.check_call([seven_zip_executable, 'x', zip_path, f'-o{extract_to}', '-y'])
        print(f"Extracted successfully to: {extract_to}")
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

def search_game_sounds(game_name):
    base_url = "https://www.sounds-resource.com"
    search_url = f"{base_url}/search/?q={game_name}"
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('table', class_='display altrow')
        
        if results:
            print("Results found:")
            game_links = {}
            count = 1
            search_terms = game_name.lower().split()
            seen_titles = set()  # Keep track of titles to filter out duplicates
            for table in results:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        title_col = cols[0]
                        title_link = title_col.find('a')
                        if title_link:
                            title = title_link.text.strip()
                            if title not in seen_titles and all(term in title.lower() for term in search_terms):
                                url = base_url + title_link['href']
                                game_links[count] = {'title': title, 'url': url}
                                seen_titles.add(title)
                                print(f"{count}. {title} - {url}")
                                count += 1
            return game_links
        else:
            print("No results found.")
            return None
    else:
        print("Failed to fetch search results.")
        return None

def select_option(options):
    while True:
        choice = input("Enter the number of your choice: ")
        print("DEBUG:", choice)
        if choice.isdigit():
            choice = int(choice)
            print("DEBUG - Selected choice:", choice)
            if 1 <= choice <= len(options):
                return options[choice]
            else:
                print("Invalid choice. Please enter a valid number.")
        elif choice.lower() == 'exit':
            return 'exit'
        else:
            print("Invalid input. Please enter a number.")

def main():
    while True:
        game_name = input("Enter the name of the game or type 'exit' to end: ")
        if game_name.lower() == 'exit':
            break

        game_links = search_game_sounds(game_name)
        if not game_links:
            print("No game found with the provided name, try again.")
            continue

        selected_game = select_option(game_links)
        categories_url = selected_game['url']
        response = requests.get(categories_url)
        if response.status_code != 200:
            print("Failed to fetch categories. Please try again.")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        category_tags = soup.find_all('div', class_='section')
        categories = [tag.find('div', class_='sect-name').text.strip() for tag in category_tags]

        print(f"Categories found for {selected_game['title']}:")
        category_options = {i + 1: category for i, category in enumerate(categories)}
        category_options[len(categories) + 1] = 'Download all categories'
        category_options[len(categories) + 2] = 'Choose another game'
        category_options[len(categories) + 3] = 'Exit'

        for key, value in category_options.items():
            print(f"{key}. {value}")

        choice = select_option(category_options)

        if choice == 'Download all categories':
            for category in categories:
                process_category(category, soup, os.path.join(destination_folder, selected_game['title'].replace(':', '').replace('/', ' or ')))
        elif choice == 'Choose another game':
            continue
        elif choice == 'Exit':
            break
        else:
            process_category(choice, soup, os.path.join(destination_folder, selected_game['title'].replace(':', '').replace('/', ' or ')))

if __name__ == "__main__":
    main()

<!-- GETTING STARTED -->
## Sounds-Resource.com Scraper Tool (made with ChatGPT)

Sounds-Resource has a huge library of searchable game sounds.

Upon running this script it'll prompt the user for a game, the user can search any game they'd like. For example searching 'castlevania'
would pull up all games associated with castlevania in number form. (assuming they're available).

The user can then select a game by the number. It'll then prompt the user by categories. (ex. 'Dialog', 'Sound Effects', 'Misc', 'All' etc)
This part of the prompts may be a little confusing. I plan to make it less confusing soon.

So the user has the option to download 'All' the categories by typing 'all'. 
*If 'All' has a number associated with it in the categories list, ignore the number and just type 'all'.*

Once the list has finished downloading, you can type 'exit' and then 'exit' again to get back to searching a game. 

*Important Note* - 7-Zip is required for this script to function correctly. The reason for this is because it uses 7-Zip to extract the .zips that are downloaded and exports them into their respective folders.
This was added to simplify the exporting process. Feel free to remove this function on your own if you don't wish to extract the .zips when they're downloaded.

This will not download any files that have been previously downloaded, it'll skip any sounds that have already been downloaded.

You will have to update this to your 7-Zip executable (ex. seven_zip_executable = r"C:\Program Files\7-Zip\7z.exe")
```sh
   seven_zip_executable = r"PATH\TO\7ZIP\EXE"
  ```

This script require BeautifulSoup & Requests:
```sh
   pip install requests beautifulsoup4
  ```

Update this to the directory in which you wish to have the games sounds saved to: (the double backslashes are necessary)
```sh
  destination_folder = "GAME\\SOUNDS\\GO\\HERE"
  ```


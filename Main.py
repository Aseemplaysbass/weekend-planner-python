# Required modules
import random
import json
import pickle
import csv
import mysql.connector

# Global Variables
token, tokenTemp, active, Suggestions, Implied = 'Home', None, 'Guest', [], []

# Initialize connection to database
def ConnectDatabase():
    return mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        port = '3308',
        database = 'profilesystem'
    )

# Critical database checks
def InitializeDatabase():
    db = ConnectDatabase()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            username VARCHAR(20) NOT NULL PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            bookmarks TEXT,
            feedback TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("SELECT username FROM profiles")
    
    existingUsers = set()
    for row in cursor.fetchall():
        existingUsers.add(row[0].lower())
    emptyListJson = json.dumps([])

    if 'guest' not in existingUsers:
        cursor.execute(
            "INSERT INTO profiles (username, password, bookmarks, feedback) VALUES (%s, %s, %s, %s)",
            ('guest', '', emptyListJson, emptyListJson)
        )
    if 'admin' not in existingUsers:
        cursor.execute(
            "INSERT INTO profiles (username, password, bookmarks, feedback) VALUES (%s, %s, %s, %s)",
            ('admin', '1234', emptyListJson, emptyListJson)
        )
    db.commit()
    
    cursor.close()
    db.close()
    
InitializeDatabase()

# Retrieves data of all places from binary file
def GetLists(place):
    try:
        with open('Places.dat', 'rb') as file:
            data = pickle.load(file)
        return data.get(place + 'Choices', None)
    
    except Exception as e:
        return e

# Retrieves token for user from csv file
def TokenHandler(choice, key = None):
    try:
        current, tokens = None, {}
        
        with open('Token Handler.csv', mode = 'r') as file:
            data = csv.reader(file)
            
            for row in data:
                if row:
                    if len(row) == 1:
                        current = row[0].strip()
                    elif len(row) > 1 and current == choice:
                        tokens[row[0].strip()] = row[1].strip()

            if key == 0:
                return list(tokens.keys())
            elif key is None:
                l = list(tokens.values())
                l.remove('UserMenu')
                l.remove('Token')
                return l
            else:
                return tokens.get(str(key), None)
        
    except Exception as e:
        return e

# Gets all available options from text file
def GetOptions(option):
    options = []
    
    try:
        with open('Options.txt', mode = 'r') as file:
            data, found = file.readlines(), False

            for line in data:
                line = line.strip()

                if line == option:
                    found = True
                    continue
                if found and 'Options' in line:
                    break
                if found and line:
                    options.append(line)

            if options:
                return options
            else:
                return 'Error! No options available.'
    
    except Exception as e:
        return e

# Profile Creation
def CreateProfile():
    connection = ConnectDatabase() 
    cursor = connection.cursor()

    print("_" * 30)
    print("       CREATE PROFILE\n")

    while True:
        username = input("Enter a username: ").strip()

        if username.lower() == 'admin':
            print("Insufficient Permissions! Unavailable username.")
            cursor.close()
            connection.close()
            return

        cursor.execute("SELECT * FROM profiles WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            break
        else:
            print("Username already exists!")

    password = input("Enter a password: ").strip()

    while True:
        choice = input("Confirm creation of profile " + username + ", enter Y/N (Yes/No): ").lower().strip()

        if choice in ['yes', 'y']:
            try:
                cursor.execute(
                    "INSERT INTO profiles (username, password, bookmarks, feedback) VALUES (%s, %s, %s, %s)",
                    (username, password, '[]', '[]')
                )
                connection.commit()
                print("\nProfile created successfully!\n")
                
            except mysql.connector.Error as e:
                return e
            break

        elif choice in ['no', 'n']:
            print("\nProfile creation cancelled!\n")
            break

        else:
            print("Invalid, please try again!")
                
    cursor.close()
    connection.close()

# Login profile
def LoginProfile():
    global token
    global active
    connection = ConnectDatabase()
    cursor = connection.cursor()

    print("_" * 30)
    
    if token == 'LoginUser':
        print("           LOGIN\n")

        while True:
            username = input("Enter your username: ").strip()

            cursor.execute("SELECT password FROM profiles WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result:
                if username.lower() == 'admin':
                    print("Insufficient Permissions!")
                    token, active = 'Home', None
                    break

                elif username.lower() == 'guest':
                    print("\nWelcome, Guest!\n")
                    token, active = 'UserMenu', 'Guest'
                    break

                else:
                    password = input("Enter your password: ").strip()

                    if password == result[0]:
                        print("Welcome " + username + "!")
                        token, active = 'UserMenu', username
                        break
                    
                    else:
                        print("Incorrect password!")

            else:
                print("Username not found!")
                token, active = 'Home', None
                break

    elif token == 'LoginAdmin':
        print("        ADMIN LOGIN\n")

        cursor.execute("SELECT password FROM profiles WHERE username = 'admin'")
        result = cursor.fetchone()

        if result:
            password = input("Enter admin password: ").strip()

            if password == result[0]:
                print("\nWelcome, Admin!\n")
                token, active = 'AdminMenu', 'Admin'
            else:
                print("Incorrect password! Access denied.")
                token, active = 'Home', None
                
    cursor.close()
    connection.close()

#Profile Recovery
def ProfileRecovery():
    connection = ConnectDatabase()
    cursor = connection.cursor()

    print("_" * 30)
    print("       PROFILE RECOVERY\n")

    username = input("Enter the username for password recovery: ").strip()

    cursor.execute("SELECT password FROM profiles WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        password = result[0]
        
        if len(password) > 1:
            maskedPassword = password[0] + '*' * (len(password) - 2) + password[-1]
            print("Password hint:", maskedPassword)
            
        else:
            print("Password hint: *")
    else:
        print("Username not found! Unable to recover password.")

    cursor.close()
    connection.close()

#Change username and password
def UpdateProfile():
    connection = ConnectDatabase()
    cursor = connection.cursor()

    print("_" * 30)
    print("       UPDATE PROFILE\n")

    currentUsername = input("Enter your current username: ").strip()
    
    if currentUsername.lower() in ['admin', 'guest', 'Admin', 'Guest']:
        print("Permission denied for this profile!")
        cursor.close()
        connection.close()
        return
    
    currentPassword = input("Enter your current password: ").strip()

    cursor.execute("SELECT password FROM profiles WHERE username = %s", (currentUsername,))
    result = cursor.fetchone()

    if result and result[0] == currentPassword:
        print("Username and password verified!")

        newUsername = input("Enter a new username: ").strip()
        newPassword = input("Enter a new password: ")

        while True:
            choice = input("Confirm update of profile? Enter Y/N (Yes/No): ").lower().strip()
            
            if choice in ['y', 'yes']:
                try:
                    cursor.execute(
                        "UPDATE profiles SET username = %s, password = %s WHERE username = %s",
                        (newUsername, newPassword, currentUsername)
                    )
                    connection.commit()
                    print("Profile username updated successfully!")
                    return

                except Exception as e:
                    return e
                    
            elif choice in ['n', 'no']:
                print("Profile update cancelled!")
                break
            
            else:
                print("Invalid input, please enter Y or N.")

    else:
        print("Incorrect username or password. Update aborted!")

    cursor.close()
    connection.close()

# Sends feedback from user to database
def SendFeedback(username, feedback):
    connection = ConnectDatabase()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT feedback FROM profiles WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            if result[0]:
                existingFeedback = result[0]
            else:
                existingFeedback = '[]'
            if existingFeedback != '[]':
                feedbackList = json.loads(existingFeedback)
            else:
                feedbackList = []
            feedbackList.append(feedback)
            newFeedback = json.dumps(feedbackList)

            cursor.execute(
                "UPDATE profiles SET feedback = %s WHERE username = %s",
                (newFeedback, username)
            )
            connection.commit()
            print("Thank you for your feedback! We value your time.")
            
        else:
            print("User not found!")

    except mysql.connector.Error as e:
        print("An error occurred while updating feedback. Please try again!")
        
    finally:
        cursor.close()
        connection.close()

# Bookmark controls for user
def EditBookmark(bookmark, mode=0):
    global token
    global active
    connection = ConnectDatabase()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT bookmarks FROM profiles WHERE username = %s", (active,))
        result = cursor.fetchone()

        if result:
            existingBookmarks = result[0] if result[0] else '[]'
            bookmarkList = json.loads(existingBookmarks)

            if mode == 0:
                if bookmark not in bookmarkList:
                    bookmarkList.append(bookmark)
                    print("Place added to Bookmarks Archive!")
                else:
                    print("Bookmark already exists in Archive!")

            elif mode == 1:
                if bookmark in bookmarkList:
                    bookmarkList.remove(bookmark)
                    print("Place removed from Bookmarks Archive!")
                else:
                    print("Bookmark not found in Archive!")
                    return

            updatedBookmarks = json.dumps(bookmarkList)
            cursor.execute(
                "UPDATE profiles SET bookmarks = %s WHERE username = %s",
                (updatedBookmarks, active)
            )
            connection.commit()

        else:
            print("User not found!")

    except mysql.connector.Error as e:
        print("An error occurred while updating bookmarks! Please try again.")

    finally:
        cursor.close()
        connection.close()

    while token == 'Bookmark':
        tokenToChoice = GetBookmarks()
        if not tokenToChoice:
            print("Bookmarks Archive Empty")
            print("First add places here!")
            token = 'UserMenu'
            break
        else:
            valid, maxLength = DisplayOptions(token, tokenToChoice)
            availableKeys = list(valid.keys())

            while True:
                choice = input("\nEnter 'key' for more info. or 'B' to go back: ").strip().lower()

                if choice in availableKeys:
                    selectedItem = tokenToChoice[int(choice) - 1]
                    DisplayMoreInfo(selectedItem, maxLength)

                    while True:
                        moreInfoChoice = input("Enter 'F' to remove bookmark or 'B' to go back: ").lower()
                        if moreInfoChoice == "b":
                            break

                        elif moreInfoChoice == "f":
                            EditBookmark(selectedItem, 1)
                            tokenToChoice = GetBookmarks()

                            if not tokenToChoice:
                                print("Bookmarks Archive Empty")
                                token = 'UserMenu'
                            break
                    break

                elif choice in ['b', 'back']:
                    token = 'UserMenu'
                    break

                else:
                    print("\nInvalid choice. Please enter a valid option or 'back'.\n")

# Handles choice to token for user 
def ChoiceHandler(choiceName, mode = None):
    while True:
        choice = input("Enter the number or option: ").strip().lower()

        if choice in TokenHandler(choiceName, 0):
            return TokenHandler(choiceName, choice)
        
        else:
            print("\nInvalid choice. Please enter a valid option.\n")

# Generates the formatted screens
def ScreenGenerator(screen):
    options, heading = GetOptions(screen + 'Options'), screen.upper() + " OPTIONS"

    maxLength = max(len(option) for option in options)

    print(" " * ((maxLength + 4 - len(heading)) // 2) + heading)
    print("╭" + "─" * (maxLength + 3) + "╮")
    for option in options:
        padding = " " * (maxLength - len(option))
        print("│ " + option + padding + "   │")
    print("╰" + "─" * (maxLength + 3) + "╯")
    print()

# Displays available options with basic details
def DisplayOptions(token, choice):
    valid = {}
    maxLength = 0
    
    for item in choice:
        addressLength = len(item.get("Address", ""))
        timingsLength = len(item.get("Timings", ""))
        
        prosLength = 0
        if 'Pros' in item:
            for pro in item['Pros']:
                prosLength = max(prosLength, len(pro))
        consLength = 0
        if 'Cons' in item:
            for con in item['Cons']:
                consLength = max(consLength, len(con))
                
        itemMaxLength = max(addressLength, timingsLength, prosLength, consLength) + 9
        maxLength = max(maxLength, itemMaxLength)
            
    for index, item in enumerate(choice, start = 1):
        print("=" * (maxLength + 4))
        print("| Key: " + str(index).ljust(maxLength - 5) + " |")
        print("| Name: " + item['Name'].ljust(maxLength - 6) + " |")
        print("| Rating: " + str(item['Rating']).ljust(maxLength - 8) + " |")
        print("| Address: " + item['Address'].ljust(maxLength - 9) + " |")
        print("| Timings: " + item['Timings'].ljust(maxLength - 9) + " |")
        print("=" * (maxLength + 4))
        valid[str(index)] = item

    return valid, maxLength

# Display detailed info for a chosen item
def DisplayMoreInfo(item, maxLength):
    Days = ["Monday    ", "Tuesday   ", "Wednesday ", "Thursday  ", "Friday    ", "Saturday  ", "Sunday    "]
    Rating = ["Food       ", "Service    ", "Value      ", "Atmosphere "]
    
    print("=" * (maxLength + 4))
    print("| Name: ".upper() + item['Name'].ljust(maxLength - 6) + " |")
    
    if "moreRatings" in item:
        DisplayRatings(item, Rating, maxLength)
        
    else:
        print("| Rating: ".upper() + str(item['Rating']).ljust(maxLength - 8) + " |")
    
    DisplayAdditionalDetails(item, maxLength, Days)
    print("=" * (maxLength + 4))

# Display specific ratings for an item
def DisplayRatings(item, Rating, maxLength):
    ratings = item.get('moreRatings', [])
    
    if len(ratings) == len(Rating):
        for idx, ratingName in enumerate(Rating):
            try:
                ratingValue = float(ratings[idx])
                fullStars = int(ratingValue)
                halfStars = ratingValue - fullStars

                totalStarsCount = '●' * fullStars
                halfStarsCount = '◖' * int(halfStars * 2)
                totalStars = totalStarsCount + halfStarsCount

                ljustValue = maxLength - len(ratingName) - len(totalStarsCount) - len(halfStarsCount) + 15
                if ratingValue <= 4:
                    ljustValue -= 1
                elif ratingValue <= 3:
                    ljustValue -= 2
                
                print("| ", ratingName, ": ", totalStars, " " * (ljustValue - len(ratingName) - len(totalStars)), "|", sep = "")
                
            except ValueError:
                print(("| " + ratingName + ": No rating available").ljust(maxLength + 2) + " |")

# Display other details
def DisplayAdditionalDetails(item, maxLength, Days):       
    if 'Price' in item:
        print("| Price: ".upper(), "".ljust(maxLength - 8), "|")
        for price in item.get('Price', []):
            print("| ", price.ljust(maxLength - 1), "|")

    if 'timingsPerDay' in item:
        item['Specific Timings'] = {}
        for day, timing in zip(Days, item['timingsPerDay']):
            item['Specific Timings'][day] = timing
        
        specificTimings = item['Specific Timings']
        print("| Specific Timings: ".upper(), "".ljust(maxLength - 19), "|")
        for day, timing in specificTimings.items():
            print("| ", day + ": " + timing.ljust(maxLength - 13), "|")

    if 'Amenities' in item:
        print("| Amenities: ".upper(), "".ljust(maxLength - 12), "|")
        for amenity in item.get('Amenities', []):
            print("| ", amenity.ljust(maxLength - 1), "|")

    if 'Contact Information' in item:
        print("| Contact Information: ".upper(), "".ljust(maxLength - 22), "|")
        for contact in item.get('Contact Information', []):
            print("| ", contact.ljust(maxLength - 1), "|")

    if 'Pros' in item:
        print("| Pros: ".upper(), "".ljust(maxLength - 7), "|")
        for pro in item.get('Pros', []):
            print("| ", pro.ljust(maxLength - 1), "|")

    if 'Cuisines' in item:
        print("| Cuisines: ".upper(), "".ljust(maxLength - 11), "|")
        for cuisine in item.get('Cuisines', []):
            print("| ", cuisine.ljust(maxLength - 1), "|")

    if 'Opened' in item:
        print("| Opened: ".upper(), "".ljust(maxLength - 9), "|")
        print("| ", item['Opened'].ljust(maxLength - 1), "|")

    if 'Floors' in item:
        print("| Floors: ".upper(), "".ljust(maxLength - 9), "|")
        print("| ", item['Floors'].ljust(maxLength - 1), "|")

    if 'Cons' in item:
        print("| Cons: ".upper(), "".ljust(maxLength - 7), "|")
        for con in item.get('Cons', []):
            print("| ", con.ljust(maxLength - 1), "|")

    if 'Parking' in item:
        print("| Parking: ".upper(), "".ljust(maxLength - 10), "|")
        print("| ", item['Parking'].ljust(maxLength - 1), "|")

    if 'Special Diets' in item:
        print("| Special Diets: ".upper(), "".ljust(maxLength - 16), "|")
        for specialDiet in item.get('Special Diets', []):
            print("|   ", specialDiet.ljust(maxLength - 3), "|")

    if 'No. of stores and services' in item:
        print("| No. of stores and services: ".upper(), "".ljust(maxLength - 29), "|")
        print("| ", item['No. of stores and services'].ljust(maxLength - 1), "|")
        
# Display all profiles
def DisplayAllProfiles(mode = 0):
    connection = ConnectDatabase()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM profiles")
        profiles = cursor.fetchall()
        
        print("=" * 40)
        if mode == 0:
            print("           ALL PROFILE DATA")
        elif mode == 1:
            print("           PASSWORD MANAGER")
        print("=" * 40)
        
        for profile in profiles:
            username, password, bookmarks, feedback, created, updated = profile
            
            print("Username:", username)
            
            if mode == 0:
                print("Password:", "*" * len(password))
                print("Feedback:", feedback)
                print("Created:", created)
                print("Updated:", updated)
                print("Bookmarks:", bookmarks)
                
            elif mode == 1:
                print("Password:", password)
            print("_" * 40 + '\n')
            
    except mysql.connector.Error as e:
        return e
    
    finally:
        cursor.close()
        connection.close()

# Retrieves the bookmarks
def GetBookmarks():
    connection = ConnectDatabase()
    cursor = connection.cursor()
    global active
    
    try:
        cursor.execute("SELECT bookmarks FROM profiles WHERE username = %s", (active,))
        result = cursor.fetchone()
        
        return json.loads(result[0]) if result and result[0] else []
    
    except mysql.connector.Error as e:
        print("An error occurred while retrieving bookmarks:", e)
        return []
    
    finally:
        cursor.close()
        connection.close()

# Welcome Screen
note = '''
Please make sure these are set for the best experience :}
(Restart for changes to take effect)
    FONT:   Consolas
    Size:   12
    Bold:   Enabled
Once set press Enter and get right into my program!
'''

print(note)
input()
print("\n" + "=" * 40)
print("Welcome to the Weekend Planner Program!")
print("=" * 40)
print("        Press Enter to Continue")
print("=" * 40 + "\n")

car = '''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡤⠴⠒⠂⠂⠉⠉⠉⠉⠉⠉⠉⠉⢙⡛⠳⢤⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠿⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⢶⣶⡶⢶⣾⣿⣿⣽⣿⠈⠈⣧⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣅⠈⣾⢀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⢸⣿⣗⡞⠀⠀⠀⠀⣿⠀⠀⢸⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⢄⡀⠀⣈⣸⣧⣴⣿⡷⠶⠶⠶⠿⠷⢶⣶⣤⣤⢏⣇⠠⠤⣴⣖⣲⠭⠽⠦⣤⣤⣆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣷⣯⣖⣲⠽⠟⠛⠉⠉⠉⢀⣀⣀⣀⠤⠤⣴⢋⡝⢉⣉⢿⣷⠴⠭⠭⠗⠒⠒⠉⠉⡽⢋⣹⣇⠀
⠀⠀⠀⠀⠀⠀⣀⣤⢶⡤⣄⣿⣽⣿⣶⣿⣷⣭⣷⣶⣒⣚⡉⠩⠤⠦⠶⠒⠒⢺⠃⡼⣰⢻⣼⣯⣇⠀⠀⠀⠀⠀⠀⠀⢸⢡⢟⡻⣿⣶
⠀⠀⠀⢀⡔⡻⠛⣇⠀⢹⣸⣿⣿⣿⣿⣿⣿⠁⠈⠱⣹⠀⢀⡤⠔⠒⠒⠒⠲⢿⣀⡇⣟⣒⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⣾⣾⣿⣿⣿⣿
⠀⠀⢠⠏⡜⠁⠀⠘⠷⣿⣿⣿⣿⣿⣿⣿⣿⣧⣀⣴⣿⠞⠉⠀⠀⠀⠀⢀⣀⣀⠈⠙⠧⣼⣻⡟⡟⠀⠀⠀⠀⠀⠀⠀⣏⣿⣿⣽⡏⠋
⠀⠀⢸⢰⠁⢀⣤⣠⠶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⢀⡴⠛⠻⣿⣷⡄⠀⠀⠉⠓⠣⠤⣄⣀⣀⣠⣤⣶⡿⠿⣿⣿⠃⠀
⣠⣄⠈⣆⠀⠹⣄⡿⣿⣿⡀⢘⣿⣿⡟⠉⣿⣿⠏⠀⠀⠀⠀⠀⡴⢋⢤⣶⣤⠈⣿⣷⠀⠀⠀⠀⢀⣀⡠⠴⠞⠛⠉⠁⠑⠤⠟⠁⠀⠀
⠫⢍⣙⣚⣿⣶⣾⣿⣿⣿⣿⣾⣿⣿⣿⣦⠛⠁⠀⠀⠀⠀⢀⣾⢡⣟⣦⣿⣿⡆⢿⠟⠧⠤⠖⠚⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠙⣟⣯⡿⠿⠿⢿⣾⣯⣥⣌⡉⠉⠑⠒⠒⠤⠾⣿⡇⣸⣾⣿⣿⡿⡇⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠻⠧⣤⡄⣀⣀⡈⢹⡀⠈⠉⠁⠒⠒⠒⡖⢻⡅⢫⣿⣿⣻⡽⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠒⠒⠒⠒⠒⠒⠒⠒⠹⠹⡀⢧⠈⠻⠿⠛⢀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠑⠮⣷⣦⡤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
'''

print(car)
print("Note: Data accurate upto 01/01/24")
input()

while True:
# Home Screen
    if token == 'Home':
        print("_" * 30)
        print("           MAIN MENU")
        print("_" * 30)
        print("Choose an option to continue:")
        
        options = GetOptions('HomeOptions')
        if options:
            for option in options:
                print(option)
        print("_" * 30)

        token, active = ChoiceHandler('ChoiceHome', 1), 'Guest'

# Profile Login
    if token == 'Profile':
        CreateProfile()
        token = 'Home'
                    
# Login
    if token == 'LoginUser' or token == 'LoginAdmin':
        LoginProfile()
        
# Recovery 
    if token == 'Recovery':
        ProfileRecovery()
        token = 'Home'

# Delete
    if token == 'Delete':
        print("_" * 30)
        print("           PROFILE DELETION\n")

        # Prevent deletion of the guest profile
        if active.lower() == 'guest':
            print("The guest profile cannot be deleted.")
            token = 'Home'
        else:
            reason = input("Enter a reason for appealing the deletion of your account: ").strip()
            password = input("To confirm deletion, please enter your password: ").strip()

            connection = ConnectDatabase()
            cursor = connection.cursor()

            cursor.execute("SELECT password FROM profiles WHERE username = %s", (active,))
            result = cursor.fetchone()

            if result:
                storedPassword = result[0].strip()
                if storedPassword == password:
                    cursor.execute("DELETE FROM profiles WHERE username = %s", (active,))
                    connection.commit()
                    print("Your account has been successfully deleted.")
                else:
                    print("Incorrect password. Deletion cancelled.")
            else:
                print("Account not found. Deletion cancelled.")

            cursor.close()
            connection.close()
            token = 'Home'

# Update
    if token == 'Update':
        UpdateProfile()
        token = 'Home'
    
#Suggestion
    if token == 'Suggestion':
        print("_" * 30)
        print("           ANONYMOUS SUGGESTION\n")

        suggestion = input("Enter an anonymous suggestion we can add: ").strip()

        Suggestions.append(suggestion)

        print("Thank you for suggesting this, our admins will look into it!")
        token = 'Home'

# Menu Screen
    while token == 'UserMenu':
        ScreenGenerator(token)
                
        token = ChoiceHandler('Choice' + token, 1)
            
# View Screen
        if token == 'View':
            ScreenGenerator(token)

            token = ChoiceHandler('Choice' + token, 1)

#Feedback Screen
        if token == 'Feedback':
            print("_" * 30)
            print("           Feedback\n")

            feedback = input("We would love to hear how your experience was: ").strip()

            if feedback:
                SendFeedback(active, feedback)
            else:
                print("\nInvalid, please try again!")
                    
            token = 'UserMenu'
                        
# Randomise Screen
        if token == 'Randomise':                
            print("\nThis will provide a random location out of our database, see where our program takes you!")
                
            while True:
                choice = input("Continue? (Y/N): ").strip().lower()

                if choice in ['y', 'n', 'yes', 'no', 'continue']:
                    break
                else:
                    print("\nInvalid choice. Please enter a valid option.\n")
                        
            if choice in ['n', 'no']:
                token = 'UserMenu'

            elif choice in ['y', 'yes', 'continue']:
                token = random.choice(TokenHandler('ChoiceEntertainment') + TokenHandler('ChoiceCultural') + TokenHandler('ChoiceRecreational') + TokenHandler('ChoiceEateries'))
                    
# Screens
        if token in ['Entertainment', 'Cultural', 'Recreational', 'Eateries']:
            ScreenGenerator(token)
                
            token = ChoiceHandler('Choice' + token, 1)

# Options + More info. Screen
        while token != 'Bookmark' and token in (TokenHandler('ChoiceEntertainment') + TokenHandler('ChoiceCultural') + TokenHandler('ChoiceRecreational') + TokenHandler('ChoiceEateries') + ['Mall']):
            tokenToChoice = GetLists(token)
            valid, maxLength = DisplayOptions(token, tokenToChoice)
            availableKeys = list(valid.keys())

            while True:
                choice = input("\nEnter 'key' for more info. or 'B' to go back: ").strip().lower()

                if choice in availableKeys:
                    selectedItem = tokenToChoice[int(choice) - 1]
                    DisplayMoreInfo(selectedItem, maxLength)
                        
                    while True:
                        moreInfoChoice = input("Enter 'F' to bookmark or 'B' to go back: ").lower()
                        
                        if moreInfoChoice == "b":
                            break
                        elif moreInfoChoice == "f":
                            EditBookmark(selectedItem, 0)
                            break
                    break
                
                elif choice in ['b', 'back']:
                    token = 'UserMenu'
                    break
                else:
                    print("\nInvalid choice. Please enter a valid option or 'back'.\n")

# Bookmarks screen
        while token == 'Bookmark':
            tokenToChoice = GetBookmarks()
            
            if not tokenToChoice:
                print("Bookmarks Archive Empty")
                print("First add places here!")
                token = 'UserMenu'
                break
            
            else:
                valid, maxLength = DisplayOptions(token, tokenToChoice)
                availableKeys = list(valid.keys())

                while True:
                    choice = input("\nEnter 'key' for more info. or 'B' to go back: ").strip().lower()

                    if choice in availableKeys:
                        selectedItem = tokenToChoice[int(choice) - 1]
                        DisplayMoreInfo(selectedItem, maxLength)
                            
                        while True:
                            moreInfoChoice = input("Enter 'F' to remove bookmark or 'B' to go back: ").lower()
                            if moreInfoChoice == "b":
                                break
                            
                            elif moreInfoChoice == "f":
                                EditBookmark(selectedItem, 1)
                                tokenToChoice = GetBookmarks()
                                
                                if not tokenToChoice:
                                    print("Bookmarks Archive Empty")
                                    token = 'UserMenu'
                                break
                        break
                    
                    elif choice in ['b', 'back']:
                        token = 'UserMenu'
                        break
                    
                    else:
                        print("\nInvalid choice. Please enter a valid option or 'back'.\n")
                  
#Admin
    while token == 'AdminMenu':
        ScreenGenerator(token)
                
        token = ChoiceHandler('Choice' + token, 1)

#View Profiles
        if token == 'ViewProfile':
            DisplayAllProfiles(0)
            token = 'AdminMenu'

# View Passwords
        if token == 'PasswordManager':
            while True:
                try:
                    hashInput = (input("Enter security hashkey: "))
                    
                    if hashInput == '00000000':
                        DisplayAllProfiles(1)
                        token = 'AdminMenu'
                        break
                    else:
                        print("Incorrect hashkey! Permission denied.")
                        token = 'AdminMenu'
                        break
                    
                except ValueError:
                    print("Invalid input. Please enter a numerical hash.")

#View Suggestions
        while token == 'ViewSuggestion':
            if not Suggestions:
                print("\nNo suggestions available!")
                token = 'AdminMenu'
                
            else:
                print("\nAvailable Suggestions:")
                for index, suggestion in enumerate(Suggestions, start = 1):
                    print(index, ".", suggestion)
                print("Enter R/I/M/B to Remove, mark as Implied, Mass delete, or go Back respectively: ")

                token = ChoiceHandler('ChoiceSuggestion', 1)

                while token == 'RemoveSuggestion':
                    choice = input("Enter serial no. from above options or enter 'B' to cancel: ").strip()
                    
                    if choice in 'bB':
                        token = 'ViewSuggestion'
                    elif choice.isdigit():
                        key = int(choice) - 1

                        if 0 <= key < len(Suggestions):
                            Suggestions.pop(key)
                            print("Suggestion '", choice,  "' removed successfully!")
                            token = 'AdminMenu'
                        else:
                            print("Invalid serial no. Please enter a valid option.")
                    else:
                        print("Invalid input. Please enter a valid number.")

                while token == 'MassDelSuggestion':
                    choice = input("Enter the start serial no. or enter 'B' to cancel: ").strip()

                    if choice in 'bB':
                        token = 'ViewSuggestion'
                    elif choice.isdigit():
                        start = int(choice) - 1
                        if 0 <= start < len(Suggestions):
                            choice = input("Enter the end serial no.: ").strip()

                            if choice.isdigit():
                                end = int(choice) - 1

                                if start <= end < len(Suggestions):
                                    removedTemp = []
                                        
                                    for i in range(end, start - 1, -1):
                                        removedTemp.append(Suggestions.pop(i))
                                        token = 'AdminMenu'
                                else:
                                    print("Invalid end serial no.!")
                            else:
                                print("Invalid input!")
                        else:
                            print("Invalid start serial no.!")
                    else:
                        print("Invalid input!")
                        
                while token == 'ImpliedSuggestion':
                    choice = input("Enter serial no. from above options or enter 'B' to cancel: ").strip()
                        
                    if choice in 'bB':
                        token = 'ViewSuggestion'
                    elif choice.isdigit():
                        key = int(choice) - 1

                        if 0 <= key < len(Suggestions):
                            Implied.append(Suggestions[key])
                            Suggestions.pop(key)
                            print("Suggestion '", choice, "' added successfully!")
                            token = 'AdminMenu'
                        else:
                            print("Invalid serial no. Please enter a valid option.")
                    else:
                        print("Invalid input. Please enter a valid number.")
                            
#Implied Suggestions
        while token == 'Implied':
            if not Implied:
                print("\nNo suggestions to view!")
                token = 'AdminMenu'
                
            else:
                print("\nImplied Suggestions:")
                for index, implied in enumerate(Implied, start = 1):
                    print(index, ".", implied)
                print("Enter R/B to Remove or go Back respectively: ")

                token = ChoiceHandler('ChoiceSuggestion', 1)

                while token == 'RemoveSuggestion':
                    choice = input("Enter serial no. from above options or enter 'B' to cancel: ").strip()
                        
                    if choice in 'bB':
                        token = 'AdminMenu'
                    elif choice.isdigit():
                        key = int(choice) - 1

                        if 0 <= key < len(Implied):
                            Implied.pop(key)
                            print("Suggestion '", choice, "' removed successfully!")
                            token = 'AdminMenu'
                        else:
                            print("Invalid serial no. Please enter a valid option.")
                    else:
                        print("Invalid input. Please enter a valid number.")

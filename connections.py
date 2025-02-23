import requests
from bs4 import BeautifulSoup
import datetime
import sys
import random
from keyword import iskeyword
from calendar import monthrange

class ConnectionGame():
    def __init__(self):
        self.lives = 4
        self.attempts = 0

    def input_date(self):
        while True:
            try:
                year = int(input("Enter year:"))
                if year < 2023 or year > 2025:
                    print("Error: Invalid Year. Try Again\n")
                else:break
            except ValueError:
                print("Error: Year must be between 2023 and 2025 (inclusive).\n")
                    
        while True:
            try:
                month = int(input("Enter month:"))
                if (month < 1 or month > 12) or (year == 2023 and (month<6 or month>12)):
                    print("Error: Invalid Month. Try Again\n")
                else:break
            except ValueError:
                print("Error: Month must be between 1 and 12 (inclusive).\n")
        while True:
            try:
                day = int(input("Enter day:"))
                is_day = monthrange(year,month)
                if (day < 1 or day > is_day[1]) or (year == 2023 and month == 6 and (day < 11 or day>is_day[1])):
                    print("Error: Invalid Day. Try Again\n")
                else: break
            except ValueError:
                print("Error: Only Numerical Values Between 1 and 12 are accepted.\n")
                print("Error: Only Numerical Values Between 1 and 12 are accepted.\n")
        return year,month,day
    def get_date(self):
        y,m,d = self.input_date()
        date = datetime.datetime(y,m,(d+1)) #Gets Date
        date = date.strftime(f'%B %d, %Y')
        return date
    def fetch(self):
        try:
            selected_date = self.get_date()
            url = 'https://wordfinder.yourdictionary.com/nyt-connections/todays-answers/' #URL to fetch
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text,'html.parser') #Parse data

                date_items = soup.find_all('li', class_='my-6') #Collect all data regarding dates
                
                if date_items:
                    for item in date_items:
                        # Find the paragraph containing the date
                        date_p = item.find('p', class_='text-base text-black-870 m-0 mb-3')
                        if selected_date in date_p.get_text().strip(): #Determines whether the date is correct
                            dictionary,spots = self.fetch_word(item) #Calls function to get the dictionary of words
                            break
            self.game(dictionary,spots)

        except requests.RequestException as e:
            print(f'Failed to fetch data: {e}', file=sys.stderr)
            return None

    def fetch_word(self,item):
        # Once we find the correct date, get all the text divs within this li
        main_header = []

        text_header = item.find_all('p', class_='inline-block font-bold text-black-870 text-base uppercase m-0 mx-3 leading-[34px] align-top overflow-hidden text-ellipsis whitespace-nowrap')
        for header in text_header:
            text = header.get_text(strip=True)
            if text:
                main_header.append(text)

        main_sub = []
        text_sub = item.find_all('p',class_='m-0 ml-3 mt-1 md:m-0 md:inline-block text-black-870 text-base leading-4 md:leading-[34px] uppercase align-top relative -top-[4px] md:top-0 md:shrink-0')
        for sub in text_sub:
            text = sub.get_text(strip=True)
            text = text.replace(' ','')
            prev_index = 0
            for i in range(len(text)):
                if text[i] == ',':
                    main_sub.append(text[prev_index:i])
                    prev_index = i + 1 #Skips the comma
                if i == len(text)-1: #Subtract one because length starts at 1 instead of 0
                    main_sub.append(text[prev_index:i+1]) #Add one as index starts at 0

        #Creates HEADER:4 TEXT -> {'WREST': 'WRENCH','YANK','TUG','JERK'}
        assignment = {}
        prev_index = 0
        for i in range (len(main_header)):
            assignment[f'{main_header[i]}'] = main_sub[prev_index:4*(i+1)]
            prev_index = 4*(i+1)
        
        #Creates the possible spots - Begins with 16 Spots -> 4x4
        spots = self.create_spots(main_sub)

        #Presents the arrangement of the words
        self.display(spots)

        return assignment,spots
    
    def create_spots(self,text):
        copy_text = text.copy()
        spots = {}
        for ele in range(len(text)):
            choice = random.choice(copy_text)
            spots[ele+1] = choice
            copy_text.remove(choice)
        return spots        

    def display(self,pos):
        rows = int(len(pos)/4)
        prevIndex = 0
        board_display = '----------------------\n'
        for row in range (rows):
            for col in range (4):
                board_display+= f'{pos[(col+1)+ prevIndex]}|'
            board_display += '\n----------------------\n'
            prevIndex = (row+1)*4
        print(board_display)

    def game(self,dictionary,spots):
        while True:
            if self.lives == 0:
                print("You RAN OUT OF LIVES :(\nHere are the CORRECT Solutions)")
                return
            if bool(spots) == False:
                print(f'You WON! Attempts: {self.attempts}')
                return
            guess_list,check =  self.is_valid(spots)
            while check == False:
                self.user_guess(spots)
                guess_list,check =  self.is_valid(spots)
                if check == True:
                    break
            self.guess_check(guess_list,dictionary,spots)

    def user_guess(self,spots):
        guess = input(f"Choices are between 1-{len(spots)}: ")     
        while len(guess) < 7 or len(guess) > 12 and (',' not in guess or ' ' not in guess):
                    print("INVALID - Please space out your choices using commas or a space. Ex. 4,5,6,7 or 4 5 6 7")
                    guess = input("ENTER Your Four Guesses: ")
                    if 7<=len(guess)<=12 and (',' in guess or ' ' in guess):
                        break
        return guess
    
    def is_valid(self,spots):
        guess = self.user_guess(spots)
        guess_list = []
        prev_index = 0
        #Remove commas or spaces from user input
        for i in range(len(guess)):
            if guess[i] == ',' or guess[i] == ' ':
                guess_list.append(guess[prev_index:i])
                prev_index = i + 1
            if i == len(guess)-1:
                guess_list.append(guess[prev_index:i+1])
        #Get the header of each response
        for i in guess_list:
            if i.isdigit() ==  False or spots.get(int(i)) == None:
                return guess_list,False
        return guess_list,True

    def guess_check(self,list,dictionary,spots):
            k = []
            for i in range(len(list)):
                for key, value in dictionary.items():
                    if spots[int(list[i])] in value:
                        k.append(key)
            print(k)
            is_equal = all(i == k[0] for i in k)
            if is_equal == True:
                print("Guessed Correctly!")
                print(f"{k[0]} - {dictionary[k[0]]}")
                items = []
                for key in spots:
                    for value in dictionary[k[0]]:
                        if spots[key] == value:
                            items.append(key)
                for item in items:
                    spots.pop(item)
                new_sub = []
                for key in spots:
                    new_sub.append(spots[key])
                spots = self.create_spots(new_sub)
                self.display(spots)
            else:
                self.lives -= 1
                print(f"Wrong Solution: Lives {self.lives}/4")
                self.display(spots)
            self.attempts += 1

if __name__ == "__main__":
    connection = ConnectionGame()
    connection.fetch()

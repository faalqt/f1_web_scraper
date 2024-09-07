import requests
from bs4 import BeautifulSoup
import json

def fetch_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def fetch_driver_standings(year):
    soup = fetch_soup(f'https://www.formula1.com/en/results/{year}/drivers')
    driver_standings = soup.find_all('tr', ['bg-brand-white', 'bg-grey-10'])
    driver_standings.pop(0)

    
    for element in driver_standings:
        pos = element.find('p').text
        driver = element.find_all('span', ['max-desktop:hidden', 'max-tablet:hidden'])
        print(pos, driver)


def fetch_races(year):
    race_list_url = f'https://www.formula1.com/en/results/{year}/races'
    soup = fetch_soup(race_list_url)
    year_race_list = soup.find_all('tr', ['bg-brand-white', 'bg-grey-10'])
    year_race_list.pop(0)

    races = []
    for race in year_race_list:
        grand_prix = race.find('a', ['underline underline-offset-normal decoration-1 decoration-greyLight hover:decoration-brand-primary']).text
        grand_prix_link = race.find('a', ['underline underline-offset-normal decoration-1 decoration-greyLight hover:decoration-brand-primary'])['href']
        remaining_data = race.find_all('td', ['p-normal default:max-mobile:collapse default:max-mobile:max-w-0 default:max-mobile:hidden mobile:max-tablet:collapse mobile:max-tablet:max-w-0 mobile:max-tablet:hidden whitespace-nowrap'])
        date = remaining_data[0].text
        laps = remaining_data[1].text
        race_id = grand_prix_link[6: grand_prix_link.find('/', 6, len(grand_prix_link)-1)]
        
        races.append({
            'race_id': race_id,
            'grand_prix': grand_prix,
            'date': date,
            'laps': laps
        })

    return races

# grand_prix is a string equal to the name of the grand prix
def fetch_session_results(year, grand_prix, session_type):
    race_list = fetch_races(year)
    session_types = {'race':'race-result',
                     'fastest_laps': 'fastest-laps',
                     'pit_stops':'pit-stop-summary',
                     'start_grid': 'starting-grid', 
                     'qual': 'qualifying', 
                     'sprint': 'sprint-results',
                     'sprint_grid': 'sprint-grid',
                     'sprint_qual': 'sprint-qualifying'}
    selected_race = {}
    selected_session = ''
    

    for race in race_list:
        if race['grand_prix'] == grand_prix:
            selected_race = race
            break
    # print(selected_race)
    # {'race_id': '1244', 'grand_prix': 'Italy', 'date': '01 Sep 2024', 'laps': '53'}
    selected_race_url = f'https://www.formula1.com/en/results/{year}/races/{selected_race['race_id']}/{selected_race['grand_prix']}/{session_type}'
    soup = fetch_soup(selected_race_url)
    # race_result_roster = soup.find_all('tr', ['bg-brand-white', 'bg-grey-10'])


def main():
    # fetch_driver_standings(2024)
    # print(fetch_races(1950))
    fetch_session_results(2024, 'Italy', 'race')

if __name__ == '__main__':
    main()
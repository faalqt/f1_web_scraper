import requests
from bs4 import BeautifulSoup
import json

def fetch_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

#i think this will be useless as I plan to re-create this in the SQL db
def fetch_driver_standings(year):
    soup = fetch_soup(f'https://www.formula1.com/en/results/{year}/drivers')
    driver_standings = soup.find_all('tr', ['bg-brand-white', 'bg-grey-10'])
    driver_standings.pop(0)

    
    for element in driver_standings:
        pos = element.find('p').text
        driver = element.find_all('span', ['max-desktop:hidden', 'max-tablet:hidden'])
        print(pos, driver)

#returns the races for the year
def fetch_races(year):
    race_list_url = f'https://www.formula1.com/en/results/{year}/races'
    soup = fetch_soup(race_list_url)
    year_race_list = soup.find('table', ['f1-table f1-table-with-data w-full']).contents[1] # Make this a function?

    races = []
    for race in year_race_list:
        row = race.find_all('p', ['f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-none f1-text__micro text-fs-15px'])
        race_name = row[0].text
        race_link = row[0].find('a')['href']
        race_id = race_link[6:race_link.find('/', 6, len(race_link)-1)]
        race_date = row[1].text
        race_winner = row[2].text[0:len(row[2].text)-3].replace(u'\xa0', ' ')
        race_winner_tag = row[2].text[len(row[2].text)-3::]
        constructor = row[3].text
        laps = row[4].text
        duration = row[5].text

        races.append({
            'race_id': race_id,
            'race_name': race_name,
            'date': race_date,
            'race_winner': race_winner,
            'race_winnter_tag': race_winner_tag,
            'constructor': constructor,
            'laps': laps,
            'duration': duration
        })

    return races

# race_name is a string equal to the name of the grand prix according to the names here https://www.formula1.com/en/results/2024/races 
# i.e the Canadian GP is just "Canada"
def fetch_session_results(year, race_name, session_type):
    race_list = fetch_races(year)
    session_types = {'race':'race-result',
                     'fastest_laps': 'fastest-laps',
                     'pit_stops':'pit-stop-summary',
                     'start_grid': 'starting-grid', 
                     'qualifying': 'qualifying', 
                     'sprint': 'sprint-results',
                     'sprint_grid': 'sprint-grid',
                     'sprint_qualifying': 'sprint-qualifying'}
    selected_race = {}
    selected_session = session_types[session_type]
    
    #find info for the given race
    for race in race_list:
        if race['race_name'] == race_name:
            selected_race = race
            break

    selected_race_url = f'https://www.formula1.com/en/results/{year}/races/{selected_race['race_id']}/{selected_race['race_name']}/{selected_session}'
    soup = fetch_soup(selected_race_url)

    #finds the result table, ignoring the table on the side, then grabs the tbody
    session_results = soup.find('table', ['f1-table f1-table-with-data w-full']).contents[1] # Make this a function?

    race_results =[{
        'race_id': selected_race['race_id'],
        'race_name': selected_race['race_name'],
        'year': year,
        'date_of_race': selected_race['date'],
        'number_of_laps': selected_race['laps'],
        'session': session_type
    }]
    
    return (race_results + filter_race_results(session_results, session_type))

def filter_race_results(session_results, session_type):
    results = []
    for result in session_results:
        #grab all <p> tags in the row
        row = result.find_all('p', ['f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-none f1-text__micro text-fs-15px'])
        pos = row[0].text
        driver_number = row[1].text
        driver = row[2].text[0:len(row[2].text)-3].replace(u'\xa0', ' ')
        driver_tag = row[2].text[len(row[2].text)-3::]
        constructor = row[3].text
        laps_completed = row[4].text
        time = row[5].text
        points = row[6].text
        results.append({
            'pos': pos,
            'driver_number': driver_number,
            'driver_name': driver,
            'driver_tag': driver_tag,
            'constructor': constructor,
            'laps_completed': laps_completed,
            'time': time,
            'points': points
        })
    return results  

def main():
    # a = fetch_session_results(2024, 'Italy', 'race')
    a = fetch_races(2024)
    for x in a:
        print(x)

if __name__ == '__main__':
    main()
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

# grand_prix is a string equal to the name of the grand prix according to the names here https://www.formula1.com/en/results/2024/races 
# i.e the Canadian GP is just "Canada"
def fetch_session_results(year, grand_prix, session_type):
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
    
    for race in race_list:
        if race['grand_prix'] == grand_prix:
            selected_race = race
            break

    selected_race_url = f'https://www.formula1.com/en/results/{year}/races/{selected_race['race_id']}/{selected_race['grand_prix']}/{selected_session}'
    soup = fetch_soup(selected_race_url)
    session_results = soup.find('table', ['f1-table f1-table-with-data w-full']).contents[1]

    race_results =[{
        'race_id': selected_race['race_id'],
        'grand_prix': selected_race['grand_prix'],
        'year': year,
        'date_of_race': selected_race['date'],
        'number_of_laps': selected_race['laps'],
        'session': session_type
    }]
    
    for result in session_results:
        row = result.find_all('p', ['f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-none f1-text__micro text-fs-15px'])
        pos = row[0].text
        driver_number = row[1].text
        driver = row[2].text[0:len(row[2].text)-3].replace(u'\xa0', ' ')
        driver_tag = row[2].text[len(row[2].text)-3::]
        constructor = row[3].text
        laps_completed = row[4].text
        time = row[5].text
        points = row[6].text
        race_results.append({
            'pos': pos,
            'driver_number': driver_number,
            'driver_name': driver,
            'driver_tag': driver_tag,
            'constructor': constructor,
            'laps_completed': laps_completed,
            'time': time,
            'points': points
        })
    
    return race_results

def main():
    a = fetch_session_results(2011, 'Great Britain', 'race')
    for x in a:
        print(x)

if __name__ == '__main__':
    main()
import requests
from bs4 import BeautifulSoup
import configparser
import os

def get_url_from_config():
    #Functia acceseaza fisierul config.ini si preia URL-ul prezent, returnand-ul
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')
    config.read(config_path)
    return config['URL']['url']

def get_url_input():
    #Functia preia de la tastatura un URL, si il verifica sa fie valid, apoi il returneaza
    while True:
        url = input("Introduceți URL-ul: ")
        if url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            print("URL-ul trebuie să înceapă cu 'http://' sau 'https://'.")

def fetch_page_content(url):
    #Face o cerere de tip GET catre un URL specificat si returneaza continutul paginii
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Eroare la cererea paginii: {e}")
        return None

def extract_page_info(html_content):
    #Extrage titlul si descrierea unei pagini web
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string.strip() if soup.title else "N/A"
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag else "N/A"
        return title, description

def fetch_olx_results(url, search_keywords):
    #Functia face o cerere de tip GET catre OLX, utilizand URL-ul specificat si cuvintele de cautare din config.ini
    search_query = '-'.join(search_keywords.split())
    search_url = f"{url}/oferte/q-{search_query}/"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Eroare la cererea OLX: {e}")
        return None

def extract_olx_results(html_content):
    #Functia extrage titlurile si preturile anunturilor de pe OLX
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('div', class_='css-u2ayx9')

        results = []
        for item in items:
            title_tag = item.find('h6', class_='css-16v5mdi')
            title = title_tag.text.strip() if title_tag else "N/A"

            price_tag = item.find('p', class_='css-10b0gli')
            price = price_tag.text.strip() if price_tag else "N/A"

            results.append({'title': title, 'price': price})

        return results
    else:
        return None
def print_sorted_results(results):
    #Functia afiseaza in ordine crescatoare anunturile de pe OLX
    #Exista un mic bug in care preturile foarte mici sunt afisate dupa (exemplu: 6 800 60 7000)
    #Am avut probleme la transformarea din sir de caractere in numar, asa ca ordonarea nu este perfecta
    if results:
        sorted_results = sorted(results, key=lambda x: int(x['price']) if x['price'].isdigit() else x['price'])

        for result in sorted_results:
            print(f"Titlu: {result['title']}")
            print(f"Pret: {result['price']} ")
            print("---------------------")
    else:
        print("Nu s-au găsit rezultate.")

def main():
    use_config = input("Doriți să utilizați URL-ul din fișierul de configurare? (da/nu): ").lower()

    if use_config == 'da':
        url = get_url_from_config()
    elif use_config == 'nu':
        url = get_url_input()
    else:
        exit()

    html_content = fetch_page_content(url)

    if html_content:
        title, description = extract_page_info(html_content)
        print(f"Titlu: {title}")
        print(f"Descriere meta: {description}")
        
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')
    config.read(config_path)
    url = config['OLX']['url']
    search_keywords = config['OLX']['search_keywords']

    html_content = fetch_olx_results(url, search_keywords)

    results = extract_olx_results(html_content)
    print_sorted_results(results)

if __name__ == "__main__":
    main()

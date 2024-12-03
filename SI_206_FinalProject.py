import json
import re
import requests
import BeautifulSoup
headers = {'X-MAL-Client-ID': '6114d00ca681b7701d1e15fe11a4987e'}
resp = requests.get('https://api.myanimelist.net/v2/anime/search?status=not_yet_aired&limit=1&offset=0&fields=alternative_titles', headers=headers)
print(resp.json())

def get_RT_Info(url):
    content = 
    def get_listing_details(listing_id): 
    
  


    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, f"html_files/listing_{listing_id}.html")

    with open(full_path, 'r', encoding = "utf-8-sig") as file:
        content = file.read()
       #make beautiful soup object
        soup = BeautifulSoup(content, 'html.parser')

        listing_details= ()
        policy_info = soup.find("li", class_='f19phm7j')
        if policy_info:
            info = policy_info.get_text().strip().replace('\ufeff', '')
            if 'policy number: ' in info.lower():
                policy_match = re.search(r"Policy number:\s(.+)", info)
                if policy_match:
                    policy_number = policy_match.group(1)
            elif "pending" in info.lower():
                policy_number = "Pending"
            elif "exempt" in info.lower():
                policy_number = "Exempt"
        
        #get the host names & place types
        host_level_tag = soup.find('span', class_ = "_1mhorg9")
        if host_level_tag and host_level_tag.get_text() == 'Superhost':
            host_level = 'Superhost'
        else:
            host_level = 'Regular'


        host_names = "missing"
        place_type = "Entire Room"
        info_tag = soup.find('h2', class_ = '_14i3z6h')

        if info_tag:
            info = info_tag.get_text().strip().replace('\ufeff', '')
            #get host names
            if 'hosted by' in info:
                host_names = info.split('hosted by')[-1].strip()
            
            #get place type
            if "private" in info.lower():
                place_type = "Private Room"

            elif "shared" in info.lower():
                place_type = "Shared Room"
            
            #get number of reviews
        num_reviews = 0
        reviews_tag = soup.find('span', class_='_s65ijh7')
        if reviews_tag:
            review_info = reviews_tag.get_text().replace('\ufeff', '')
            num_reviews = int(''.join(filter(str.isdigit, review_info)))

        
        #get listing's nightly rate  
        nightly_rate = 0
        rate_info_tag = soup.find('div', class_ ='_1jo4hgw')
        if rate_info_tag:
            rate_text = rate_info_tag.get_text()
            rate_match = re.search(r'\$(\d+)', rate_text)
            if rate_match:
                nightly_rate = int(rate_match.group(1) )
        listing_details = (policy_number, host_level, host_names, place_type, num_reviews, nightly_rate)

    return listing_details


def get_MAL_ID(url): ## Picturing a string of a url or multiple as input
    patternID = r'myanimelist.net/anime/(d+)/w*'
    patternTitle = r'myanimelist.net/anime/d+/(w*)'
    MAL_ID =  re.findall(patternID, url)
    MAL_Titles = re.findall(patternTitle, url)
    

    

    ## Want to get specific id from animelist
    return 


def get_anime_details(id):
    url = f'https://api.jikan.moe/v4/anime/{id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

try:
    anime_details = get_anime_details(20)
    print(anime_details)
except Exception as e:
    print(e)
    #evie testing
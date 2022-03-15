import requests
from bs4 import BeautifulSoup

#purpose of file is to generate text file containing links to every highschool that needs to be scraped, will include some invalid links (wont follow format in next file_)

start_link = "https://www.niche.com/k12/search/best-public-high-schools/s/texas/?page="
#manually changing starting page and using vpn to change results b/c proxies weren't working
page_num = 65
#current num of pages on niche, subject to change
page_max = 83

#headers
agents = open("user_agents_firefox.txt", 'r')
headers = {"User-Agent":agents.readline().strip()}

#output file info
file = open("school_list2.txt", "a")

while(page_num<=page_max):
    print("Page "+str(page_num))
    main_search_page = requests.post(url=start_link+str(page_num), headers=headers)
    headers = {"User-Agent":agents.readline().strip()}
    if(main_search_page.status_code != 200):
        print("ERROR FAILED TO GET FIRST PAGE WITH REQUESTS. STATUS CODE "+str(main_search_page.status_code))

    search_page_soup = BeautifulSoup(main_search_page.content, 'html.parser')

    #filter results to find school links
    all_schools = search_page_soup.find_all("a", {"class":"search-result__link"})

    all_schools = [school['href'] for school in all_schools]
    for school in all_schools:
        file.write(school)
        file.write('\n')
    page_num+=1

from asyncore import write
from pip import main
import requests
from bs4 import BeautifulSoup
import csv
import time
from random import randint


start_link = "https://www.niche.com/k12/search/best-public-high-schools/s/texas/?page="
page_num = 1
#current num of pages on niche, subject to change
page_max = 83
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0"}
proxies = {}
output_file_name = "school_data.csv"

agents = open("user_agents_firefox.txt", 'r')

proxy_file = open("Free_Proxy_List.csv", 'r')
proxy_file.readline()


numTimes = randint(0,2030)
print(numTimes)
for i in range(numTimes):
    agents.readline()

with open(output_file_name, "a", newline='') as output:
    #get proxy ip from file, strip quotes
    proxies = {"http":proxy_file.readline().split(',')[0][1:-1]}
    try:
        headers = {"User-Agent": agents.readline().strip()}
        print(headers)
    except:
        agents.close()
        agents = open("user_agents_firefox.txt", 'r')
        headers = {"User-Agent": agents.readline().strip()}
    writer = csv.writer(output)
    writer.writerow(["School Name", "Niche Rank", "Number of Students", "Number of Seniors", "Proportion interested in UT", "Number of Seniors interested"])
    
    rank = 1
    #loop through all possible pages of texas highschool
    
    while(page_num <= page_max):
    
        main_search_page = requests.post(url=start_link+str(page_num), headers=headers, proxies=proxies)
        if(main_search_page.status_code != 200):
            print("ERROR FAILED TO GET FIRST PAGE WITH REQUESTS. STATUS CODE "+str(main_search_page.status_code))
            quit()

        search_page_soup = BeautifulSoup(main_search_page.content, 'html.parser')

        #filter results to find school links
        all_schools = search_page_soup.find_all("a", {"class":"search-result__link"})
        
        all_schools = [school['href'] for school in all_schools if (not (school.find("div", {"class": "search-result-badge"}) is None))]

        
        for school in all_schools:
            try:
                headers = {"User-Agent": agents.readline().strip()}
            except:
                agents.close()
                agents = open("user_agents_firefox.txt", 'r')
                headers = {"User-Agent": agents.readline().strip()}

            school_page = requests.post(school, headers=headers, proxies=proxies)
            numTries = 30
            while (school_page.status_code != 200):
                proxies = {"http":proxy_file.readline().split(',')[0][1:-1]}
                if(numTries == 30):
                    print("Errored on link: "+school)
                    print("Status Code: "+str(school_page.status_code))
                
                if(numTries%8==1):
                    print("sleeping, trying new header")
                time.sleep(1)
                headers = {"User-Agent": agents.readline().strip()}
                school_page = requests.post(school, headers=headers, proxies=proxies)
                numTries -=1
                if (numTries==0):
                    print("ERROR. DID NOT RECEIVE RESPONSE FOR SCHOOL PAGE REQUEST")
                    print(school_page.status_code)
                    quit()

                ##print("ERROR. DID NOT RECEIVE RESPONSE FOR SCHOOL PAGE REQUEST")
                #quit()
            
            school_soup = BeautifulSoup(school_page.content, 'html.parser')


            #first see if UT is a top choice in interested school
            school_names = school_soup.find_all("a", {"class":"popular-entity-link"})
            names = [sname.string for sname in school_names]
            if ("University of Texas - Austin" in names):
                #get school name
                school_title = school_soup.find("h1", {"class": "postcard__title postcard__title--claimed"})
                if(school_title is None):
                    school_title = school_soup.find("h1", {"class": "postcard__title"})
                school_title = school_title.string

                num_interested = school_soup.find_all("div", {"class":"popular-entity-descriptor"})
                num_interested = [n.contents[0].replace(',','') for n in num_interested]
                print(num_interested)
                UT_sum = 0
                total_sum = 0
                assert(len(num_interested)==len(names))
                for i in range(len(num_interested)):
                    if (names[i] == "University of Texas - Austin" ):
                        UT_sum+=int(num_interested[i])
                    total_sum+=int(num_interested[i])
                
                UT_proportion = UT_sum/total_sum
                student_section = school_soup.find("section", {"id":"students"})

                #compile stats
                num_students = float((student_section.find("div", {"class": "scalar__value"}).contents[0]).string.replace(',',''))
                num_seniors = num_students/4.0
                num_seniors_interested = num_seniors * UT_proportion
                print(school_title+": "+str(num_seniors_interested))
                writer.writerow([school_title, rank, num_students, num_seniors, UT_proportion, num_seniors_interested])
                rank += 1
        page_num += 1
agents.close()
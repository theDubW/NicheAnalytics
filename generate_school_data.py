from asyncore import write
import requests
from bs4 import BeautifulSoup
import csv
import time
from random import randint

school_list = open("Schools/school_list.txt").readlines()

#manually change start link in case of timeout/crash
start_link = 0
school_list = school_list[start_link:]

agents = open("UserAgents/user_agents_firefox.txt", 'r')
numTimes = randint(0,2030)

#output files
output_file_name = "Output/school_data.csv"
failed_links_file = "Output/failed_links.txt"
failed_writer = open(failed_links_file, "w")

for i in range(numTimes):
    agents.readline()

with open(output_file_name, "a", newline='') as output:
    rank = start_link+1
    writer = csv.writer(output)
    writer.writerow(["School Name", "Niche Rank", "Number of Students", "Number of Seniors", "Proportion interested in UT", "Number of Seniors interested"])


    all_schools = [sc.strip() for sc in school_list]
    for school in all_schools:
        try:
            headers = {"User-Agent": agents.readline().strip()}
        except:
            agents.close()
            agents = open("UserAgents/user_agents_firefox.txt", 'r')
            headers = {"User-Agent": agents.readline().strip()}
        print(school+", "+str(headers))

        #diagnostic
        if(rank % 15 == 0):
            print("Working on school #"+str(rank)+"!")

        school_page = requests.post(url=school, headers=headers)
        timesFail = 0 
        while (school_page.status_code != 200):
            # print("Status code: "+str(school_page.status_code)+", changing user header for link "+school)
            try:
                headers = {"User-Agent": agents.readline().strip()}
            except:
                agents.close()
                agents = open("UserAgents/user_agents_firefox.txt", 'r')
                headers = {"User-Agent": agents.readline().strip()}
            time.sleep(30+5*timesFail)
            timesFail +=1
            print("time sleep of " + str(30 + 5 * timesFail -5 ) + " failed")
            school_page = requests.post(url=school, headers = headers)
        
        school_soup = BeautifulSoup(school_page.content, 'html.parser')


        try:
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
                # print(school_title+": "+str(num_seniors_interested))
                writer.writerow([school_title, rank, num_students, num_seniors, UT_proportion, num_seniors_interested])
                rank += 1
        except:
            print("Failed link "+school)
            failed_writer.write(school)
agents.close()
failed_writer.close()
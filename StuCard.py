import getpass
import re

import requests
from bs4 import BeautifulSoup

from coloring import *

class Contest:
    base_url = "https://www.stucard.ch"

    def __init__(self, name, url, contest_id, session):
        self.name = name
        self.url = url
        self.id = contest_id
        self.session = session

    def participate(self):
        url = "{}/?wettbewerb=1&participate={}".format(self.base_url, self.id)
        response = self.session.get(url)
        return response

    def has_participated(self):
        url = self.base_url + self.url
        response = self.session.get(url)
        return "wettTeilnahmeOk" in response.text

    def __str__(self):
        return "{}: url=\"{}\", id={}".format(self.name, self.base_url + self.url, self.id)


def login(email, password):
    print("Logging in with {}".format(email), end="")
    login_post = {"loginEmail": email,
                  "loginPassword": password}

    url = "https://www.stucard.ch/?loginMember=1&keepPage=1"
    s = requests.Session()
    r = s.post(url, data=login_post)
    if r.status_code != 200:
        return None
    print(colorize(" - {FG_GREEN}Success!{FG_DEFAULT}"))
    return s


def get_contests(session):
    out = []
    response = session.get("https://www.stucard.ch/de/wettbewerb/")
    soup = BeautifulSoup(response.text, 'html.parser')
    block_container = soup.find("div", {"id": "blockContainer1"})
    blocks = block_container.find_all("div", {"class": re.compile("item.*")})
    for block in blocks:
        title = block.text.replace("\n", " ").replace("   CLICK & WIN  ", "")
        tease = block.find("div", {"class": "dealBlockTease"})
        url = tease['data-url']
        contest_id = tease['id'].replace("dealTease", "")
        out.append(Contest(title, url, contest_id, session))
    return out

def show_tag(file):
    with open(file, "r") as f:
        tag = f.read()
    tag = tag + "{BG_DEFAULT}{FG_DEFAULT}"
    tag = colorize(tag)
    print(tag)
    return len(tag.split("\n")[0])

if __name__ == "__main__":

    width = show_tag("tag.txt")
    with open("welcome.txt","r") as f:
        welcome_text = f.read()

    welcome_text = colorize(welcome_text)

    print()
    print(welcome_text)
    print()

    logged_in = False
    login_session = None

    while not logged_in:
        email = input(colorize("Enter your {FG_BLUE}Stu{FG_GREEN}Card{FG_DEFAULT} mail address: "))
        passwd = getpass.getpass(colorize("Enter your {FG_BLUE}Stu{FG_GREEN}Card{FG_DEFAULT} password: "))

        print()

        login_session = login(email, passwd)

        # Login successful
        if login_session != None:
            logged_in = True
        else:
            print(colorize("\n{FG_RED}I'm sorry, but I can't log in with these credentials. Please try again.{FG_DEFAULT}\n"))

    print("Fetching Contests",end="")
    contests = get_contests(login_session)
    print(colorize(" - {FG_GREEN}Done{FG_DEFAULT}"))

    print("Check for Contests you haven't participated in yet. (this might take a while)")
    count = 0
    for contest in contests:
        if not contest.has_participated():
            contest.participate()
            print("\tParticipating in {}".format(contest.name))
            count += 1
    print("\nNewly participating in {} new contests.".format(count))
    print("You are currently participating in a total of {} contests".format(len(contests)))
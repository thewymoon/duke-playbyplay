from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime, timedelta
from time import sleep
import sys
import csv

espn_url = "http://scores.espn.go.com"

def make_soup(url):
    return BeautifulSoup(urlopen(url), "lxml")

def get_games():
    soup = make_soup("http://espn.go.com/mens-college-basketball/team/schedule/_/id/150/duke-blue-devils")
    games = soup.find_all("li", {"class": "score"})
    links = [game.find("a") for game in games]
    links2 = [link.get("href") for link in links]
    
    play_by_play = []
    for game in links2:
       game_soup = make_soup(espn_url + game)
       ul = game_soup.find("ul", {"class":"links"})
       a = ul.find_all("a")
       for i in a:
           if "playbyplay" in i.get("href"):
               play_by_play.append(i.get("href"))

    return play_by_play


def get_play_by_play(pbp_path):
    "Returns the play-by-play data for a given game id."
    soup = make_soup(pbp_path)
    table = soup.find("table", "mod-data mod-pbp")

    if table is None:
        return None

    rows = [row.find_all("td") for row in table.find_all("tr",
        lambda x: x in ("odd", "even"))]
 
    data = []
    for row in rows:
        values = []
        for value in row:
            if value.string is None:
                values.append(u"")
            else:
                values.append(value.string.replace(u"\xa0", u""))
        # handle timeouts being colspan=3
        # repeat the timeout or note in the other columns
        if len(values) != 4:
            values = [values[0], values[1], values[1], values[1]]
        data.append(values)
 
    return data
 
if __name__ == '__main__':
        games = get_games()
        for game in games:
            game_id = game.lower().split("gameid=")[1]
 
            # I didn't feel like dealing with unicode characters
            try:
                print "Writing data for game: {0}".format(game_id)
                with open("duke-data/" + game_id + ".psv", "w") as f:
                    writer = csv.writer(f, delimiter="|")
                    writer.writerow(["time", "away", "score", "home"])
                    if get_play_by_play(game) is None:
                        pass
                    else:
                        writer.writerows(get_play_by_play(game))
            except UnicodeEncodeError:
                print "Unable to write data for game: {0}".format(game_id)
                print "Moving on ..."
                continue
 
            sleep(2) # be nice    



    



    
    

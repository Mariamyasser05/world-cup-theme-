standings = {
    "ARG" : {
        "P" :0 , "W":0 , "L":0 , "D":0 , "GF":0 , "GA":0 ,"GD":0 , "PTS":0
    },
    "MEX"  : {
        "P" :0 , "W":0 , "L":0 , "D":0 , "GF":0 , "GA":0 ,"GD":0 , "PTS":0
    },
    "POL"  : {
        "P" :0 , "W":0 , "L":0 , "D":0 , "GF":0 , "GA":0 ,"GD":0 , "PTS":0
    },
    "KSA" : {
        "P" :0 , "W":0 , "L":0 , "D":0 , "GF":0 , "GA":0 ,"GD":0 , "PTS":0
    } }
matches = [
    ("ARG", "MEX"),
    ("ARG" , "POL"),
    ("ARG","KSA"),
    ("MEX","POL"),
    ("MEX", "KSA"),
    ("POL", "KSA")
]



def process_match (standings,team1,team2,goals1,goals2):
    standings[team1]["P"]+=1
    standings[team2]["P"]+=1

    standings[team1]["GF"]+=goals1
    standings[team1]["GA"]+=goals2
    standings[team2]['GF']+=goals2
    standings[team2]["GA"]+=goals1

    standings[team1]["GD"]= (standings[team1]["GF"] - standings[team1]["GA"])
    standings[team2]["GD"]= (standings[team2]["GF"] - standings[team2]["GA"])

    if goals1 > goals2 :
        standings[team1]["W"]+=1
        standings[team2]["L"]+=1
        standings[team1]["PTS"]+=3
    elif goals2 > goals1 :
        standings[team2]["W"]+=1
        standings[team1]["L"]+=1
        standings[team2]["PTS"]+=3
    else :
        standings[team1]["D"]+=1
        standings[team2]["D"]+=1
        standings[team1]["PTS"]+=1
        standings[team2]["PTS"]+=1

def print_score (standings) :
    sortedTeams=sorted(standings.items(),
                       key=lambda item :(
                           item[1]["PTS"],
                           item[1]["GD"],
                           item[1]["GF"]
                       ), reverse=True)
    print()
    print(f"{'Team':<5} {'P':>2} {'W' :>2} {'L' :>2} {'D' :>2} {'GD' :>3} {'GF' :>3} {'GA' :>3} {'PTS' :>4}")

    for team,stats in sortedTeams :
        gd=stats['GD']
        if gd > 0 :
            gd= f"+{gd}"
        else :
            gd=str(gd)
        print(f"{team :<5} {stats['P']:>2} {stats['W']:>2} {stats['L']:>2} {stats['D'] :>2} {gd :>3} {stats['GF']:>3} {stats['GA']:>3} {stats['PTS']:>4}")


for team1 , team2 in matches :
    while True :
        try :
            score=input(f"enter score for {team1} vs {team2} (fromat 2-0) : ")
            goals1,goals2=score.split("-")
            goals1=int(goals1)
            goals2=int(goals2)
            break
        except :
            print("invalid format , please enter the score like this 2-0")
       
    process_match(standings,team1,team2,goals1,goals2)
print_score(standings)
import random
import os 
from groq import Groq
class player :
    def __init__(self,name,position,base_attack,base_defense) :
        self.name=name
        self.position=position
        self.base_defense=base_defense
        self.base_attack=base_attack
        self.stamina=100.0
        self.yellow_card=0
        self.red_card=False

    #everytime it is called wich is every minute (in run_minute_tick ) it minus the rate
    def deplete_stamina (self,rate) :
        self.stamina=max(10.0,self.stamina - rate)


    #change the base_defence and attack of the player according to the stamina
    def get_effective_defense (self) :
        return self.base_defense *(self.stamina/100)
    
    def get_effective_attack(self) :
        return self.base_attack *(self.stamina/100)    

    #called when the player takes a yellow card (2 yellow card result in a red one)
    def receive_card (self) :
        self.yellow_card +=1
        if self.yellow_card >=2 :
            self.red_card=True
    

    

class team :
    def __init__(self,name , roster , active_lineup , bench , substitutions_remaining ) :
        self.name=name
        self.roster=roster
        self.active_lineup=active_lineup
        self.bench=bench
        self.substitutions_remaining=substitutions_remaining
        self.formation = "BALANCED"


    #to calculate how good they can attack the average of the effective attack of the attackers  
    def get_aggregate_attack(self) :
        total =0
        attackers=[]

        # in balanced the attackers are the forward and midfielder
        # 4-4-2 then the 2 forward and the 4 mid to have 6 attackers 
        if self.formation == "BALANCED" :
            for player in self.active_lineup :
                if player.position in ["FORWARD" ,"MIDFIELDER"] :
                    attackers.append(player)

        #attacking 3-4-3 7 players must attack but the position are balanced at the begining of the match 4-4-2 so 
        #we will add one from the defenders to have 7 attackers 
        elif self.formation == "ATTACKING" :
            defender_added=0
            for player in self.active_lineup :
                if player.position in ["FORWARD" ,"MIDFIELDER"] :
                    attackers.append(player)
                elif player.position == "DEFENDER" and defender_added <1 :
                    attackers.append(player)
                    defender_added+=1
        
        #defencive 5 attackers so we put the 2 forward and 3 mid 
        elif self.formation == "DEFENSIVE" :
            midfield_used =0
            for player in self.active_lineup :
                if player.position == "FORWARD" :
                    attackers.append(player)
                elif player.position == "MIDFIELDER" and midfield_used<3 :
                    attackers.append(player)
                    midfield_used+=1


        if len(attackers) ==0 :
            return 0
        for player in attackers :
            total+=player.get_effective_attack()
        return total/len(attackers)
                

    def get_aggregate_defense(self) :
        total =0
        defenders=[]
        #5 players 4 defenders and the goalkeeper
        if self.formation == "BALANCED" :
           for player in self.active_lineup :
              if player.position =="GOALKEEPER" or player.position=="DEFENDER" :
                  defenders.append(player)
        
        #6 players 4 defenders 1 goalkeeper and 1 mid
        elif self.formation == "DEFENSIVE" :
            midfield_added=0
            for player in self.active_lineup :
                if player.position in ["GOALKEEPER", "DEFENDER"]:
                    defenders.append(player)
                elif player.position == "MIDFIELDER" and midfield_added<1 :
                    defenders.append(player)
                    midfield_added+=1

        #4 players 1 goalkepper and 3 defenders
        elif self.formation =="ATTACKING" :
            defenders_used=0
            for player in self.active_lineup :
                if player.position == "GOALKEEPER" :
                    defenders.append(player)
                elif player.position =="DEFENDER" and defenders_used<3 :
                    defenders.append(player)
                    defenders_used+=1
            

        if len(defenders) == 0 :
            return 0 
        for player in defenders :
            total +=player.get_effective_defense()
        return total/ len(defenders)
    
    #change the attribute (formation)
    def change_formation(self, new_formation):
       if new_formation in ["DEFENSIVE", "BALANCED", "ATTACKING"]:
        self.formation = new_formation

                

    #substitute the 2 players 
    def execute_substitution(self,player_out,player_in) :
        if self.substitutions_remaining==0 :
            return
        if player_out not in self.active_lineup :
            return 
        if player_in not in self.bench :
            return 
        
        self.active_lineup.remove(player_out)
        self.active_lineup.append(player_in)
        self.bench.remove(player_in)
        self.bench.append(player_out)
    
        self.substitutions_remaining-=1
    
#return a string that describes the event 
class matchEvent :
    def __init__(self,event_id,event_type,minute,team,player,outcome_text) :
        self.event_id=event_id
        self.event_type=event_type
        self.minute=minute
        self.team=team
        self.player=player
        self.outcome_text=outcome_text
    
    def to_string(self) :
        return f"Event # {self.event_id} : {self.event_type} at minute {self.minute} for {self.team} by {self.player}  {self.outcome_text}"


class match :
    def __init__(self,home_team,away_team, home_score , away_score  ,timeline , phase) :
        self.home_team=home_team
        self.away_team=away_team
        self.home_score=home_score
        self.away_score=away_score
        self.current_minute=0
        self.timeline=timeline
        self.phase=phase
        self.home_ai = matchAi("openai/gpt-oss-120b",self.home_team,0.5,self,[])#for the ai match
        self.away_ai = matchAi("openai/gpt-oss-120b",self.away_team,0.5,self,[])

    def process_discipline(self,team) :
        if random.random() >= 0.008 : #only a card received in 2%
            return
        player=random.choice(team.active_lineup) # choosing a random player 
        if random.random() < 0.8 : #80 % will be a yellow card
            player.receive_card()
            #checking if it's the 3rd yellow card (red card)
            if player.red_card:
                team.active_lineup.remove(player)
                event = matchEvent(
                    len(self.timeline)+1,
                    "RED CARD",
                    self.current_minute,
                    team.name,
                    player.name,
                    "Second Yellow"
                )
                self.timeline.append(event) # add the red card event in the history 

            event=matchEvent(len(self.timeline) +1  ,"YELLOW CARD" , self.current_minute,team.name,player.name, "booked")
            self.timeline.append(event) # add the yellow card .. 
        #2%  will be red card 
        else :
            player.red_card=True
            team.active_lineup.remove(player)
            event=matchEvent(len(self.timeline) +1 ,"RED CARD" , self.current_minute,team.name,player.name, "straight red")
            self.timeline.append(event)

     # minute counter 
    def run_minute_tick(self) :
        self.current_minute+=1

        base_decay = 0.5
        home_decay = base_decay * (
            1 + (self.home_ai.risk_tolerance - 0.5) * 0.4
        )
        away_decay = base_decay * (
            1 + (self.away_ai.risk_tolerance - 0.5) * 0.4
        )
        for player in self.home_team.active_lineup:
            player.deplete_stamina(home_decay)
        for player in self.away_team.active_lineup:
            player.deplete_stamina(away_decay)


        #calling for a yellow card every minute (probability of 20% to be a foul  )
        self.process_discipline(self.home_team)
        self.process_discipline(self.away_team)

        #calling for a goal every minute (probabilty 10%)
        self.process_goal_attempt(self.home_team,self.away_team)
        self.process_goal_attempt(self.away_team,self.home_team)

        #every 15 minute the ai get to make a decision 
        if self.current_minute %15 ==0 :
            state = self.home_ai.observe_state(self)
            action = self.home_ai.decide_action(state)
            self.home_ai.apply_decision(action)

            state = self.away_ai.observe_state(self)
            action = self.away_ai.decide_action(state)
            self.away_ai.apply_decision(action)
    

    def process_goal_attempt(self,attacking_team,defending_team) :
        # 10% 
        if random.random() >=0.10 : 
            return
        
        attack=attacking_team.get_aggregate_attack()
        defense=defending_team.get_aggregate_defense()

        #adding the risk tolerance 
        if attacking_team == self.home_team:
            risk = self.home_ai.risk_tolerance
        else:
            risk = self.away_ai.risk_tolerance

        upper_attack = 1.25 + (risk - 0.5) * 0.4
        attack_value = attack * random.uniform(0.75, upper_attack)        
        defense_value= defense *1.3 * random.uniform(0.80, 1.20)
         #score a goal when the attack_value > defence
        if attack_value > defense_value :
            if attacking_team == self.home_team :
                self.home_score+=1
            else :
                self.away_score+=1
            
            scorer="unknown"
            for player in attacking_team.active_lineup :
                if player.position == "FORWARD" :
                    scorer=player.name
                    break

            goal = matchEvent(len(self.timeline)+1,"GOAL",self.current_minute,attacking_team.name,scorer,"goal scored")
            self.timeline.append(goal)
    

    def play_match(self) :
        # the whole match 90 minutes
        for i in range(90) :
            self.run_minute_tick()
        self.phase="FINISHED"
        # print the final score
        print()
        print("FINAL SCORE")
        print(f"{self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}")

        if self.home_score > self.away_score:
          print(self.home_team.name, "wins!")

        elif self.away_score > self.home_score:
          print(self.away_team.name, "wins!")
        #if it"s a draw then penalties
        else:
          self.phase= "PENALTIES"
          self.penalty_shootout()
          return
        
    def penalty_shootout(self) :
        print("PENALTIES")
        home_penalties=0
        away_penalties=0
        #5 penalties for each team
        for i in range(5) :
            # 75% in 
            if random.random() <0.75 :
                home_penalties+=1
                print(self.home_team.name,"scores")
            else :
                print(self.home_team.name,"misses")
            if random.random() <0.75 :
                away_penalties+=1
                print(self.away_team.name,"scores")
            else : 
                print(self.away_team.name,"misses") 
        print()
        print("penalties result :")
        print(self.home_team.name , home_penalties)   
        print(self.away_team.name , away_penalties) 
        if home_penalties > away_penalties :
            print(self.home_team.name , "win on penalties")
        elif away_penalties > home_penalties :
            print(self.away_team.name , "win on penalties")
        else :
            #if draw again then 1 penalty 
            while home_penalties == away_penalties :
                if random.random() <0.75 :
                    home_penalties+=1
                if random.random() <0.75 :
                    away_penalties+=1
            if home_penalties > away_penalties :
                print(self.home_team.name , "win on penalties")
            else : 
                print(self.away_team.name , "win on penalties") 

        self.phase="FINISHED"
        


class matchAi :
    def __init__(self,model,controlled_team,risk_tolerance,match,decision_log) :
        self.model=model
        self.controlled_team=controlled_team
        self.risk_tolerance=risk_tolerance
        self.match=match
        self.decision_log=decision_log
        self.client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)
    
    #observe the state to make the decision 
    def observe_state(self,match) :
        state={
            "minute" : match.current_minute,
            "phase" : match.phase,
            "home_score" : match.home_score,
            "away_score" : match.away_score,
            "stamina" : []
        }
        
        for player in self.controlled_team.active_lineup :
            state["stamina"].append(player.stamina)
        
        return state
    
    #return the action 
    def decide_action(self, state): 
    
        return self.get_ai_actions(state)
    
    def apply_decision(self, actions):
        if  not actions  :
            return
        for action in actions :    
            if action == "SUBSTITUTE":
                player_out=min(self.controlled_team.active_lineup,key= lambda player : player.stamina)
                candidates=[]
                for player in self.controlled_team.bench :
                    if player.position == player_out.position :
                        candidates.append(player)      
                if len(candidates) >0 : 
                    player_in=max(candidates, key = lambda player : player.base_attack + player.base_defense) 
                    self.controlled_team.execute_substitution(player_out,player_in) 
                    self.decision_log.append(f"Substituted {player_out.name} with {player_in.name}")
            
            elif action == "CHANGE_TO_ATTACKING":
            
                self.controlled_team.change_formation("ATTACKING")
                self.decision_log.append("Changed formation to ATTACKING")
            
            elif action == "CHANGE_TO_DEFENSIVE":
            
                self.controlled_team.change_formation("DEFENSIVE")
                self.decision_log.append("Changed formation to DEFENSIVE")
            
            elif action == "PUSH_ATTACK":
            
                self.risk_tolerance = min(1, self.risk_tolerance + 0.2)
                self.decision_log.append("Increased risk (Push Attack)")
            
            elif action == "HOLD":
            
                self.risk_tolerance = max(0, self.risk_tolerance - 0.2)
                self.decision_log.append("Reduced risk (Hold)")


    def get_ai_actions(self,state) : # i used the ai model openai/gpt-oss-120b 
        #the prompt gived to the model
        prompt = f""" 
        You are the AI manager of {self.controlled_team.name}.
        Current minute: {state["minute"]}
        
        Score:
        Home: {state["home_score"]}
        Away: {state["away_score"]}
        
        Formation:
        {self.controlled_team.formation}
        
        Risk tolerance:
        {self.risk_tolerance}
        
        Lowest stamina:
        {min(state["stamina"])}
        
        Available actions:

        SUBSTITUTE
        CHANGE_TO_ATTACKING
        CHANGE_TO_DEFENSIVE
        PUSH_ATTACK
        HOLD
        
        Return ONLY action names separated by commas.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role":"user",#to act as the user to take the decisions
                    "content": prompt
                }
            ],
            temperature=0.4 # to not be so random
        )
        answer = response.choices[0].message.content.upper()#make it upper case 
        actions=answer.split(",")
        actions = []
        
        for a in answer.split(","):
            a = a.strip()# remove the spaces 
        #only append the actions 
            if a in [
                "SUBSTITUTE",
                "CHANGE_TO_ATTACKING",
                "CHANGE_TO_DEFENSIVE",
                "PUSH_ATTACK",
                "HOLD"
            ]:
                actions.append(a)
        
        return actions

            



# TEST
# Argentina
messi = player("Messi", "FORWARD", 95, 40)
alvarez = player("Alvarez", "FORWARD", 90, 45)

enzo = player("Enzo", "MIDFIELDER", 82, 75)
mac = player("MacAllister", "MIDFIELDER", 80, 72)
depaul = player("DePaul", "MIDFIELDER", 79, 74)
palacios = player("Palacios", "MIDFIELDER", 76, 70)

romero = player("Romero", "DEFENDER", 40, 92)
otamendi = player("Otamendi", "DEFENDER", 35, 90)
molina = player("Molina", "DEFENDER", 40, 82)
tagliafico = player("Tagliafico", "DEFENDER", 35, 84)

martinez = player("Martinez", "GOALKEEPER", 20, 95)

lineup1 = [
    messi,
    alvarez,
    enzo,
    mac,
    depaul,
    palacios,
    romero,
    otamendi,
    molina,
    tagliafico,
    martinez
]

# Bench

dybala = player("Dybala", "FORWARD", 88, 40)
lautaro = player("Lautaro Martinez", "FORWARD", 91, 42)

paredes = player("Paredes", "MIDFIELDER", 76, 78)
lo_celso = player("Lo Celso", "MIDFIELDER", 81, 73)
garnacho = player("Garnacho", "MIDFIELDER", 84, 55)

lisandro = player("Lisandro Martinez", "DEFENDER", 45, 91)
foyth = player("Foyth", "DEFENDER", 42, 84)
acuna = player("Acuna", "DEFENDER", 43, 83)

rulli = player("Rulli", "GOALKEEPER", 18, 88)

bench1 = [
    dybala,
    lautaro,
    paredes,
    lo_celso,
    garnacho,
    lisandro,
    foyth,
    acuna,
    rulli
]

roster1 = lineup1 + bench1

argentina = team(
    "Argentina",
    roster1,
    lineup1,
    bench1,
    5
)

# France

mbappe = player("Mbappe", "FORWARD", 95, 35)
giroud = player("Giroud", "FORWARD", 88, 45)

griezmann = player("Griezmann", "MIDFIELDER", 84, 72)
camavinga = player("Camavinga", "MIDFIELDER", 82, 74)
tchouameni = player("Tchouameni", "MIDFIELDER", 80, 78)
rabiot = player("Rabiot", "MIDFIELDER", 78, 73)

upa = player("Upamecano", "DEFENDER", 35, 90)
hernandez = player("Hernandez", "DEFENDER", 38, 88)
kounde = player("Kounde", "DEFENDER", 36, 86)
saliba = player("Saliba", "DEFENDER", 34, 90)

maignan = player("Maignan", "GOALKEEPER", 20, 94)

lineup2 = [
    mbappe,
    giroud,
    griezmann,
    camavinga,
    tchouameni,
    rabiot,
    upa,
    hernandez,
    kounde,
    saliba,
    maignan
]

# Bench

dembele = player("Dembele", "FORWARD", 90, 35)
thuram = player("Marcus Thuram", "FORWARD", 89, 40)

kante = player("Kante", "MIDFIELDER", 74, 90)
zaire = player("Zaire-Emery", "MIDFIELDER", 82, 77)
olise = player("Olise", "MIDFIELDER", 86, 60)

konate = player("Konate", "DEFENDER", 40, 91)
theo = player("Theo Hernandez", "DEFENDER", 46, 86)
clauss = player("Clauss", "DEFENDER", 44, 82)

samba = player("Brice Samba", "GOALKEEPER", 18, 90)

bench2 = [
    dembele,
    thuram,
    kante,
    zaire,
    olise,
    konate,
    theo,
    clauss,
    samba
]


roster2 = lineup2 + bench2

france = team(
    "France",
    roster2,
    lineup2,
    bench2,
    5
)

game = match(
    argentina,
    france,
    0,
    0,
    [],
    "REGULATION"
)

game.play_match()

print("\nTimeline\n")

for event in game.timeline:
    print(event.to_string())

print("\nAI Decisions\n")

for decision in game.home_ai.decision_log:
    print("Argentina:", decision)

for decision in game.away_ai.decision_log:
    print("France:", decision)

print("\nRemaining Stamina\n")

for p in argentina.active_lineup:
    print(p.name, round(p.stamina,1))

for p in france.active_lineup:
    print(p.name, round(p.stamina,1))





from flask import Flask, render_template, request, jsonify, abort
import Units
import Combat_Ser as Combat
import time
import random


app = Flask(__name__)


"""
REF: RoomManagement, RMG, Room, Manager

room system allowing for multipule rooms on one serverport
"""

class RoomManager():
    def __init__(self):
        self.rooms = []
    
    def CreateRoom(self) -> None:
        self.rooms.append(Room(len(self.rooms)+1))
    
class Room(RoomManager):
    def __init__(self, id:int):
        self.id = id
        self.state = {
        'Player1_mana': int(5),
        'Player2_mana': int(5),
        'Player1_HP': int(20),
        'Player2_HP': int(20),
        'Won': bool(False),
        'last_update': float(time.time()),
        'time_index': list([]),
        'max_time': int(1200),
        'total_time': float(0),
        'Player1_mana_timer': float(0),
        'Player2_mana_timer': float(0),
        'Player1_Units': list([]),
        'Player2_Units': list([]),
        'Player1_SpawnPos': list([370, 630]), # Basic player spawn point
        'Player2_SpawnPos': list([370, 70]), # enchanter spawn point
        'Pumps': list([]),
        'GameSeed': int(123456789)}
        self.player1_ID = random.randint(0, 9999999)
        self.player2_ID = random.randint(0, 9999999)
        self.givenPlayer1 = False
        self.givenPlayer2 = False
        if self.player1_ID == self.player2_ID:
            self.player1_ID -= 1
        self.state['player1_ID'] = self.player1_ID
        self.state['player2_ID'] = self.player2_ID
        

    def updateGame(self):
        self.state = Combat.BatLogic(Units, self.state)
        self.state['time_index'].append(time.time())
        self.state['last_update'] = time.time()

    def ReturnPlayerIDs(self) -> int:
        if self.givenPlayer2:
            return None
        elif self.givenPlayer1:
            self.givenPlayer2 = True
            return self.player2_ID
        else:
            self.givenPlayer1 = True
            return self.player1_ID
            

    def GetState(self):
        sentState = self.state.copy()
        sentState['Player1_Units'] = [u.Package() for u in self.state['Player1_Units']]
        sentState['Player2_Units'] = [u.Package() for u in self.state['Player2_Units']]
        sentState['Pumps'] = [u.Package() for u in self.state['Pumps']]
        return sentState
        
    def AddUnit(self, playerID:int, UnitID:int):
        if UnitID == 0:
            unit = Units.Footman(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        elif UnitID == 1:
            unit = Units.Horse(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        elif UnitID == 2:
            unit = Units.Soldier(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        elif UnitID == 3:
            unit = Units.Summoner(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        elif UnitID == 4:
            unit = Units.Runner(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        elif UnitID == 5:
            unit = Units.Tank(self.state['Player1_SpawnPos'] if self.player1_ID == playerID else self.state['Player2_SpawnPos'])
        else:
            unit = None
        if playerID == self.player1_ID:
            self.state['Player1_Units'].append(unit)
        elif playerID == self.player2_ID:
            self.state['Player2_Units'].append(unit)

    def RetargetUnit(self, playerID:int, UnitIndex:int, target:list=[0,0]):
        if playerID == self.player1_ID:
            self.state['Player1_Units'][UnitIndex].target = target
        elif playerID == self.player2_ID:
            # We need to flip the player 2 target locations in relation to the battlefield (reminder that it is 741x700)
            target = [abs(target[0] - 741), abs(target[1] - 700)]
            self.state['Player2_Units'][UnitIndex].target = target

RMG = RoomManager()



"""
REF: SERVER, SER, MAIN

This is the server section, all the flask functions and routes are here.


"""

queue = []

def Matchmake():
    global queue
    if not len(queue) < 2:

        temp_queue = queue.copy()
        saved_u = []
        i = 0
        for u in queue:
            if u is None:
                saved_u.append(i)
            i += 1
        i = 0
        if len(saved_u) % 2 != 0:
            return temp_queue
        else:
            for u in saved_u:
                if temp_queue[u] is None:
                    RMG.CreateRoom()
                    roomID = RMG.rooms[-1].id
                    temp_queue[saved_u[i]] = roomID
                    temp_queue[saved_u[i+1]] = roomID
        queue = temp_queue



    


@app.route('/queue-up', methods=['GET'])
def Join_Queue():
    global queue
    queue.append(None)
    return jsonify({
        "Success": True,
        "Position":len(queue) - 1,
        })

@app.route('/check-queue', methods=['POST'])
def Check_Queue():
    global queue
    data = request.json
    queuePos = data['Position']
    Matchmake()
    # print(queue)
    return jsonify({
        "Success": True,
        "RoomID":queue[queuePos],
    })

@app.route('/join-room', methods=['POST'])
def Join_Room():
    data = request.json
    RoomID = data['RoomID']
    if RoomID:
        for r in RMG.rooms:
            if r.id == RoomID:
                ID = r.ReturnPlayerIDs()
                if ID:
                    return jsonify({
                        "Success": True,
                        "PlayerID": ID,
                    })
                else:
                    return jsonify({
                        "Success": False,
                        "PlayerID": None,
                    })
    else:
        return jsonify({
                        "Success": False,
                        "PlayerID": None,
                    })
@app.route('/summon', methods=['POST'])
def SummonTroops() -> None:
    data = request.json
    RoomID = data['RoomID']
    playerID = data['PlayerID']
    index = data['SummonIndex']
    for r in RMG.rooms:
        if r.id == RoomID:
            r.AddUnit(playerID, index)

@app.route('/target', methods=['POST'])
def Retarget() -> None:
    data = request.json
    RoomID = data['RoomID']
    playerID = data['PlayerID']
    index = data['UnitsIndex']
    target = data['Target']
    for r in RMG.rooms:
        if r.id == RoomID:
            r.RetargetUnit(playerID, index, target)


@app.route('/get-state', methods=['POST'])
def State():
    data = request.json
    RoomID = data['RoomID']
    for r in RMG.rooms:
        if r.id == RoomID:
            r.updateGame()
            return jsonify({
                'Success':True,
                'State': r.GetState()
            })
    return jsonify({
        'Success':False,
        'State': None,
    })

app.run(host="0.0.0.0", port="54321", threaded=True)
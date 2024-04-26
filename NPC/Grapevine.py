from random import choice, randint, gauss
from collections import deque
from typing import Dict, List, Tuple
from GPTEndpoint import GPTEndpoint
from NPC.NPC import NPC
import time, re

from NPC.Prompts import Prompts


def sort_tuple(x: object, y: object) -> Tuple[object, object]:
    return tuple(sorted([x, y]))

def get_first_number(s: str) -> int:
    # Regular expression to find the first sequence of digits in the string
    match = re.search(r'\d+', s)
    if match:
        # Convert the matched string to an integer
        return int(match.group())
    else:
        # Return None if no digits were found
        return None

class Grapevine:
    '''
        Assume NPCs X and Y present in the Grapevine (a weighted undirected graph).
        The Grapevine manages the following:
            (1) The strength of the communication or "distance" between X and Y  (represented by edge Dxy)
                (a) From 0 to 10, where 0 represents NO CONNECTION and 10 represents CONSTANT COMMUNICATION
            (2) The emotion X FEELS towards Y (represented by edge Exy)
                (a) From -10 to 10, where -10 represents DEEP HATE and 10 represents SOUL MATE
            (3) The PLAYER interactions with NPCs
                (a) The PLAYER is a node in the network
                (b) Every conversation the NPC has with the PLAYER updates
                    (i) Dxy (by rate of convo)
                    (ii) Exy (by sentiment analysis)
                (c) TODO: Every WITNESS event (robbery, murder, heroics) is processed in a buffer
                    (i) Every in-game day, information is diffused reigonally from the buffer
            (4) Information diffusion from one NPC to another
                (a) Every in-game day, an Info Diffusion process is run, consisting of the following:
                    (i) If Dxy > N(5,2), where N is a normal R.V, then trigger a conversation
                    (ii) A natural conversation is simulated via LLM between X and Y
                    (ii) The length of the conversation will be determined by Exy
                    (iv) X and Y will both reflect on this conversation
                    (v) Updates Dxy by keeping track of rate of conversation
                    (vi) Updates Exy by analyzing sentiment of conversation
            (5) TODO: Dealing with the loss or gain of NPCs
                (a) Losses of NPCs in the network leave people with high Dxy's to wonder what happened
                (b) An addition of a new NPC Z automatically triggers convo's with others connected to Z
            (6) TODO: Miscellanious Functions
                (a) get_subset_by_strength(V, thresh)
                    (i) V is a specific NPC or PLAYER, and thresh is a number in [1, 10]
                    (ii) Creates a new Grapevine localized to V and every node N connected to V with Dvn > thresh
                (b) get_subset_by_emotion(V, thresh)
                    (i) Similar to get_subset_by_emotion but now Evn > thresh
    '''

    class Edge:
        '''
            Edge class representing a directed edge to another NPC / player with edge weights Dxy and Exy

            Has functions to help update Dxy and Exy
        '''
        BUFFER_SIZE = 4

        def __init__(self, x: str, y: str, D: float, E: float) -> None:
            self.x = x
            self.y = y
            self.D = D
            self.E = E

            # Keep last 4 weights as buffer
            self.D_buffer = deque(maxlen=Grapevine.Edge.BUFFER_SIZE)
            self.E_buffer = deque(maxlen=Grapevine.Edge.BUFFER_SIZE)
        
        def update_distance(self, newD: float) -> None:
            self.E_buffer.append(newD)
            self.E = sum(self.D_buffer) / len(self.D_buffer)

        def update_emotion(self, newE: float) -> None:
            self.E_buffer.append(newE)
            self.E = sum(self.E_buffer) / len(self.E_buffer)
        
        def get_weights(self) -> Tuple[float, float]:
            return (self.D, self.E)
        
        def __eq__(self, other) -> bool:
            if isinstance(self, Grapevine.Edge):
                return (self.x == other.x) and (self.y == other.y)
    
        def __hash__(self) -> int:
            return hash(self.x, self.y)
        
        def __repr__(self) -> str:
            return f"{self.x} -> {self.y} | D,E = {self.D},{self.E}"



    def __init__(self, player: str, NPC_nodes: List[NPC], edges: List[Tuple[str, str, float, float]], LLM: GPTEndpoint) -> None:
        '''
            Initializes the Grapevine with:
                - player: The name of the PLAYER
                - NPC_nodes: A list of NPCs 
                - edges: A list of edges, where each edge is:
                    - (x, y, Dxy, Exy)
        '''
        # TODO: Add assertions to the edges' Dxy and Exy
        self.player = player
        self.name_to_NPC = {npc.name:npc for npc in NPC_nodes}
        self.LLM = LLM
        
        # Init Grapevine graph
        self.grapevine: Dict[str, Dict[str, Grapevine.Edge]] = {npc.name:{} for npc in NPC_nodes}
        self.grapevine[player] = {}
        for edge in edges:
            x, y, Dxy, Exy = edge
            assert x in self.grapevine and y in self.grapevine and 0 <= Dxy <= 10 and -10 <= Exy <= 10
            self.grapevine[x][y] = Grapevine.Edge(x, y, Dxy, Exy)
    
    def get_NPC(self, npc_name:str=None) -> NPC:
        if npc_name is None:
            return choice(list(self.name_to_NPC.values()))
        return self.name_to_NPC[npc_name] if npc_name in self.name_to_NPC else None

    def tick_info_diffusion(self) -> None:
        '''
        Process for all pairs of NPCs
            (i) If Dxy > N(5,2), where N is a normal R.V, then trigger a conversation
            (ii) A natural conversation is simulated via LLM between X and Y
            (ii) The length of the conversation will be determined by Exy
            (iv) X and Y will both reflect on this conversation
            (v) Updates Dxy by keeping track of rate of conversation
            (vi) Updates Exy by analyzing sentiment of conversation
        '''
        processed_conversations = set()
        # TODO: Process NPCs in a random order
        for x in self.grapevine:
            for y in self.grapevine[x]:
                Dxy, Exy = self.grapevine[x][y].get_weights()

                # Skip if player
                if x == self.player or y == self.player:
                    continue

                # Check if already processed
                if sort_tuple(x, y) in processed_conversations:
                    continue
                processed_conversations.add(sort_tuple(x, y))

                # Check if NPC 1 and 2 have a convo
                if not self.does_convo_occur(Dxy):
                    continue

                # Simulate dialogue between NPC 1 and NPC 2
                NPC_1, NPC_2 = self.name_to_NPC[x], self.name_to_NPC[y]
                dialogue_history = ["Hello!"]
                for i in range(self.calc_convo_length(Exy)):
                    dialogue_history.append(NPC_1.dialogue(f'{x} is conversing with {y}', dialogue_history, y, time.time()))
                    dialogue_history.append(NPC_2.dialogue(f'{y} is conversing with {x}', dialogue_history, x, time.time()))
                NPC_1.reflect(time.time())
                NPC_2.reflect(time.time())

                # Update weights
                self.update_NPC_emotion(self.grapevine[x][y])
                self.update_NPC_emotion(self.grapevine[y][x])
    

    def update_NPC_emotion(self, edge:Edge) -> None:
        '''
            Updates Exy by analyzing how X feels about Y (X and Y are both NPCs)
        '''
        # print(self.grapevine)
        perciever = self.name_to_NPC[edge.x]
        queried_memories = perciever.memory.query(f'What are your thoughts on {edge.y}', 3, time.time())
        emotion_level = get_first_number(perciever.LLM.complete(message_stream=[{'role':'user', 'content': perciever.prompt.emotion_level(edge.y, queried_memories)}]))
        if emotion_level is not None:
            edge.update_emotion(emotion_level)

    def update_player_emotion(self, reciever:NPC, dialogue_history:List[str]) -> None:
        '''
            Updates Exy by analyzing how PLAYER feels about Y and vice versa
        '''
        # Update player -> reciever
        emotion_level = get_first_number(self.LLM.complete(message_stream=[{'role':'user', 'content': Prompts.player_emotion_level(self.player, reciever, dialogue_history)}]))
        if emotion_level is not None:
            self.grapevine[self.player][reciever.name].update_emotion(emotion_level)

        # Update reciever -> player
        self.update_NPC_emotion(self.grapevine[reciever.name][self.player])


    def calc_convo_length(self, E: float) -> int:
        '''
            TODO: Try different functions

            For now, we calculate convo_length naively by adding 10 to E
        '''
        res = int(E)
        assert res >= 0
        return res
    

    def does_convo_occur(self, D: float) -> bool:
        '''
            TODO: Try different functions

            For now, we calculate if convo occurs if D > N(5, 2)
        '''
        return D > gauss(5, 2) - 5




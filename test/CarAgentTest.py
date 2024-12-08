from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import json
import asyncio

class CarAgent(Agent):
    def __init__(self, jid, password, location):
        super().__init__(jid, password)
        self.location = location  # Current location of the car
        self.best_slot = None     # Best parking slot found
        self.parked_slot = None   # Slot where the car is parked
        
    def calculate_distance(self, location1, location2):
        return abs(location1[0] - location2[0]) + abs(location1[1] - location2[1])
    
    def get_best_slot(self, slots):
        best_slot = None
        #cost is funtion of distance and cost per hour
        function_cost = lambda x: x["cost_per_hour"] + self.calculate_distance(self.location, x["location"])
        best_slot = min(slots, key=function_cost)
        return best_slot
    
    
    
    class SearchAndWaitState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Sending parking search request to BroadcastAgent...")

            # Step 1: Send parking request to BroadcastAgent
            request_msg = Message(to="SPMSBroadcast@localhost")  # BroadcastAgent JID
            request_msg.set_metadata("performative", "inform")
            request_msg.body = json.dumps({
                "type": "parking_request", 
                "location": self.agent.location, 
                "jid": str(self.agent.jid)
            })
            await self.send(request_msg)
            print(f"[{self.agent.jid}] Parking search request sent. Waiting for responses...")

            # Step 2: Wait for parking responses
            responses = []
            timeout = 5  # Collect responses for 5 seconds

            while timeout > 0:
                msg = await self.receive(timeout=1)
                if msg:
                    content = json.loads(msg.body)
                    if content.get("type") == "parking_response":
                        responses.append(content)
                        print(f"[{self.agent.jid}] Received parking response: {content}")
                timeout -= 1

            # Step 3: Process the responses
            if responses:
                # Select the best parking slot based on cost
                self.agent.best_slot = self.agent.get_best_slot(responses)
                print(f"[{self.agent.jid}] Best parking slot selected: {self.agent.best_slot}")
                self.set_next_state("CONFIRM_PARKING")
            else:
                print(f"[{self.agent.jid}] No parking slots available. Retrying search...")
                self.set_next_state("SEARCH_AND_WAIT")  # Retry same state if no responses


            
    class ConfirmParkingState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Confirming parking slot...")
            slot_jid = self.agent.best_slot["slot_jid"]
            confirm_msg = Message(to=slot_jid)
            print(f"[{self.agent.jid}] Sending confirm message to {slot_jid}")
            confirm_msg.set_metadata("performative", "inform")
            confirm_msg.body = json.dumps({"type": "confirm_parking", "slot": self.agent.best_slot, "car": str(self.agent.jid)})
            await self.send(confirm_msg)
            
            #wait for response
            response = None
            timeout = 5
            while timeout > 0:
                msg = await self.receive(timeout=1)
                if msg:
                    content = json.loads(msg.body)
                    if content.get("type") == "confirm_response":
                        response = content
                        print(f"[{self.agent.jid}] Received confirm response: {content}")
                timeout -= 1
            if response:
                self.agent.parked_slot = response["slot"]
                print(f"[{self.agent.jid}] Parking confirmed.")
                self.set_next_state("PARKED")
            else:
                print(f"[{self.agent.jid}] Parking not confirmed.")
                self.set_next_state("SEARCH_AND_WAIT")

    class ParkedState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Parking done.")
            

    async def setup(self):
        print(f"[{self.jid}] CarAgent starting...")
        fsm = FSMBehaviour()

        # Add States
        fsm.add_state(name="SEARCH_AND_WAIT", state=self.SearchAndWaitState(), initial=True)
        fsm.add_state(name="CONFIRM_PARKING", state=self.ConfirmParkingState())
        fsm.add_state(name="PARKED", state=self.ParkedState())
        
        # Add Transitions
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="CONFIRM_PARKING")
        fsm.add_transition(source="CONFIRM_PARKING", dest="SEARCH_AND_WAIT")
        fsm.add_transition(source="CONFIRM_PARKING", dest="PARKED")
        fsm.add_transition(source="PARKED", dest="SEARCH_AND_WAIT")

        # Add self-referencing transition
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="SEARCH_AND_WAIT")

        self.add_behaviour(fsm)


async def main():
    car_agent_1 = CarAgent("car1@localhost", "car1", location=(5, 5))
    car_agent_2 = CarAgent("car2@localhost", "car2", location=(15, 15))
    car_agent_3 = CarAgent("car3@localhost", "car3", location=(25, 25))
    
    
    await car_agent_1.start()
    await car_agent_2.start()
    await car_agent_3.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")
    
    await car_agent_1.stop()
    await car_agent_2.stop()
    await car_agent_3.stop()
    
if __name__ == "__main__":
    asyncio.run(main())


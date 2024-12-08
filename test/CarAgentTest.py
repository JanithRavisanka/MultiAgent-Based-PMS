from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import json
import asyncio
import random
from math import sqrt

class CarAgent(Agent):
    def __init__(self, jid, password, shedule):
        super().__init__(jid, password)
        self.best_slot = None     # Best parking slot found
        self.parked_slot = None   # Slot where the car is parked
        self.target_location = shedule["target_location"]
        self.parking_duration = shedule["parking_duration"]
        self.location = self.random_location()
        
    def random_location(self):
        return (random.randint(0, 50), random.randint(0, 50))   
        
    def calculate_distance(self, location1, location2):
        return round(sqrt(abs(location1[0] - location2[0])**2 + abs(location1[1] - location2[1])**2))
    
    def get_best_slot(self, slots):
        best_slot = None
        #cost is funtion of distance and cost per hour
        function_cost = lambda x: x["cost_per_hour"] + self.calculate_distance(self.location, x["location"])
        best_slot = min(slots, key=function_cost)
        return best_slot

    def driving_time(self, location1, location2):
        return self.calculate_distance(location1, location2) * 2
    
    class DriveState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Driving to target location: {self.agent.target_location}")
            # Simulate driving by sleeping for 10 seconds
            await asyncio.sleep(self.agent.driving_time(self.agent.location, self.agent.target_location))
            print(f"[{self.agent.jid}] Arrived at target location.")
            self.location = self.agent.target_location
            self.set_next_state("SEARCH_AND_WAIT")
            
    class SearchAndWaitState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Sending parking search request to BroadcastAgent...")

            # Step 1: Send parking request to BroadcastAgent
            request_msg = Message(to="SPMSBroadcast@localhost")  # BroadcastAgent JID
            request_msg.set_metadata("performative", "inform")
            request_msg.body = json.dumps({
                "type": "parking_request", 
                # "location": self.agent.location, 
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
                self.agent.parked_slot = {"slot_jid":response["slot_jid"], "location":response["slot"]}
                print(f"[{self.agent.jid}] Parking confirmed.")
                self.set_next_state("PARKED")
            else:
                print(f"[{self.agent.jid}] Parking not confirmed.")
                self.set_next_state("SEARCH_AND_WAIT")

    class ParkedState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Car parked at {self.agent.parked_slot}.")
            # Simulate parking by sleeping for 10 seconds
            await asyncio.sleep(self.agent.parking_duration+self.agent.driving_time(self.agent.location, self.agent.parked_slot["location"]))
            print(f"[{self.agent.jid}] Car has been parked for {self.agent.parking_duration} seconds. Departing...")
            
            #send departure message
            departure_msg = Message(to=self.agent.parked_slot["slot_jid"])
            departure_msg.set_metadata("performative", "inform")
            departure_msg.body = json.dumps({"type": "confirm_departure", "car": str(self.agent.jid)})
            
            await self.send(departure_msg)
            
            self.set_next_state("DEPARTED")
            
    class DepartedState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Car has departed from parking slot.")
            self.agent.target_location = self.agent.random_location()
            self.set_next_state("DRIVE")
            
            
            

    async def setup(self):
        print(f"[{self.jid}] CarAgent starting...")
        fsm = FSMBehaviour()

        # Add States
        fsm.add_state(name="DRIVE", state=self.DriveState(), initial=True)
        fsm.add_state(name="SEARCH_AND_WAIT", state=self.SearchAndWaitState())
        fsm.add_state(name="CONFIRM_PARKING", state=self.ConfirmParkingState())
        fsm.add_state(name="PARKED", state=self.ParkedState())
        fsm.add_state(name="DEPARTED", state=self.DepartedState())
        
        # Add Transitions
        fsm.add_transition(source="DRIVE", dest="SEARCH_AND_WAIT")
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="CONFIRM_PARKING")
        fsm.add_transition(source="CONFIRM_PARKING", dest="SEARCH_AND_WAIT")
        fsm.add_transition(source="CONFIRM_PARKING", dest="PARKED")
        fsm.add_transition(source="PARKED", dest="DEPARTED")
        fsm.add_transition(source="DEPARTED", dest="DRIVE")

        # Add self-referencing transition
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="SEARCH_AND_WAIT")

        self.add_behaviour(fsm)


async def main():
    car_agent_1 = CarAgent("car1@localhost", "car1", shedule={"target_location": (5, 5), "parking_duration": 10})
    car_agent_2 = CarAgent("car2@localhost", "car2", shedule={"target_location": (15, 15), "parking_duration": 15})
    car_agent_3 = CarAgent("car3@localhost", "car3", shedule={"target_location": (25, 25), "parking_duration": 20})
    
    
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


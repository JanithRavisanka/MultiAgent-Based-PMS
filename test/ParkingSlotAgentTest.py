
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import json
import asyncio

class ParkingSlotAgent(Agent):
    def __init__(self, jid, password, location, cost_per_hour):
        super().__init__(jid, password)
        self.location = location
        self.cost_per_hour = cost_per_hour
        self.current_car = None  # To track the parked car

    # REGISTER State: Register with the BroadcastAgent
    class RegisterState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Registering with BroadcastAgent...")
            register_msg = Message(to="SPMSBroadcast@localhost")  # BroadcastAgent JID
            register_msg.set_metadata("performative", "inform")
            register_msg.body = json.dumps({"type": "register_slot", "location": self.agent.location})
            await self.send(register_msg)
            print(f"[{self.agent.jid}] Registered successfully.")
            self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")

    class WaitForRequestAndConfirmationState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Waiting for parking requests or confirmations...")
            msg = await self.receive(timeout=20)
            if msg:
                content = json.loads(msg.body)
                print(f"[{self.agent.jid}] Received message: {content}")
                if content.get("type") == "parking_request" and self.agent.current_car is None:
                    car_jid = content.get("jid")
                    response_msg = Message(to=car_jid)
                    response_msg.set_metadata("performative", "inform")
                    response_msg.body = json.dumps({
                        "type": "parking_response",
                        "location": self.agent.location,
                        "cost_per_hour": self.agent.cost_per_hour,
                        "slot_jid": str(self.agent.jid)
                    })
                    await self.send(response_msg)
                    print(f"[{self.agent.jid}] Sent parking details to {car_jid}.")
                    self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")
                elif content.get("type") == "confirm_parking" and self.agent.current_car is None:
                    self.agent.current_car = content.get("car")
                    print(f"[{self.agent.jid}] Parking confirmed for car: {self.agent.current_car}.")
                    response_msg = Message(to=self.agent.current_car)
                    response_msg.set_metadata("performative", "inform")
                    response_msg.body = json.dumps({
                        "type": "confirm_response",
                        "slot": self.agent.location,
                        "slot_jid": str(self.agent.jid)
                    })
                    await self.send(response_msg)
                    self.set_next_state("WAIT_FOR_DEPARTURE")
                elif content.get("type") == "parking_request" and self.agent.current_car is not None:
                    print(f"[{self.agent.jid}] Slot is occupied, rejecting new parking request.")
                    self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")
                else:
                    print(f"[{self.agent.jid}] Invalid message received.")
                    self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")
            else:
                print(f"[{self.agent.jid}] No messages received, staying in WAIT_FOR_REQUEST_AND_CONFIRMATION.")
                self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")


    # WAIT_FOR_DEPARTURE State: Wait for the car to depart
    class WaitForDepartureState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Waiting for car {self.agent.current_car} to depart...")
            msg = await self.receive(timeout=20)
            if msg:
                content = json.loads(msg.body)
                print(f"[{self.agent.jid}] Received message: {content}")
                if content.get("type") == "confirm_departure":
                    print(f"[{self.agent.jid}] Car {self.agent.current_car} has departed. Slot is now available.")
                    self.agent.current_car = None  # Free up the parking slot
                    self.set_next_state("WAIT_FOR_REQUEST_AND_CONFIRMATION")
                elif content.get("type") == "parking_request" and self.agent.current_car is not None:
                    print(f"[{self.agent.jid}] Slot is occupied, rejecting new parking request.")
                    self.set_next_state("WAIT_FOR_DEPARTURE")
                else:
                    print(f"[{self.agent.jid}] Invalid departure message received.")
                    self.set_next_state("WAIT_FOR_DEPARTURE")

            else:
                print(f"[{self.agent.jid}] No departure message received, slot still occupied.")
                self.set_next_state("WAIT_FOR_DEPARTURE")
    
        # HANDLE_UNMATCHED State: Catch-all for unmatched messages

    # Setup FSMBehaviour
    async def setup(self):
        print(f"[{self.jid}] ParkingSlotAgent starting at location {self.location}...")
        fsm = FSMBehaviour()
        fsm.add_state(name="REGISTER", state=self.RegisterState(), initial=True)
        fsm.add_state(name="WAIT_FOR_REQUEST_AND_CONFIRMATION", state=self.WaitForRequestAndConfirmationState())
        fsm.add_state(name="WAIT_FOR_DEPARTURE", state=self.WaitForDepartureState())
        
        # Register transitions
        fsm.add_transition(source="REGISTER", dest="WAIT_FOR_REQUEST_AND_CONFIRMATION")
        fsm.add_transition(source="WAIT_FOR_REQUEST_AND_CONFIRMATION", dest="WAIT_FOR_DEPARTURE")
        fsm.add_transition(source="WAIT_FOR_DEPARTURE", dest="WAIT_FOR_REQUEST_AND_CONFIRMATION")
        
        # Add self-referencing transitions to retry states
        fsm.add_transition(source="WAIT_FOR_REQUEST_AND_CONFIRMATION", dest="WAIT_FOR_REQUEST_AND_CONFIRMATION")
        fsm.add_transition(source="WAIT_FOR_DEPARTURE", dest="WAIT_FOR_DEPARTURE")

        self.add_behaviour(fsm)



# Main Function to Start ParkingSlotAgents
async def main():
    # Start two parking slots
    # slot1 = ParkingSlotAgent("parking1@localhost", "parking1", location=(23, 26), cost_per_hour=5)
    # slot2 = ParkingSlotAgent("parking2@localhost", "parking2", location=(21, 26), cost_per_hour=3)
    # slot3 = ParkingSlotAgent("parking3@localhost", "parking3", location=(25, 17), cost_per_hour=4)
    
    # Road layout represented as a grid (0 = road, 1 = wall)
    ROAD_MAP = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 2, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 2, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    
    # List to store the parking slot agents
    parking_agents = []
    
    

    # Iterate through the grid to find parking slots
    for i, row in enumerate(ROAD_MAP):
        for j, cell in enumerate(row):
            if cell == 2:  # Found a parking slot
                agent_id = len(parking_agents) + 1
                agent_name = f"parking{agent_id}"
                email = f"{agent_name}@localhost"
                location = (i, j)
                cost_per_hour = (agent_id % 3) + 3  # Example cost: rotating between 3, 4, 5
                parking_agents.append(
                    ParkingSlotAgent(f"{email}", f"{agent_name}", location=location, cost_per_hour=cost_per_hour)
                )

    # Print the generated parking slot agents
    for agent in parking_agents:
        await agent.start()
    
    
    print("ParkingSlotAgents are running...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")

    # Stop agents
    for agent in parking_agents:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())

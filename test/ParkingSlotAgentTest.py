# from spade.agent import Agent
# from spade.behaviour import CyclicBehaviour
# from spade.message import Message
# from spade.template import Template
# import json
# import asyncio


# class ParkingSlotAgent(Agent):
#     def __init__(self, jid, password, location, cost_per_hour):
#         super().__init__(jid, password)
#         self.location = location
#         self.cost_per_hour = cost_per_hour

#     class RespondToRequest(CyclicBehaviour):
#         async def on_start(self):
#             # Register with the BroadcastAgent
#             register_msg = Message(to="SPMSBroadcast@localhost")  # BroadcastAgent JID
#             register_msg.set_metadata("performative", "inform")
#             register_msg.body = json.dumps({"type": "register_slot"})
#             await self.send(register_msg)
#             print(f"[{self.agent.jid}] Registered with BroadcastAgent.")

#         async def run(self):
#             msg = await self.receive(timeout=20)  # Wait for forwarded parking requests
#             if msg:
#                 content = json.loads(msg.body)
#                 print(f"[{self.agent.jid}] Received parking request: {content}")
#                 if content.get("type") == "parking_request":
#                     # Respond directly to the CarAgent
#                     car_agent = content.get("jid")
#                     response = Message(to=car_agent)
#                     response.set_metadata("performative", "inform")
#                     response.body = json.dumps({
#                         "type": "parking_response",
#                         "location": self.agent.location,
#                         "cost_per_hour": self.agent.cost_per_hour
#                     })
#                     await self.send(response)
#                     print(f"[{self.agent.jid}] Sent parking details to {car_agent}.")
#                 elif content.get("type") == "confirm_parking":
#                     self.agent.parked_slot = content.get("slot")
#                     print(f"[{self.agent.jid}] Car parked in slot: {self.agent.parked_slot}")
#                     self.set_next_state("WAIT_FOR_DEPARTURE")
    
#     class WaitForDeparture(CyclicBehaviour):
#         async def run(self):
#             msg = await self.receive(timeout=20)
#             if msg:
#                 content = json.loads(msg.body)
#                 print(f"[{self.agent.jid}] Received departure confirmation: {content}")
#                 if content.get("type") == "confirm_departure":
#                     self.agent.parked_slot = None
#                     print(f"[{self.agent.jid}] Car departed.")
#                     self.set_next_state("RESPOND_TO_REQUEST")
            
                    

#     async def setup(self):
#         print(f"[{self.jid}] ParkingSlotAgent starting...")
#         self.fsm
#         self.add_behaviour(self.RespondToRequest())
#         self.add_behaviour(self.WaitForDeparture())
        
    
        
# async def main():
#     # Start ParkingSlotAgents
#     slot1 = ParkingSlotAgent("parking1@localhost", "parking1", location=(10, 10), cost_per_hour=5)
#     slot2 = ParkingSlotAgent("parking2@localhost", "parking2", location=(20, 20), cost_per_hour=3)
#     await slot1.start()
#     await slot2.start()
    
#     try:
#         while True:
#             await asyncio.sleep(1)
#     except KeyboardInterrupt:
#         print("Stopping agents...")
        
#     # Stop all agents
#     await slot1.stop()
#     await slot2.stop()
    
# if __name__ == "__main__":
#     asyncio.run(main())


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
            self.set_next_state("WAIT_FOR_REQUEST")

    # WAIT_FOR_REQUEST State: Wait for car parking requests
    class WaitForRequestState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Waiting for parking requests...")
            msg = await self.receive(timeout=20)  # Wait for parking requests
            if msg:
                content = json.loads(msg.body)
                print(f"[{self.agent.jid}] Received parking request: {content}")
                if content.get("type") == "parking_request":
                    # Respond with slot details directly to CarAgent
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
                    self.set_next_state("WAIT_FOR_CONFIRMATION")
                else:
                    print(f"[{self.agent.jid}] Invalid message received.")
            else:
                print(f"[{self.agent.jid}] No parking request received.")

    # WAIT_FOR_CONFIRMATION State: Wait for a confirmation from CarAgent
    class WaitForConfirmationState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Waiting for parking confirmation...")
            
            time_out = 10
            response = None
            while time_out > 0:
                msg = await self.receive(timeout=1)
                if msg:
                    content = json.loads(msg.body)
                    print(f"[{self.agent.jid}] Received message: {content}")
                    if content.get("type") == "confirm_parking":
                        if content.get("slot") == self.agent.jid:
                            response = content
                time_out -= 1
            if response:
                response_msg = Message(to=response.get("car"))
                response_msg.set_metadata("performative", "inform")
                response_msg.body = json.dumps({
                    "type": "confirm_response",
                    "slot": self.agent.location
                })
                await self.send(response_msg)
                print(f"[{self.agent.jid}] Parking confirmed for car: {self.agent.current_car}.")
                self.set_next_state("WAIT_FOR_DEPARTURE")
            else:
                print(f"[{self.agent.jid}] No valid confirmation received.")
                # self.set_next_state("WAIT_FOR_REQUEST")
            
                
                #         self.agent.current_car = content.get("car")
                #         response_msg = Message(to=content.get("car"))
                #         response_msg.set_metadata("performative", "inform")
                #         response_msg.body = json.dumps({
                #             "type": "confirm_response",
                #             "slot": self.agent.location
                #         })
                #         await self.send(response_msg)
                #         print(f"[{self.agent.jid}] Parking confirmed for car: {self.agent.current_car}.")
                #         self.set_next_state("WAIT_FOR_DEPARTURE")
                #     else:
                #         print(f"[{self.agent.jid}] No valid confirmation received.")
                # else:
                #     print(f"[{self.agent.jid}] No confirmation received, returning to WAIT_FOR_REQUEST.")
                #     self.set_next_state("WAIT_FOR_REQUEST")

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
                    self.set_next_state("WAIT_FOR_REQUEST")
                else:
                    print(f"[{self.agent.jid}] Invalid departure message received.")
            else:
                print(f"[{self.agent.jid}] No departure message received, slot still occupied.")

    # Setup FSMBehaviour
    async def setup(self):
        print(f"[{self.jid}] ParkingSlotAgent starting at location {self.location}...")
        fsm = FSMBehaviour()
        fsm.add_state(name="REGISTER", state=self.RegisterState(), initial=True)
        fsm.add_state(name="WAIT_FOR_REQUEST", state=self.WaitForRequestState())
        fsm.add_state(name="WAIT_FOR_CONFIRMATION", state=self.WaitForConfirmationState())
        fsm.add_state(name="WAIT_FOR_DEPARTURE", state=self.WaitForDepartureState())

        fsm.add_transition(source="REGISTER", dest="WAIT_FOR_REQUEST")
        fsm.add_transition(source="WAIT_FOR_REQUEST", dest="WAIT_FOR_CONFIRMATION")
        fsm.add_transition(source="WAIT_FOR_CONFIRMATION", dest="WAIT_FOR_DEPARTURE")
        fsm.add_transition(source="WAIT_FOR_DEPARTURE", dest="WAIT_FOR_REQUEST")

        self.add_behaviour(fsm)


# Main Function to Start ParkingSlotAgents
async def main():
    # Start two parking slots
    slot1 = ParkingSlotAgent("parking1@localhost", "parking1", location=(10, 10), cost_per_hour=5)
    slot2 = ParkingSlotAgent("parking2@localhost", "parking2", location=(20, 20), cost_per_hour=3)
    
    await slot1.start()
    await slot2.start()
    print("ParkingSlotAgents are running...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")

    # Stop agents
    await slot1.stop()
    await slot2.stop()

if __name__ == "__main__":
    asyncio.run(main())

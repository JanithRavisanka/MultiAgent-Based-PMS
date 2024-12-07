from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import math


class ParkingAgent(Agent):
    def __init__(self, jid, password, parking_id, location, capacity, cost_per_hour):
        super().__init__(jid, password)
        self.parking_id = parking_id
        self.location = location
        self.capacity = capacity
        self.available_slots = capacity
        self.cost_per_hour = cost_per_hour
        self.occupied_slots = {}

    def calculate_distance(self, car_location):
        return math.sqrt((self.location[0] - car_location[0]) ** 2 + (self.location[1] - car_location[1]) ** 2)

    class HandleParkingRequestsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for parking request
            if msg:
                content = json.loads(msg.body)
                if content.get("type") == "parking_request":
                    car_location = tuple(content["location"])
                    car_id = content["car_id"]
                    
                    # Check if parking has availability
                    if self.agent.available_slots > 0:
                        distance = self.agent.calculate_distance(car_location)
                        response = {
                            "type": "parking_response",
                            "parking_id": self.agent.parking_id,
                            "distance": distance,
                            "cost_per_hour": self.agent.cost_per_hour,
                            "available_slots": self.agent.available_slots
                        }
                        
                        reply = msg.make_reply()
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps(response)
                        await self.send(reply)
                        print(f"{self.agent.parking_id}: Responded to {car_id} with details.")
                    else:
                        print(f"{self.agent.parking_id}: No available slots to respond to {car_id}.")

    class HandleParkingConfirmationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for parking confirmation
            if msg:
                content = json.loads(msg.body)
                if content.get("type") == "confirm_parking":
                    car_id = content["car_id"]
                    
                    if self.agent.available_slots > 0:
                        self.agent.available_slots -= 1
                        self.agent.occupied_slots[car_id] = {
                            "start_time": self.current_time(),
                            "cost_per_hour": self.agent.cost_per_hour
                        }
                        print(f"{self.agent.parking_id}: Reserved a slot for {car_id}.")
                        
                        reply = msg.make_reply()
                        reply.set_metadata("performative", "confirm")
                        reply.body = json.dumps({"status": "reserved", "car_id": car_id})
                        await self.send(reply)
                    else:
                        print(f"{self.agent.parking_id}: No available slots to confirm for {car_id}.")

    class HandleCarLeaveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for "car_leave" message
            if msg:
                content = json.loads(msg.body)
                if content.get("type") == "car_leave":
                    car_id = content["car_id"]
                    
                    if car_id in self.agent.occupied_slots:
                        # Free the parking slot and update availability
                        del self.agent.occupied_slots[car_id]
                        self.agent.available_slots += 1
                        print(f"{self.agent.parking_id}: Car {car_id} has left. Slot freed.")
                        
                        # Send acknowledgment to the car agent
                        reply = msg.make_reply()
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps({"status": "slot_freed", "car_id": car_id})
                        await self.send(reply)
                    else:
                        print(f"{self.agent.parking_id}: Car {car_id} was not found in the occupied slots.")

    def current_time(self):
        import time
        return time.time()

    async def setup(self):
        print(f"ParkingAgent {self.parking_id} starting...")
        self.add_behaviour(self.HandleParkingRequestsBehaviour())
        self.add_behaviour(self.HandleParkingConfirmationBehaviour())
        self.add_behaviour(self.HandleCarLeaveBehaviour())  # Add the new behavior


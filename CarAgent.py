import random
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json

# class CarAgent(Agent):
#     def __init__(self, jid, password, car_id, preferences, location):
#         """
#         Initialize the car agent.

#         :param jid: The Jabber ID of the agent.
#         :param password: The password for the agent.
#         :param car_id: A unique identifier for the car (e.g., license plate).
#         :param preferences: A dictionary with preferences for distance and cost.
#         :param location: A tuple representing the car's location (x, y).
#         """
#         super().__init__(jid, password)
#         self.car_id = car_id
#         self.preferences = preferences
#         self.location = location
#         self.selected_parking = None
#         self.parking_options = []  # List to store parking options received in response
#         self.status = "idle"

#     class RequestParkingBehaviour(OneShotBehaviour):
#         async def run(self):
#             """
#             Broadcast a parking request to nearby parking agents after a random delay.
#             """
#             await asyncio.sleep(random.uniform(1, 5))  # Random delay before sending the request (1 to 5 seconds)
#             print(f"{self.agent.car_id}: Broadcasting parking request...")
            
#             # Sending message to all available parking agents (can be modified to specific agents)
#             msg = Message(to="all@localhost")  # Replace with actual broadcast logic or JIDs of nearby parking agents
#             msg.set_metadata("performative", "request")
#             msg.body = json.dumps({
#                 "type": "parking_request",
#                 "car_id": self.agent.car_id,
#                 "location": self.agent.location
#             })
#             await self.send(msg)
#             print(f"{self.agent.car_id}: Parking request broadcasted.")

#     class HandleParkingResponsesBehaviour(CyclicBehaviour):
#         async def run(self):
#             """
#             Handle parking responses and choose the best option based on preferences.
#             """
#             msg = await self.receive(timeout=10)  # Wait for a response for 10 seconds
#             if msg:
#                 response = json.loads(msg.body)
#                 print(f"{self.agent.car_id}: Received response: {response}")
                
#                 # Evaluate response based on preferences
#                 distance = response.get("distance")
#                 cost = response.get("cost_per_hour")
#                 score = (1 / distance) * self.agent.preferences["distance_weight"] + \
#                         (1 / cost) * self.agent.preferences["cost_weight"]
                
#                 response["score"] = score
#                 self.agent.parking_options.append(response)
#             else:
#                 if self.agent.parking_options:
#                     # Choose the best parking option based on calculated score
#                     best_option = max(self.agent.parking_options, key=lambda x: x["score"])
#                     self.agent.selected_parking = best_option
#                     print(f"{self.agent.car_id}: Selected parking: {best_option}")
#                     await self.confirm_parking(best_option)

#         async def confirm_parking(self, parking_option):
#             """
#             Confirm the selected parking slot with the parking agent.
#             """
#             print(f"{self.agent.car_id}: Confirming parking with {parking_option['parking_id']}...")
#             msg = Message(to=parking_option["parking_id"])
#             msg.set_metadata("performative", "confirm")
#             msg.body = json.dumps({
#                 "type": "confirm_parking",
#                 "car_id": self.agent.car_id,
#                 "selected_parking": parking_option
#             })
#             await self.send(msg)

#     class LeaveParkingBehaviour(CyclicBehaviour):
#         async def run(self):
#             """
#             Simulate the car leaving after a random parking duration.
#             """
#             await asyncio.sleep(random.uniform(5, 10))  # Random time (5 to 10 seconds) before leaving
#             if self.agent.selected_parking:
#                 print(f"{self.agent.car_id}: Leaving parking {self.agent.selected_parking['parking_id']}...")
#                 msg = Message(to=self.agent.selected_parking["parking_id"])
#                 msg.set_metadata("performative", "exit")
#                 msg.body = json.dumps({
#                     "type": "car_exit",
#                     "car_id": self.agent.car_id
#                 })
#                 await self.send(msg)
#                 print(f"{self.agent.car_id}: Exit message sent.")
#                 self.agent.status = "idle"  # Set status back to idle
#                 self.agent.selected_parking = None

#     async def setup(self):
#         """
#         Set up the agent and add behaviours.
#         """
#         print(f"CarAgent {self.car_id} starting...")
#         self.add_behaviour(self.RequestParkingBehaviour())  # Request parking
#         self.add_behaviour(self.HandleParkingResponsesBehaviour())  # Handle parking responses
#         self.add_behaviour(self.LeaveParkingBehaviour())  # Leave parking after a random duration


# async def main():
#     # Create multiple CarAgents with random positions and preferences
#     car_agents = []
#     for i in range(1,4):  # Create 5 car agents
#         preferences = {"distance_weight": random.uniform(0, 1), "cost_weight": random.uniform(0, 1)}
#         car_agent = CarAgent(f"car{i}@localhost", f"car{i}", f"Car-{i}", preferences, location=(random.randint(0, 10), random.randint(0, 10)))
#         car_agents.append(car_agent)

#     # Start the agents
#     for car_agent in car_agents:
#         await car_agent.start()

#     # Simulate continuous operation (agents running in the background)
#     try:
#         while True:
#             await asyncio.sleep(1)
#     except KeyboardInterrupt:
#         # Stop all agents when the program ends
#         for car_agent in car_agents:
#             await car_agent.stop()

#         print("All agents stopped. Exiting...")
#         import sys
#         sys.exit(0)


# # Run the main function
# asyncio.run(main())


# class CarAgent(Agent):
#     def __init__(self, jid, password, car_id, preferences, location):
#         super().__init__(jid, password)
#         self.car_id = car_id
#         self.preferences = preferences
#         self.location = location
#         self.selected_parking = None
#         self.parking_options = []

#     class RequestParkingBehaviour(OneShotBehaviour):
#         async def run(self):
#             await asyncio.sleep(random.uniform(1, 5))  # Random delay before sending the request
#             print(f"{self.agent.car_id}: Broadcasting parking request...")
#             msg = Message(to="all@localhost")  # Broadcast to all parking agents
#             msg.set_metadata("performative", "request")
#             msg.body = json.dumps({
#                 "type": "parking_request",
#                 "car_id": self.agent.car_id,
#                 "location": self.agent.location
#             })
#             await self.send(msg)

#     class HandleParkingResponsesBehaviour(CyclicBehaviour):
#         async def run(self):
#             msg = await self.receive(timeout=10)
#             if msg:
#                 response = json.loads(msg.body)
#                 distance = response.get("distance")
#                 cost = response.get("cost_per_hour")
#                 score = (1 / distance) * self.agent.preferences["distance_weight"] + \
#                         (1 / cost) * self.agent.preferences["cost_weight"]
                
#                 response["score"] = score
#                 self.agent.parking_options.append(response)
#             else:
#                 if self.agent.parking_options:
#                     best_option = max(self.agent.parking_options, key=lambda x: x["score"])
#                     self.agent.selected_parking = best_option
#                     print(f"{self.agent.car_id}: Selected parking: {best_option}")
#                     await self.confirm_parking(best_option)

#         async def confirm_parking(self, parking_option):
#             print(f"{self.agent.car_id}: Confirming parking with {parking_option['parking_id']}...")
#             msg = Message(to=parking_option["parking_id"])
#             msg.set_metadata("performative", "confirm")
#             msg.body = json.dumps({
#                 "type": "confirm_parking",
#                 "car_id": self.agent.car_id,
#                 "selected_parking": parking_option
#             })
#             await self.send(msg)

#     class HandleCarLeaveBehaviour(CyclicBehaviour):
#         async def run(self):
#             # Simulate the car leaving after some time
#             await asyncio.sleep(random.uniform(5, 10))  # Random delay before leaving
#             print(f"{self.agent.car_id}: Leaving parking.")
#             if self.agent.selected_parking:
#                 msg = Message(to=self.agent.selected_parking["parking_id"])
#                 msg.set_metadata("performative", "inform")
#                 msg.body = json.dumps({
#                     "type": "car_leave",
#                     "car_id": self.agent.car_id
#                 })
#                 await self.send(msg)

#     async def setup(self):
#         print(f"CarAgent {self.car_id} starting...")
#         self.add_behaviour(self.RequestParkingBehaviour())
#         self.add_behaviour(self.HandleParkingResponsesBehaviour())
#         self.add_behaviour(self.HandleCarLeaveBehaviour())  # Add the car leave behavior


class CarAgent(Agent):
    def __init__(self, jid, password, car_id, preferences, location):
        super().__init__(jid, password)
        self.car_id = car_id
        self.preferences = preferences
        self.location = location
        self.selected_parking = None
        self.parking_options = []
        self.status = "driving"

    class RequestParkingBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(random.uniform(1, 5))  # Random delay before sending the request
            print(f"{self.agent.car_id}: Broadcasting parking request...")
            msg = Message(to="all@localhost")  # Broadcast to all parking agents
            msg.set_metadata("performative", "request")
            msg.body = json.dumps({
                "type": "parking_request",
                "car_id": self.agent.car_id,
                "location": self.agent.location
            })
            await self.send(msg)

    class HandleParkingResponsesBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                response = json.loads(msg.body)
                distance = response.get("distance")
                cost = response.get("cost_per_hour")
                score = (1 / distance) * self.agent.preferences["distance_weight"] + \
                        (1 / cost) * self.agent.preferences["cost_weight"]
                
                response["score"] = score
                self.agent.parking_options.append(response)
            else:
                if self.agent.parking_options:
                    best_option = max(self.agent.parking_options, key=lambda x: x["score"])
                    self.agent.selected_parking = best_option
                    print(f"{self.agent.car_id}: Selected parking: {best_option}")
                    await self.confirm_parking(best_option)

        async def confirm_parking(self, parking_option):
            print(f"{self.agent.car_id}: Confirming parking with {parking_option['parking_id']}...")
            msg = Message(to=parking_option["parking_id"])
            msg.set_metadata("performative", "confirm")
            msg.body = json.dumps({
                "type": "confirm_parking",
                "car_id": self.agent.car_id,
                "selected_parking": parking_option
            })
            await self.send(msg)

    class HandleCarLeaveBehaviour(CyclicBehaviour):
        async def run(self):
            # Simulate the car leaving after some time
            await asyncio.sleep(random.uniform(5, 10))  # Random delay before leaving

            # Check if the car has a selected parking slot
            if self.agent.selected_parking:
                print(f"{self.agent.car_id}: Leaving parking {self.agent.selected_parking['parking_id']}...")
                
                # Send a message to the parking agent to indicate the car has left
                msg = Message(to=self.agent.selected_parking["parking_id"])
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "car_leave",
                    "car_id": self.agent.car_id
                })
                await self.send(msg)
                print(f"{self.agent.car_id}: Exit message sent.")
                
                # Update car status and parking slot
                self.agent.selected_parking = None
                self.agent.status = "idle"  # Set status back to idle
            else:
                # If the car hasn't been assigned a parking slot, do nothing
                print(f"{self.agent.car_id}: Not currently parked, cannot leave.")

    # async def setup(self):
    #     print(f"CarAgent {self.car_id} starting...")
    #     self.add_behaviour(self.RequestParkingBehaviour())
    #     self.add_behaviour(self.HandleParkingResponsesBehaviour())
    #     self.add_behaviour(self.HandleCarLeaveBehaviour())  # Add the car leave behavior
        
    
    
    # create a funtion that will change the status of the car to seraching for parking in random time
    async def search_for_parking(self):
        await asyncio.sleep(random.uniform(5, 10))  # Random delay before searching for parking
        print(f"{self.car_id}: Searching for parking...")
        self.status = "searching"
        await self.RequestParkingBehaviour().run()
        await self.HandleParkingResponsesBehaviour().run()
        
    async def leave_parking(self):
        await asyncio.sleep(random.uniform(5, 10))
        
    
        

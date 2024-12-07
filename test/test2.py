from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json

class CarAgent(Agent):
    def __init__(self, jid, password, car_id, preferences, location):
        """
        Initialize the car agent.

        :param jid: The Jabber ID of the agent.
        :param password: The password for the agent.
        :param car_id: A unique identifier for the car (e.g., license plate).
        :param preferences: A dictionary with preferences for distance and cost.
        :param location: A tuple representing the car's location (x, y).
        """
        super().__init__(jid, password)
        self.car_id = car_id
        self.preferences = preferences
        self.location = location
        self.selected_parking = None

    class RequestParkingBehaviour(OneShotBehaviour):
        async def run(self):
            """
            Broadcast a parking request to nearby parking agents.
            """
            print(f"{self.agent.car_id}: Broadcasting parking request...")
            
            msg = Message(to="all@domain")  # Replace with actual broadcast logic
            msg.set_metadata("performative", "request")
            msg.body = json.dumps({
                "type": "parking_request",
                "car_id": self.agent.car_id,
                "location": self.agent.location
            })
            await self.send(msg)
            print(f"{self.agent.car_id}: Parking request broadcasted.")

    class HandleParkingResponsesBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Handle parking responses and choose the best option.
            """
            msg = await self.receive(timeout=10)  # Wait for a response
            if msg:
                response = json.loads(msg.body)
                print(f"{self.agent.car_id}: Received response: {response}")
                
                # Evaluate response based on preferences
                distance = response.get("distance")
                cost = response.get("cost_per_hour")
                score = (1 / distance) * self.agent.preferences["distance_weight"] + \
                        (1 / cost) * self.agent.preferences["cost_weight"]
                
                response["score"] = score
                self.agent.parking_options.append(response)
            else:
                if self.agent.parking_options:
                    # Choose the best parking option
                    best_option = max(self.agent.parking_options, key=lambda x: x["score"])
                    self.agent.selected_parking = best_option
                    print(f"{self.agent.car_id}: Selected parking: {best_option}")
                    await self.confirm_parking(best_option)

        async def confirm_parking(self, parking_option):
            """
            Confirm the selected parking slot with the parking agent.
            """
            print(f"{self.agent.car_id}: Confirming parking with {parking_option['parking_id']}...")
            msg = Message(to=parking_option["parking_id"])
            msg.set_metadata("performative", "confirm")
            msg.body = json.dumps({
                "type": "confirm_parking",
                "car_id": self.agent.car_id,
                "selected_parking": parking_option
            })
            await self.send(msg)

    async def setup(self):
        """
        Set up the agent and add behaviours.
        """
        print(f"CarAgent {self.car_id} starting...")
        self.parking_options = []  # Store received parking options
        self.add_behaviour(self.RequestParkingBehaviour())
        self.add_behaviour(self.HandleParkingResponsesBehaviour())

# from spade.agent import Agent
# from spade.behaviour import CyclicBehaviour
# from spade.message import Message
# import json
# import time


# class PaymentAgent(Agent):
#     def __init__(self, jid, password, parking_id):
#         """
#         Initialize the PaymentAgent.

#         :param jid: The Jabber ID of the agent.
#         :param password: The password for the agent.
#         :param parking_id: The ID of the associated parking lot.
#         """
#         super().__init__(jid, password)
#         self.parking_id = parking_id
#         self.car_records = {}  # Stores car entry and exit times
#         self.cost_per_hour = None  # To be set dynamically based on parking info

#     def calculate_payment(self, entry_time, exit_time):
#         """
#         Calculate payment based on entry and exit times.

#         :param entry_time: Timestamp when the car entered.
#         :param exit_time: Timestamp when the car exited.
#         :return: The total cost for the duration.
#         """
#         hours_parked = (exit_time - entry_time) / 3600  # Convert seconds to hours
#         return round(hours_parked * self.cost_per_hour, 2)

#     class TrackCarBehaviour(CyclicBehaviour):
#         async def run(self):
#             """
#             Handle messages to track car entry and exit.
#             """
#             msg = await self.receive(timeout=10)  # Wait for messages
#             if msg:
#                 content = json.loads(msg.body)
#                 msg_type = content.get("type")
#                 car_id = content.get("car_id")

#                 if msg_type == "car_entry":
#                     # Log the car's entry
#                     if car_id not in self.agent.car_records:
#                         self.agent.car_records[car_id] = {"entry_time": time.time()}
#                         self.agent.cost_per_hour = content["cost_per_hour"]
#                         print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} entered at {self.agent.car_records[car_id]['entry_time']}.")
                        
#                         # Acknowledge the car's entry
#                         reply = msg.make_reply()
#                         reply.set_metadata("performative", "inform")
#                         reply.body = json.dumps({"status": "entry_logged", "car_id": car_id})
#                         await self.send(reply)
#                     else:
#                         print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} is already logged.")

#                 elif msg_type == "car_exit":
#                     # Log the car's exit and calculate payment
#                     if car_id in self.agent.car_records:
#                         entry_time = self.agent.car_records[car_id]["entry_time"]
#                         exit_time = time.time()
#                         total_cost = self.agent.calculate_payment(entry_time, exit_time)

#                         print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} exited. Total cost: {total_cost}.")
#                         del self.agent.car_records[car_id]  # Remove the car record

#                         # Send payment details to the car agent
#                         reply = msg.make_reply()
#                         reply.set_metadata("performative", "inform")
#                         reply.body = json.dumps({"status": "payment_due", "car_id": car_id, "total_cost": total_cost})
#                         await self.send(reply)
#                     else:
#                         print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} is not found in the records.")

#     async def setup(self):
#         """
#         Set up the PaymentAgent and its behaviour.
#         """
#         print(f"PaymentAgent for Parking {self.parking_id} starting...")
#         self.add_behaviour(self.TrackCarBehaviour())


from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import time

class PaymentAgent(Agent):
    def __init__(self, jid, password, parking_id):
        """
        Initialize the PaymentAgent.

        :param jid: The Jabber ID of the agent.
        :param password: The password for the agent.
        :param parking_id: The ID of the associated parking lot.
        """
        super().__init__(jid, password)
        self.parking_id = parking_id
        self.car_records = {}  # Stores car entry and exit times
        self.cost_per_hour = None  # To be set dynamically based on parking info

    def calculate_payment(self, entry_time, exit_time):
        """
        Calculate payment based on entry and exit times.

        :param entry_time: Timestamp when the car entered.
        :param exit_time: Timestamp when the car exited.
        :return: The total cost for the duration.
        """
        hours_parked = (exit_time - entry_time) / 3600  # Convert seconds to hours
        return round(hours_parked * self.cost_per_hour, 2)

    class TrackCarBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Handle messages to track car entry and exit.
            """
            msg = await self.receive(timeout=10)  # Wait for messages
            if msg:
                content = json.loads(msg.body)
                msg_type = content.get("type")
                car_id = content.get("car_id")

                if msg_type == "car_entry":
                    # Log the car's entry
                    if car_id not in self.agent.car_records:
                        self.agent.car_records[car_id] = {"entry_time": time.time()}
                        self.agent.cost_per_hour = content["cost_per_hour"]
                        print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} entered at {self.agent.car_records[car_id]['entry_time']}.")
                        
                        # Acknowledge the car's entry
                        reply = msg.make_reply()
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps({"status": "entry_logged", "car_id": car_id})
                        await self.send(reply)
                    else:
                        print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} is already logged.")

                elif msg_type == "car_exit":
                    # Log the car's exit and calculate payment
                    if car_id in self.agent.car_records:
                        entry_time = self.agent.car_records[car_id]["entry_time"]
                        exit_time = time.time()
                        total_cost = self.agent.calculate_payment(entry_time, exit_time)

                        print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} exited. Total cost: {total_cost}.")
                        del self.agent.car_records[car_id]  # Remove the car record

                        # Send payment details to the car agent
                        reply = msg.make_reply()
                        reply.set_metadata("performative", "inform")
                        reply.body = json.dumps({"status": "payment_due", "car_id": car_id, "total_cost": total_cost})
                        await self.send(reply)
                    else:
                        print(f"PaymentAgent ({self.agent.parking_id}): Car {car_id} is not found in the records.")

    async def setup(self):
        """
        Set up the PaymentAgent and its behaviour.
        """
        print(f"PaymentAgent for Parking {self.parking_id} starting...")
        self.add_behaviour(self.TrackCarBehaviour())


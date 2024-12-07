# import asyncio
# # Import your agent classes here
# from CarAgent import CarAgent
# from ParkingAgent import ParkingAgent
# from PaymentAgent import PaymentAgent

# async def main():
#     # Create ParkingAgents
#     parking_agent_1 = ParkingAgent("parking1@localhost", "parking1", "Parking-1", capacity=5, cost_per_hour=10, location=(0, 0))
#     parking_agent_2 = ParkingAgent("parking2@localhost", "parking2", "Parking-2", capacity=3, cost_per_hour=8, location=(5, 5))

#     # Create PaymentAgents
#     payment_agent_1 = PaymentAgent("payment1@localhost", "payment1", "Parking-1")
#     payment_agent_2 = PaymentAgent("payment2@localhost", "payment2", "Parking-2")

#     # Start ParkingAgents and PaymentAgents
#     await parking_agent_1.start()
#     parking_agent_1.link_payment_agent(payment_agent_1.jid)
#     await payment_agent_1.start()

#     await parking_agent_2.start()
#     parking_agent_2.link_payment_agent(payment_agent_2.jid)
#     await payment_agent_2.start()

#     # Create CarAgents
#     car_agent_1 = CarAgent("car1@localhost", "car1", car_id="Car-1", preferences={"distance_weight": 0.5, "cost_weight": 0.5}, location=(2, 2))
#     car_agent_2 = CarAgent("car2@localhost", "car2", car_id="Car-2", preferences={"distance_weight": 0.5, "cost_weight": 0.5}, location=(10, 10))

#     # Start CarAgents
#     await car_agent_1.start()
#     await car_agent_2.start()

#     # Simulate CarAgent 1 requesting parking
#     await asyncio.sleep(1)  # Wait for all agents to start
#     await car_agent_1.request_parking("parking1@localhost")

#     # Simulate CarAgent 2 requesting parking
#     await asyncio.sleep(2)  # Simulate a delay in arrival
#     await car_agent_2.request_parking("parking2@localhost")

#     print("System is running. Press Ctrl+C to stop.")

#     try:
#         while True:
#             await asyncio.sleep(1)
#     except KeyboardInterrupt:
#         await car_agent_1.stop()
#         await car_agent_2.stop()
#         await parking_agent_1.stop()
#         await parking_agent_2.stop()
#         await payment_agent_1.stop()
#         await payment_agent_2.stop()

#         # Exit the program
#         print("All agents stopped. Exiting...")
#         import sys
#         sys.exit(0)

# # Run the main function
# asyncio.run(main())


import asyncio
import random
# Import your agent classes here
from CarAgent import CarAgent
from ParkingAgent import ParkingAgent

from PaymentAgent import PaymentAgent

async def main():
    # Create multiple ParkingAgents with different properties
    parking_agents = []
    for i in range(1, 4):  # Three parking agents
        parking_agent = ParkingAgent(f"parking{i}@localhost", f"parking{i}", f"Parking-{i}", (random.randint(0, 10), random.randint(0, 10)), 10, random.randint(5, 15))
        parking_agents.append(parking_agent)

    # Start all parking agents
    for parking_agent in parking_agents:
        await parking_agent.start()

    # Create multiple CarAgents
    car_agents = []
    for i in range(1, 4):  # Five car agents
        preferences = {"distance_weight": random.uniform(0, 1), "cost_weight": random.uniform(0, 1)}
        car_agent = CarAgent(f"car{i}@localhost", f"car{i}", f"Car-{i}", preferences, location=(random.randint(0, 10), random.randint(0, 10)))
        car_agents.append(car_agent)

    # Start all car agents
    for car_agent in car_agents:
        await car_agent.start()

    # Simulate continuous operation (agents running in the background)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Stop all agents when the program ends
        for car_agent in car_agents:
            await car_agent.stop()
        for parking_agent in parking_agents:
            await parking_agent.stop()

        print("All agents stopped. Exiting...")
        import sys
        sys.exit(0)

# Run the main function
asyncio.run(main())

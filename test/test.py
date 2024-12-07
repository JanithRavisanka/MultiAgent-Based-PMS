import asyncio
from spade.web import WebApp as Web

from BroadCastAgent import BroadcastAgent
from CarAgentTest import CarAgent
from ParkingSlotAgentTest import ParkingSlotAgent

async def main():
    # Start the web interface for monitoring
    # Web.start(hostname="127.0.0.1", port=10000)

    # Start the BroadcastAgent
    broadcast_agent = BroadcastAgent("SPMSBroadcast@localhost", "broadcast")
    await broadcast_agent.start()
    

    # Start ParkingSlotAgents
    slot1 = ParkingSlotAgent("parking1@localhost", "parking1", location=(10, 10), cost_per_hour=5)
    slot2 = ParkingSlotAgent("parking2@localhost", "parking2", location=(20, 20), cost_per_hour=3)
    
    await slot1.start()
    await slot2.start()

    # Start CarAgent
    car_agent = CarAgent("car1@localhost", "car1", location=(5, 5))
    # car_agent2 = CarAgent("car2@localhost", "car2", location=(15, 15))
    
    await car_agent.start()
    # await car_agent2.start()

    # print("Agents are running... Access the web interface at http://127.0.0.1:10000")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")

    # Stop all agents
    await broadcast_agent.stop()
    await slot1.stop()
    await slot2.stop()
    await car_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())

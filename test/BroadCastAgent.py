from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import asyncio

class BroadcastAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.parking_slots = set()  # Registered parking slots
        

    class ManageRequests(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for messages
            if msg:
                print(f"[{self.agent.jid}] Received message from {msg.sender}")

                content = json.loads(msg.body)
                
                print(f"[{self.agent.jid}] Content: {content}")
                sender = str(msg.sender)

                # Register parking slot agents
                if content.get("type") == "register_slot":
                    self.agent.parking_slots.add(sender)
                    print(f"[{self.agent.jid}] Registered ParkingSlot: {sender}")

                # Forward parking request to all parking slots
                elif content.get("type") == "parking_request":
                    print(f"[{self.agent.jid}] Forwarding request to parking slots...")
                    for slot in self.agent.parking_slots:
                        forward_msg = Message(to=slot)
                        forward_msg.set_metadata("performative", "inform")
                        forward_msg.body = json.dumps(content)
                        await self.send(forward_msg)

    async def setup(self):
        print(f"[{self.jid}] BroadcastAgent starting...")
        self.add_behaviour(self.ManageRequests())
        
        
async def main():

    # Start the BroadcastAgent
    broadcast_agent = BroadcastAgent("SPMSBroadcast@localhost", "broadcast")
    await broadcast_agent.start()
    
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")
        
    # Stop all agents
    await broadcast_agent.stop()
    
if __name__ == "__main__":
    asyncio.run(main())
    
        
    
    

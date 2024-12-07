import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template

class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            try:
                print("InformBehav running")
                msg = Message(to="responderAgent@localhost")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = "Hello World"                    # Set the message content

                await self.send(msg)
                print("Message sent!")
            except Exception as e:
                print(f"Error while sending message: {e}")
            finally:
                await self.agent.stop()  # stop agent after behaviour

    async def setup(self):
        print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)

class ReceiverAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            try:
                print("RecvBehav running")
                msg = await self.receive(timeout=10) # wait for a message for 10 seconds
                if msg:
                    print(f"Message received with content: {msg.body}")
                else:
                    print("Did not receive any message after 10 seconds")
            except Exception as e:
                print(f"Error while receiving message: {e}")
            finally:
                await self.agent.stop()  # stop agent after behaviour

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

async def main():
    try:
        receiveragent = ReceiverAgent("responderAgent@localhost", "12345678")
        await receiveragent.start(auto_register=True)
        print("Receiver started")

        senderagent = SenderAgent("requesterAgent@localhost", "12345678")
        await senderagent.start(auto_register=True)
        print("Sender started")

        await spade.wait_until_finished(receiveragent)
        print("Agents finished")
    except Exception as e:
        print(f"Error during agent execution: {e}")

if __name__ == "__main__":
    spade.run(main())
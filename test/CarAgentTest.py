from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import json
import asyncio
import random
from math import sqrt
import pygame
from collections import deque
import sys

pygame.init()


# Screen dimensions
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 950
GRID_SIZE = 35  # Size of grid cells

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)


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


#radom location should be a 0
def get_random_location():
    row = random.randint(0, len(ROAD_MAP) - 1)
    col = random.randint(0, len(ROAD_MAP[0]) - 1)
    while ROAD_MAP[row][col] != 0:
        row = random.randint(0, len(ROAD_MAP) - 1)
        col = random.randint(0, len(ROAD_MAP[0]) - 1)
    return (row, col)
    

# Convert pixel positions to grid positions
def pixel_to_grid(x, y):
    return x // GRID_SIZE, y // GRID_SIZE

def grid_to_pixel(row, col):
    return col * GRID_SIZE, row * GRID_SIZE

# Breadth-First Search for pathfinding
def bfs(start, goal, road_map):
    rows, cols = len(road_map), len(road_map[0])
    visited = set()
    queue = deque([(start, [])])

    while queue:
        (current, path) = queue.popleft()

        if current == goal:
            return path + [current]

        if current in visited:
            continue

        visited.add(current)
        row, col = current

        # Define possible directions (up, down, left, right)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and road_map[nr][nc] == 0:
                queue.append(((nr, nc), path + [current]))

    return None  # No path found


class CarAgent(Agent):
    def __init__(self, jid, password, shedule, screen, start_position=(0, 0)):
        super().__init__(jid, password)
        self.best_slot_jid = None     # Best parking slot found
        self.parked_slot_jid = None   # Slot where the car is parked
        # self.target_location = shedule["target_location"]
        self.parking_duration = shedule["parking_duration"]
        self.location = start_position
        self.path = []
        self.speed = 2
        self.target_index = 0
        self.screen = screen
        # self.clock = clock
        self.goal_position = shedule["target_location"]
        self.park_position = None
        self.initialize_rect()
        self.find_path()
        
    def set_path(self, new_path):
        self.path = new_path
        self.target_index =1
    
    def change_color(self, color):
        self.rect.fill(color)
        
    def update(self):
        # print(self.path)
        if not self.path or self.target_index >= len(self.path):
            return  # No movement needed

        target_row, target_col = self.path[self.target_index]
        target_x, target_y = grid_to_pixel(target_row, target_col)
        target_x += GRID_SIZE // 2
        target_y += GRID_SIZE // 2

        car_x, car_y = self.rect.center
        dx = target_x - car_x
        dy = target_y - car_y

        # Normalize the direction vector
        if abs(dx) > 0 or abs(dy) > 0:
            step_x = self.speed if dx > 0 else -self.speed if dx < 0 else 0
            step_y = self.speed if dy > 0 else -self.speed if dy < 0 else 0

            self.rect.move_ip(step_x, step_y)

            # Check if reached target
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.target_index += 1  # Move to the next point
                
    def draw(self):
        pygame.draw.rect(self.screen, BLUE, self.rect)
        
    def initialize_rect(self):
        start_x, start_y = grid_to_pixel(*self.location)
        self.rect = pygame.Rect(start_x + 5, start_y + 5, GRID_SIZE - 10, GRID_SIZE - 10)
    def find_path(self):
        path = bfs(self.location, self.goal_position, ROAD_MAP)
        if path:
            self.set_path(path)
        else:
            print("No path found!")   
    def set_goal_position(self, goal_position):
        self.goal_position = goal_position
        
    def find_path_to_park(self, parking_slot):
        """Find the nearest road block adjacent to the given parking slot."""
        row, col = parking_slot
        nr, nc = 0,0
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(ROAD_MAP) and 0 <= nc < len(ROAD_MAP[0]) and ROAD_MAP[nr][nc] == 0:
                return nr, nc  # Return the first road block found
        if nr == 0 and nc == 0:
            print(f"No road block found near parking slot {parking_slot}")
                
        
    # def random_location(self):
    #     return (random.randint(0, 50), random.randint(0, 50))   
        
    def calculate_distance(self, location1, location2):
        return round(sqrt(abs(location1[0] - location2[0])**2 + abs(location1[1] - location2[1])**2))
    
    def get_best_slot(self, slots):
        best_slot = None
        #cost is funtion of distance and cost per hour
        function_cost = lambda x: x["cost_per_hour"] + self.calculate_distance(self.location, x["location"])
        best_slot = min(slots, key=function_cost)
        return best_slot

    def driving_time(self, location1, location2):
        return self.calculate_distance(location1, location2) * 2
    
    class DriveState(State):
        async def run(self):
            # print(f"[{self.agent.jid}] Driving to target location: {self.agent.target_location}")

            if self.agent.target_index >= len(self.agent.path):
                print(f"[{self.agent.jid}] Arrived at target location.")
                self.agent.location = self.agent.goal_position
                self.set_next_state("SEARCH_AND_WAIT")
            else:
                self.set_next_state("DRIVE")
            
            
            
    class SearchAndWaitState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Sending parking search request to BroadcastAgent...")

            # Step 1: Send parking request to BroadcastAgent
            request_msg = Message(to="SPMSBroadcast@localhost")  # BroadcastAgent JID
            request_msg.set_metadata("performative", "inform")
            request_msg.body = json.dumps({
                "type": "parking_request", 
                # "location": self.agent.location, 
                "jid": str(self.agent.jid)
            })
            await self.send(request_msg)
            print(f"[{self.agent.jid}] Parking search request sent. Waiting for responses...")

            # Step 2: Wait for parking responses
            responses = []
            timeout = 5  # Collect responses for 5 seconds

            while timeout > 0:
                msg = await self.receive(timeout=1)
                if msg:
                    content = json.loads(msg.body)
                    if content.get("type") == "parking_response":
                        responses.append(content)
                        print(f"[{self.agent.jid}] Received parking response: {content}")
                timeout -= 1

            # Step 3: Process the responses
            if responses:
                # Select the best parking slot based on cost
                self.agent.best_slot_jid = self.agent.get_best_slot(responses)['slot_jid']
                print(f"[{self.agent.jid}] Best parking slot selected: {self.agent.best_slot_jid}")
                self.set_next_state("CONFIRM_PARKING")
            else:
                print(f"[{self.agent.jid}] No parking slots available. Retrying search...")
                self.set_next_state("SEARCH_AND_WAIT")  # Retry same state if no responses


            
    class ConfirmParkingState(State):
        async def run(self):
            await asyncio.sleep(1)
            print(f"[{self.agent.jid}] Confirming parking slot...")
            confirm_msg = Message(to=self.agent.best_slot_jid)
            print(f"[{self.agent.jid}] Sending confirm message to {self.agent.best_slot_jid}")
            confirm_msg.set_metadata("performative", "inform")
            confirm_msg.body = json.dumps({"type": "confirm_parking", "slot_jid": self.agent.best_slot_jid, "car": str(self.agent.jid)})
            await self.send(confirm_msg)
            
            #wait for response
            response = None
            timeout = 10
            while timeout > 0:
                msg = await self.receive(timeout=1)
                if msg:
                    content = json.loads(msg.body)
                    if content.get("type") == "confirm_response":
                        response = content
                        print(f"[{self.agent.jid}] Received confirm response: {content}")
                timeout -= 1
            if response:
                self.agent.parked_slot_jid = response["slot_jid"] 
                self.agent.park_position = tuple(response["slot"])
                # self.agent.goal_position = self.agent.parked_slot["location"]
                print(f"[{self.agent.jid}] Park Reserved.")
                self.agent.target_index = 1
                self.agent.goal_position = self.agent.find_path_to_park(self.agent.park_position)
                print(f"[{self.agent.jid}] Goal position: {self.agent.goal_position}")
                self.agent.find_path()
                self.set_next_state("DRIVETOPARK")
            else:
                print(f"[{self.agent.jid}] Parking not confirmed.")
                self.set_next_state("SEARCH_AND_WAIT")
                
    class DriveToParkState(State):
        async def run(self):
            
            print(f"[{self.agent.jid}] Driving to parking slot: {self.agent.parked_slot_jid}.")
            # print(f"[{self.agent.jid}] Path to parking slot: {self.agent.path}")
            if self.agent.target_index >= len(self.agent.path):
                print(f"[{self.agent.jid}] Arrived at parking slot.")
                self.agent.location = self.agent.goal_position
                self.set_next_state("PARKED")             
            else:
                self.set_next_state("DRIVETOPARK")

    class ParkedState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Car parked at {self.agent.parked_slot_jid}.")
            # Simulate parking by sleeping for 10 seconds
            await asyncio.sleep(self.agent.parking_duration+self.agent.driving_time(self.agent.location, self.agent.park_position))
            print(f"[{self.agent.jid}] Car has been parked for {self.agent.parking_duration} seconds. Departing...")

            #send departure message
            departure_msg = Message(to=self.agent.parked_slot_jid)
            departure_msg.set_metadata("performative", "inform")
            departure_msg.body = json.dumps({"type": "confirm_departure", "car": str(self.agent.jid)})
            self.agent.location = self.agent.park_position
            
            await self.send(departure_msg)
            self.set_next_state("DEPARTED")
            
    class DepartedState(State):
        async def run(self):
            print(f"[{self.agent.jid}] Car has departed from parking slot.")
            
            # Reset parked and best slot information
            self.agent.parked_slot_jid = None   
            self.agent.best_slot_jid = None
            
            self.agent.location = self.agent.find_path_to_park(self.agent.location)
            
            # Set a new random goal location
            self.agent.goal_position = get_random_location()
            print(f"[{self.agent.jid}] New goal location: {self.agent.goal_position}")
            
            # Update path to the new goal
            print(f"[{self.agent.jid}] Current location: {self.agent.location}")
            self.agent.find_path()
            print(f"[{self.agent.jid}] New path: {self.agent.path}")
            
            # Transition to DRIVE state
            self.set_next_state("DRIVE")
       
            

    async def setup(self):
        print(f"[{self.jid}] CarAgent starting...")
        fsm = FSMBehaviour()

        # Add States
        fsm.add_state(name="DRIVE", state=self.DriveState(), initial=True)
        fsm.add_state(name="SEARCH_AND_WAIT", state=self.SearchAndWaitState())
        fsm.add_state(name="CONFIRM_PARKING", state=self.ConfirmParkingState())
        fsm.add_state(name="PARKED", state=self.ParkedState())
        fsm.add_state(name="DEPARTED", state=self.DepartedState())
        fsm.add_state(name="DRIVETOPARK", state=self.DriveToParkState())
        
        # Add Transitions
        fsm.add_transition(source="DRIVE", dest="SEARCH_AND_WAIT")
        fsm.add_transition(source="DRIVE", dest="DRIVE")
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="CONFIRM_PARKING")
        fsm.add_transition(source="CONFIRM_PARKING", dest="SEARCH_AND_WAIT")
        fsm.add_transition(source="DRIVETOPARK", dest="PARKED")
        fsm.add_transition(source="CONFIRM_PARKING", dest="DRIVETOPARK")
        fsm.add_transition(source="PARKED", dest="DEPARTED")
        fsm.add_transition(source="DEPARTED", dest="DRIVE")
        fsm.add_transition(source="DRIVETOPARK", dest="DRIVETOPARK")

        # Add self-referencing transition
        fsm.add_transition(source="SEARCH_AND_WAIT", dest="SEARCH_AND_WAIT")

        self.add_behaviour(fsm)


async def main():
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Road Simulation")
    clock = pygame.time.Clock()
    
    car_agent_1 = CarAgent("car1@localhost", "car1", shedule={"target_location": (25,26), "parking_duration": 10}, screen=screen, start_position=(1,1))
    car_agent_2 = CarAgent("car2@localhost", "car2", shedule={"target_location": (19,22), "parking_duration": 15}, screen=screen, start_position=(20,1))
    car_agent_3 = CarAgent("car3@localhost", "car3", shedule={"target_location": (25, 2), "parking_duration": 20}, screen=screen, start_position=(1,4))
    
    
    await car_agent_1.start()
    await car_agent_2.start()
    await car_agent_3.start()
    
    try:
        while True:
            await asyncio.sleep(0.001)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()    
            screen.fill(WHITE)
            for row in range(len(ROAD_MAP)):
                for col in range(len(ROAD_MAP[row])):
                    if ROAD_MAP[row][col] == 1:
                        pygame.draw.rect(screen, GRAY, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    elif ROAD_MAP[row][col] == 2:
                        pygame.draw.rect(screen, GREEN, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    else:
                        pygame.draw.rect(screen, BLACK, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            car_agent_1.update()
            car_agent_2.update()
            car_agent_3.update()
            
            car_agent_1.draw()
            car_agent_2.draw()     
            car_agent_3.draw()    
            pygame.display.flip()     
            clock.tick(60)
    except KeyboardInterrupt:
        print("Stopping agents...")
        pygame.quit()
        sys.exit()
    
    await car_agent_1.stop()
    await car_agent_2.stop()
    await car_agent_3.stop()

    
if __name__ == "__main__":
    asyncio.run(main())


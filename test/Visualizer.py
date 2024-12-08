import pygame
import sys
from collections import deque

# Initialize pygame
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
    [1, 0, 1, 1, 1, 0, 1, 2, 1, 0, 1, 1, 1, 0, 1, 2, 1, 0, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 2, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 2, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1],
    [1, 2, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 0, 1],
    [1, 0, 1, 1, 2, 1, 1, 1, 2, 1, 1, 0, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 0, 1],
    [1, 0, 2, 1, 2, 1, 1, 0, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 1, 2, 1, 1, 0, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 0, 1],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]



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

# Car class
class Car:
    def __init__(self, start_position):
        self.grid_position = start_position
        self.park_position = None
        self.goal_position = None
        self.path = []
        self.speed = 1  # Number of pixels to move per frame
        self.target_index = 0  # Index of next target in the path

    def set_path(self, new_path):
        self.path = new_path
        self.target_index = 1

    def update(self):
        print(self.path)
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

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

    def initialize_rect(self):
        start_x, start_y = grid_to_pixel(*self.grid_position)
        self.rect = pygame.Rect(start_x + 5, start_y + 5, GRID_SIZE - 10, GRID_SIZE - 10)
    def find_path(self):
        path = bfs(self.grid_position, self.goal_position, ROAD_MAP)
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
        else:
            self.path = bfs(self.grid_position, (nr, nc), ROAD_MAP)
            if self.path:
                self.set_path(self.path)
            else:
                print("No path found!")
            
# Main function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Road Simulation")
    clock = pygame.time.Clock()

    # Starting and goal positions (grid)
    start_position = (1, 1)
    goal_position = (25, 26)

    # Create car
    car = Car(start_position)
    car.initialize_rect()
    car.set_goal_position((25, 26))
    car.find_path()
    
    car2 = Car((20, 1))
    car2.initialize_rect()
    car2.set_goal_position((20, 17))
    car2.find_path()


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw road map
        screen.fill(WHITE)
        for row in range(len(ROAD_MAP)):
            for col in range(len(ROAD_MAP[row])):
                if ROAD_MAP[row][col] == 1:
                    pygame.draw.rect(screen, GRAY, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                elif ROAD_MAP[row][col] == 2:
                    pygame.draw.rect(screen, GREEN, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                else:
                    pygame.draw.rect(screen, BLACK, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Update and draw car
        car.update()
        car2.update()
        # print car position
        print(f"Car position: {car.grid_position}")
        car.draw(screen)
        car2.draw(screen)

        # Draw goal
        # goal_x, goal_y = grid_to_pixel(*goal_position)
        # goal_x_2, goal_y_2 = grid_to_pixel(car2.goal_position[0], car2.goal_position[1])
        # pygame.draw.rect(screen, RED, (goal_x + 5, goal_y + 5, GRID_SIZE - 10, GRID_SIZE - 10))
        # pygame.draw.rect(screen, GREEN, (goal_x_2 + 5, goal_y_2 + 5, GRID_SIZE - 10, GRID_SIZE - 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

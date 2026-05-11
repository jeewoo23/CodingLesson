import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
WORLD_SIZE = 3000  # The total map size
FPS = 60
SNAKE_SPEED = 4
TURN_SPEED = 5
SEGMENT_DISTANCE = 15  # Distance between body segments

class Snake:
    def __init__(self, x, y, color, is_ai=False):
        self.segments = [[x, y]]
        self.length = 5
        self.color = color
        self.angle = random.randint(0, 360)
        self.is_ai = is_ai
        self.alive = True

    def update(self, target_angle=None):
        if not self.alive: return

        # AI Steering Logic
        if self.is_ai:
            # Simple AI: Jitter the angle or follow food (logic can be expanded)
            self.angle += random.uniform(-5, 5)
        elif target_angle is not None:
            # Smoothly rotate towards mouse
            angle_diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += max(min(angle_diff, TURN_SPEED), -TURN_SPEED)

        # Move Head
        head_x = self.segments[0][0] + math.cos(math.radians(self.angle)) * SNAKE_SPEED
        head_y = self.segments[0][1] + math.sin(math.radians(self.angle)) * SNAKE_SPEED
        self.segments.insert(0, [head_x, head_y])

        # Keep segments at specific intervals
        if len(self.segments) > self.length * (SEGMENT_DISTANCE // SNAKE_SPEED):
            self.segments.pop()

    def draw(self, surface, camera_offset):
        for i, (x, y) in enumerate(self.segments):
            # Only draw every Nth coordinate to space out segments
            if i % (SEGMENT_DISTANCE // SNAKE_SPEED) == 0:
                pygame.draw.circle(surface, self.color, 
                                   (int(x - camera_offset[0]), int(y - camera_offset[1])), 10)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # World Objects
    player = Snake(WORLD_SIZE//2, WORLD_SIZE//2, (0, 255, 0))
    ais = [Snake(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), 
                 (random.randint(50,255), 0, 0), is_ai=True) for _ in range(10)]
    
    food = [[random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE)] for _ in range(100)]

    running = True
    while running:
        screen.fill((30, 30, 30))
        
        # 1. Handle Input
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (SCREEN_WIDTH // 2)
        dy = mouse_y - (SCREEN_HEIGHT // 2)
        target_angle = math.degrees(math.atan2(dy, dx))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update Snakes
        player.update(target_angle)
        for ai in ais:
            ai.update()

        # 3. Camera System (Center on Player)
        camera_offset = [player.segments[0][0] - SCREEN_WIDTH // 2, 
                         player.segments[0][1] - SCREEN_HEIGHT // 2]

        # 4. Collision & Food Logic
        head = player.segments[0]
        for f in food[:]:
            dist = math.hypot(head[0] - f[0], head[1] - f[1])
            if dist < 20:
                player.length += 1
                food.remove(f)
                food.append([random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE)])

        # 5. Draw Everything
        for f in food:
            pygame.draw.circle(screen, (255, 255, 0), 
                               (int(f[0] - camera_offset[0]), int(f[1] - camera_offset[1])), 5)
        
        for ai in ais:
            ai.draw(screen, camera_offset)
        player.draw(screen, camera_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
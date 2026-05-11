import pygame
import random

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
LAVA = (255, 69, 0)

# Physics constants
# Using $g$ for gravity and $v_y$ for jump velocity
GRAVITY = 0.8
JUMP_STRENGTH = -12

class Player:
    def __init__(self):
        self.size = 30
        self.x = 100
        self.y = SCREEN_HEIGHT - self.size - 50
        self.vel_y = 0
        self.is_jumping = False
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True

    def update(self):
        # Apply Gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Floor Collision (Simple)
        floor_y = SCREEN_HEIGHT - 50
        if self.y + self.size > floor_y:
            self.y = floor_y - self.size
            self.vel_y = 0
            self.is_jumping = False
        
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, CYAN, self.rect)

class Obstacle:
    def __init__(self, x):
        self.width = 30
        self.height = 40
        self.x = x
        self.y = SCREEN_HEIGHT - 50 - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 6

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, surface):
        # Drawing a triangle (spike)
        points = [
            (self.x, self.y + self.height),
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, LAVA, points)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Dash")
    clock = pygame.time.Clock()

    player = Player()
    obstacles = []
    spawn_timer = 0
    score = 0
    font = pygame.font.SysFont("Arial", 24)

    running = True
    while running:
        screen.fill(BLACK)
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()

        # 2. Spawning Obstacles
        spawn_timer += 1
        if spawn_timer > random.randint(60, 120):
            obstacles.append(Obstacle(SCREEN_WIDTH))
            spawn_timer = 0

        # 3. Updates
        player.update()
        for obs in obstacles[:]:
            obs.update()
            # Remove off-screen obstacles
            if obs.x < -obs.width:
                obstacles.remove(obs)
                score += 1
            
            # Collision Detection
            if player.rect.colliderect(obs.rect):
                print(f"Game Over! Final Score: {score}")
                running = False

        # 4. Drawing
        # Draw Floor
        pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT-50), (SCREEN_WIDTH, SCREEN_HEIGHT-50), 2)
        
        player.draw(screen)
        for obs in obstacles:
            obs.draw(screen)

        # Draw Score
        score_txt = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_txt, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
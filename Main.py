import pygame
import math
import random

# Constants
FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Player Class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 5
        self.vision_radius = 100
        self.vision_angle = math.pi / 4  # 45 degrees

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(0, min(SCREEN_WIDTH, self.x))  # Keep player on screen
        self.y = max(0, min(SCREEN_HEIGHT, self.y))

    def rotate(self, d_angle):
        self.angle += d_angle
        self.angle %= 2 * math.pi  # Keep angle within 0-2π

    def draw(self, surface):
        # Draw vision cone
        self.draw_vision_cone(surface)
        # Draw player
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), 10)

    def draw_vision_cone(self, surface):
        vision_points = []
        for i in range(-15, 16, 1):
            angle = self.angle + math.radians(i)
            x = self.x + self.vision_radius * math.cos(angle)
            y = self.y + self.vision_radius * math.sin(angle)
            vision_points.append((x, y))
        pygame.draw.polygon(surface, WHITE, [(self.x, self.y)] + vision_points)

# Enemy Class
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.patrol_points = [(x, y), (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))]
        self.current_patrol_index = 0
        self.speed = 2

    def update(self, player):
        if self.detect_player(player):
            self.chase_player(player)
        else:
            self.patrol()

    def patrol(self):
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        if abs(self.x - target_x) < 5 and abs(self.y - target_y) < 5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            dx = target_x - self.x
            dy = target_y - self.y
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

    def detect_player(self, player):
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        if distance < 100:
            angle_to_player = math.atan2(player.y - self.y, player.x - self.x)
            if abs(angle_to_player - self.x) < player.vision_angle / 2:
                return True
        return False

    def chase_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.atan2(dy, dx)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 10)

# Game Class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.enemies = [Enemy(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(5)]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            self.player.move(dx, dy)

            self.screen.fill(BLACK)
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.update(self.player)
                enemy.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
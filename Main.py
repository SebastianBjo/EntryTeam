import arcade
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("player.png")  # Add your player image
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.angle = 0

class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("enemy.png")  # Add your enemy image
        self.center_x = x
        self.center_y = y

class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "CQB Tactical Shooter")
        self.player = Player()
        self.enemies = arcade.SpriteList()

    def setup(self):
        # Setup enemies
        for i in range(3):
            enemy = Enemy(100 * (i + 1), 100)
            self.enemies.append(enemy)

    def on_draw(self):
        arcade.start_render()
        self.player.draw()
        self.enemies.draw()

    def on_update(self, delta_time):
        self.handle_movement()

    def handle_movement(self):
        # Smooth WASD movement
        if arcade.key.W in self.pressed_keys:
            self.player.change_y = 5
        elif arcade.key.S in self.pressed_keys:
            self.player.change_y = -5
        else:
            self.player.change_y = 0

        if arcade.key.A in self.pressed_keys:
            self.player.change_x = -5
        elif arcade.key.D in self.pressed_keys:
            self.player.change_x = 5
        else:
            self.player.change_x = 0

        self.player.update()

    def on_key_press(self, key, modifiers):
        self.pressed_keys.add(key)

    def on_key_release(self, key, modifiers):
        self.pressed_keys.discard(key)

if __name__ == '__main__':
    game = Game()
    arcade.run()
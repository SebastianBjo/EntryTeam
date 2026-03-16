import arcade
import math
import random

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "CQB Tactical Shooter"

PLAYER_SPEED = 3
BULLET_SPEED = 10
VISION_CONE_ANGLE = 60
VISION_CONE_LENGTH = 200

ROOM_COLOR = arcade.color.DARK_SLATE_GRAY
FOG_COLOR = arcade.color.BLACK
MEMORY_COLOR = arcade.color.DIM_GRAY

# --- Classes ---


class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("player_sprite.png", scale=0.5)
        self.center_x = x
        self.center_y = y
        self.angle = 0
        self.change_x = 0
        self.change_y = 0
        self.bullets = arcade.SpriteList()
        self.alive = True

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        # Keep inside screen
        self.center_x = max(0, min(SCREEN_WIDTH, self.center_x))
        self.center_y = max(0, min(SCREEN_HEIGHT, self.center_y))


class Bullet(arcade.Sprite):
    def __init__(self, x, y, angle):
        super().__init__("bullet.png", scale=0.2)
        self.center_x = x
        self.center_y = y
        self.angle = angle
        rad = math.radians(angle)
        self.change_x = math.cos(rad) * BULLET_SPEED
        self.change_y = math.sin(rad) * BULLET_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (
            self.center_x < 0
            or self.center_x > SCREEN_WIDTH
            or self.center_y < 0
            or self.center_y > SCREEN_HEIGHT
        ):
            self.kill()


class Enemy(arcade.Sprite):
    def __init__(self, x, y, patrol_points=None):
        super().__init__("enemy_sprite.png", scale=0.5)
        self.center_x = x
        self.center_y = y
        self.angle = 0
        self.patrol_points = patrol_points or [(x, y)]
        self.current_point = 0
        self.speed = 1.5
        self.detect_range = 150
        self.alive = True

    def update(self, player):
        if not self.alive:
            return
        # Simple AI: check for player in range
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance < self.detect_range:
            self.angle = math.degrees(math.atan2(dy, dx))
            self.center_x += math.cos(math.radians(self.angle)) * self.speed
            self.center_y += math.sin(math.radians(self.angle)) * self.speed
        else:
            # Patrol
            target = self.patrol_points[self.current_point]
            dx = target[0] - self.center_x
            dy = target[1] - self.center_y
            if math.hypot(dx, dy) < 5:
                self.current_point = (self.current_point + 1) % len(self.patrol_points)
            else:
                self.angle = math.degrees(math.atan2(dy, dx))
                self.center_x += math.cos(math.radians(self.angle)) * self.speed
                self.center_y += math.sin(math.radians(self.angle)) * self.speed


class Wall(arcade.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__("wall_texture.png")
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height


class Door(arcade.Sprite):
    def __init__(self, x, y, width, height, open=False):
        super().__init__("door_texture.png")
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.open = open

    def interact(self):
        self.open = not self.open


# --- Main Game Class ---


class CQBGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        # Sprites
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.door_list = arcade.SpriteList()
        self.visible_memory = {}  # map memory system

        # Player
        self.player = Player(100, 100)
        self.player_list.append(self.player)

        # Map setup
        self.setup_map()

        # Victory/Defeat
        self.game_over = False
        self.victory = False

    def setup_map(self):
        # Rooms: walls
        self.wall_list.append(Wall(300, 300, 50, 200))
        self.wall_list.append(Wall(600, 500, 100, 50))

        # Doors
        self.door_list.append(Door(300, 400, 40, 10))

        # Enemies with patrol points
        self.enemy_list.append(Enemy(400, 400, patrol_points=[(400, 400), (500, 400)]))
        self.enemy_list.append(Enemy(700, 300, patrol_points=[(700, 300), (750, 350)]))

    # --- Vision System ---
    def is_in_vision_cone(self, x, y):
        dx = x - self.player.center_x
        dy = y - self.player.center_y
        angle_to_obj = math.degrees(math.atan2(dy, dx))
        angle_diff = (angle_to_obj - self.player.angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360
        distance = math.hypot(dx, dy)
        return abs(angle_diff) < VISION_CONE_ANGLE / 2 and distance < VISION_CONE_LENGTH

    # --- Drawing ---
    def on_draw(self):
        arcade.start_render()

        # Draw memory/fog
        for wall in self.wall_list:
            arcade.draw_rectangle_filled(
                wall.center_x,
                wall.center_y,
                wall.width,
                wall.height,
                MEMORY_COLOR,
            )

        for door in self.door_list:
            arcade.draw_rectangle_filled(
                door.center_x,
                door.center_y,
                door.width,
                door.height,
                MEMORY_COLOR,
            )

        # Draw player
        self.player.draw()

        # Draw bullets
        self.player.bullets.draw()

        # Draw enemies if in vision
        for enemy in self.enemy_list:
            if enemy.alive and self.is_in_vision_cone(enemy.center_x, enemy.center_y):
                enemy.draw()

        # Draw vision cone
        self.draw_vision_cone()

        # Draw victory/defeat messages
        if self.game_over:
            arcade.draw_text(
                "VICTORY" if self.victory else "DEFEAT",
                SCREEN_WIDTH / 2 - 100,
                SCREEN_HEIGHT / 2,
                arcade.color.RED,
                50,
            )

    def draw_vision_cone(self):
        arcade.draw_arc_filled(
            self.player.center_x,
            self.player.center_y,
            VISION_CONE_LENGTH * 2,
            VISION_CONE_LENGTH * 2,
            arcade.color.LIGHT_YELLOW + (100,),
            self.player.angle - VISION_CONE_ANGLE / 2,
            self.player.angle + VISION_CONE_ANGLE / 2,
        )

    # --- Update ---
    def on_update(self, delta_time):
        if self.game_over:
            return

        # Player update
        self.player.update()
        self.player.bullets.update()

        # Enemy update
        for enemy in self.enemy_list:
            enemy.update(self.player)

        # Bullet collision
        for bullet in self.player.bullets:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            for enemy in hit_list:
                enemy.alive = False
                bullet.kill()

        # Check player death
        for enemy in self.enemy_list:
            if enemy.alive and self.is_in_vision_cone(self.player.center_x, self.player.center_y):
                # Simple hit detection
                distance = math.hypot(enemy.center_x - self.player.center_x, enemy.center_y - self.player.center_y)
                if distance < 15:
                    self.player.alive = False
                    self.game_over = True
                    self.victory = False

        # Victory check
        if all(not enemy.alive for enemy in self.enemy_list):
            self.game_over = True
            self.victory = True

    # --- Controls ---
    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.S:
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.E:
            # Interact doors
            for door in self.door_list:
                if math.hypot(self.player.center_x - door.center_x, self.player.center_y - door.center_y) < 50:
                    door.interact()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        if key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self.player.angle = math.degrees(math.atan2(y - self.player.center_y, x - self.player.center_x))

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.player.alive:
            self.player.bullets.append(Bullet(self.player.center_x, self.player.center_y, self.player.angle))


# --- Run the Game ---
if __name__ == "__main__":
    game = CQBGame()
    arcade.run()

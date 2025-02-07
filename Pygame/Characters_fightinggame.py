import pygame

class Character:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.scale = (100, 100)
        self.sprite = self.load_sprite()

        self.max_health = 100
        self.current_health = self.max_health
        self.health_bar_width = 100
        self.health_bar_height = 10

        self.velocity_y = 0
        self.velocity_x = 0
        self.is_jumping = False
        self.move_speed = 5
        self.jump_force = -15
        self.gravity = 0.8
        self.ground_y = 900
        self.on_platform = False
        self.is_dead = False
        self.death_y = 700

        self.rect = pygame.Rect(x - self.scale[0]//2, y - self.scale[1], self.scale[0], self.scale[1])

    def load_sprite(self):

        character_colors = {
            'Lucario': (0, 0, 255),
            'Mewtwo': (255, 0, 255),
            'Zeraora': (255, 255, 0),
            'Cinderace': (255, 0, 0)
        }

        try:
            sprite_path = f"sprites/{self.name.lower()}_sprite.png"
            img = pygame.image.load(sprite_path).convert_alpha()
            return pygame.transform.scale(img, self.scale)

        except Exception as e:
            print(f"Error loading sprite for {self.name}: {str(e)}")

            surface = pygame.surface.Surface(self.scale)
            color = character_colors.get(self.name, (255, 0, 0))
            surface.fill(color)
            return surface

    def check_platform_collision(self, platforms):

        self.rect.x = self.x - self.scale[0]//2
        self.rect.y = self.y - self.scale[1]

        for platform in platforms:
            if self.rect.right >= platform.x and self.rect.left <= platform.x + platform.width:
                if self.rect.bottom >= platform.y and self.rect.bottom <= platform.y + 20:
                    self.y = platform.y
                    self.velocity_y = 0
                    self.is_jumping = False
                    self.on_platform = True
                    return True
        return False

    def draw_health_bar(self, screen):
        bar_x = self.x - self.health_bar_width // 2
        bar_y = self.y - self.scale[1] - 20

        pygame.draw.rect(screen, (255, 0, 0),
                         (bar_x, bar_y, self.health_bar_width, self.health_bar_height))

        health_width = (self.current_health / self.max_health) * self.health_bar_width
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0),
                             (bar_x, bar_y, health_width, self.health_bar_height))

        pygame.draw.rect(screen, (0, 0, 0),
                         (bar_x, bar_y, self.health_bar_width, self.health_bar_height), 1)

    def check_death(self):
        if self.y > self.death_y:
            self.is_dead = True
            self.current_health = 0
            return True
        return False

    def move(self, keys, platforms):
        #forward and backward movement
        if keys[pygame.K_LEFT]:
            self.x -= self.move_speed
        elif keys[pygame.K_RIGHT]:
            self.x += self.move_speed
        else:
            self.velocity_x = 0

        self.x += self.velocity_x

        #jumping
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_force
            self.is_jumping = True
            self.on_platform = False

        #gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        if not self.check_platform_collision(platforms):
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.velocity_y = 0
                self.is_jumping = False
                self.on_platform = True

        #screen boundaries
        self.x = max(50, min(self.x, 950))

        self.check_death()

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x - self.sprite.get_width()//2,
                                      self.y - self.sprite.get_height()))
            self.draw_health_bar(screen)


class CharacterManager:
    def __init__(self):
        self.current_character = None

    def set_character(self, character_name):
        character_x = 500
        character_y = 580
        self.current_character = Character(character_name, character_x, character_y)

    def update(self, keys, platforms):
        if self.current_character:
            self.current_character.move(keys, platforms)

    def draw(self, screen):
        if self.current_character:
            self.current_character.draw(screen)
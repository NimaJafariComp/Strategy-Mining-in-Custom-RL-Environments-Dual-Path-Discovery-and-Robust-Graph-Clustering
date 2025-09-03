import pygame

# Base Interactable class
class Interactable(pygame.sprite.Sprite):
    def __init__(self, x, y, image, color, name):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.name = name
        self.color = color
        self.rect.topleft = (x, y)

    def interact(self, player, selected_item):
        """
        Base interact method. Override in subclasses for specific behavior.
        """
        pass

# Class-level attributes for images
class Door(Interactable):
    open_door_image = pygame.image.load("openDoor.png").convert_alpha()
    open_door_image = pygame.transform.smoothscale(open_door_image, (40, 40))

    def __init__(self, x, y, image, color, name):
        super().__init__(x, y, image, color, name)
        self.is_open = False

    def interact(self, player, selected_item):
        #if selected_item.name == "key" and selected_item.color == self.color:
        print(f"{self.color} Door unlocked! with {selected_item.color} {selected_item.name}")
        self.is_open = True
        self.image = Door.open_door_image
        player.inventory.remove(selected_item)
        return True  # Interaction successful

class Rock(Interactable):

    def __init__(self, x, y, image, color, name):
        super().__init__(x, y, image, color, name)

    def interact(self, player, selected_item):
        #if selected_item.name == "explosive" and selected_item.color == self.color:
        print(f"{self.color} Rock {self.name} destroyed with {selected_item.color} explosive!")
        player.inventory.remove(selected_item)
        self.kill()  # Remove the rock from the game
        return True  # Interaction successful


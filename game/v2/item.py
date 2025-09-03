import pygame

# Base Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, image, name, weight, color):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = name
        self.color = color
        self.weight = weight  # Set the weight of the item

# Key class inherits from Item
class Key(Item):
    
    def __init__(self, x, y, image, name, weight, color):
        super().__init__(x, y, image, name, weight, color)

# Explosive class inherits from Item
class Explosive(Item):

    def __init__(self, x, y, image, name, weight, color):
        super().__init__(x, y, image, name, weight, color)

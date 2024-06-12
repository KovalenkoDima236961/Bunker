# abilities.py
from main.models import Inventory, Player
import random


# abilities.py
def change_inventory_randomly(player, ability_code):
    if not player.abilities.filter(code=ability_code).exists():
        return False

    # Assuming Inventory is a model with inventory items
    inventory_items = list(Inventory.objects.all())
    if inventory_items:
        new_inventory = random.choice(inventory_items)
        player.inventory = new_inventory
        player.save()
        return True
    return False

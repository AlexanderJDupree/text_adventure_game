# file: text_game.py
# description: text game
# authors: Jacob Bickle, Alex DuPree
# date: 11/17/2017
# compiler: Python 3.6

"""
    11/23/2017

    *Re-implemented original get_input function into combat and main game loop. The get_input receives a action list when called and only executes action if user
    input is in the action list. The action list is also updated with the current
    room special actions. This prevents the user from entering 'run_action' and
    blowing the stack. As well as stops the user from calling the fight function
    anywhere in the game map. Separating our input into a different function really
    simplifies and prevents errors later in the code.

    * Enemies now drop loot at the end of combat. Loot is auto-picked up by the
    player

    * On failed run away attempts the enemy will now take a free turn. instead of
    a flat -10 damage to player.

    * Changed the while loops from while True to while player.health > 0:
    this allows the keypad function to terminate if the player dies.

    * Need to make death method functional and dynamic

    * Need to populate game_start.txt with actual game text

    * Need to create a tutorial or readme.txt file for game

    * Look into saving game state

    *condense object grabbing in the action methods into a separate method for ease of use.

    *Look into creating convenience methods for lines of code I reuse alot.
"""
import csv
import textwrap
import time

from random import randint


class Players:
    """Initializes player class with attributes"""

    player_objects = []

    def __init__(self, name='', health=100, dignity=1):
        self.name = name
        self.health = health
        self.equipped_weapon = None
        self.inventory = Players.initialize_inventory(name)
        self.equipped_weapon = Players.initial_equip(name)
        self.dignity = dignity  # Haven't found a use for this attribute yet.
        self.current_room = None
        self.player_objects.append(self)

    def read_inventory(self):
        print("\nInventory:\n====================")
        for item in self.inventory:
            print(item.name.capitalize(), 'x', item.uses)
        print("====================\n")

    def add_item(self, item):
        if item.name in [i.name for i in self.inventory]:
            player_item = [i for i in self.inventory if item.name == i.name]
            player_item[0].uses += 1
        else:
            self.inventory.append(item)
            if item in Weapons.weapon_objects:
                self.equip_weapon(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def equip_weapon(self, item):
        print("\nEquip {}? (yes or no)".format(item.name))
        opt = input(">  ")
        if opt[0].lower() in ('y', 'yes'):
            self.equipped_weapon = item
            print("You equipped {}!\n".format(item.name))
        else:
            print("\n{} remains unequipped.".format(item.name))

    # Can still use ACTION commands outside of combat. FIXED 11/23/2017
    def combat(self, enemy):
        action_list = ['fight', 'use', 'run', 'cry']

        print("\nYou entered combat with {}.".format(enemy.name))
        time.sleep(.5)

        while self.health > 0 and enemy.health > 0:
            print("\nActions:")
            for action in action_list:
                if action == 'use':
                    print('\t' + action.capitalize(), '(item)')
                else:
                    print('\t' + action.capitalize())
            opt = get_input("\n>  ", self.current_room, action_list)
            if opt[0] == 'run':
                if self.run_away(enemy) == True:
                    self.current_room.next_room(self.current_room.branches[0])
                    break
            else:
                action = Actions(opt[0], opt[1:])
                action.run_action()
                enemy.enemy_turn()
        if self.health > 0 and enemy.health <= 0:
            print("\nCongratulations! You defeated {}".format(enemy.name))
            loot = enemy.inventory[randint(1, len(enemy.inventory) - 1)]
            time.sleep(1)
            print("{} dropped a {}".format(enemy.name, loot.name))
            self.add_item(loot)
            self.current_room.enemies = None
            self.current_room.events = 'None'
            Players.player_objects.remove(enemy)
            del enemy
        if self.health <= 0:
            print("\nYou were deafeated by {}".format(enemy.name))
            death("GAME OVER")

    def run_away(self, enemy):
        # Must roll above a 85 to run away
        print("Running away!. . . .")
        time.sleep(1)
        if randint(1, 100) > 85:
            print("\nYou ran away!")
            time.sleep(1)
            return True
        else:
            print("\nYou failed to run away!")
            time.sleep(1)
            enemy.enemy_turn()
            return False

    @classmethod
    def get_player(cls, name):
        for p in cls.player_objects:
            if name == p.name:
                return p

    @classmethod
    def initialize_inventory(cls, name):
        item_list = parse_file('game_start.txt', name, '*player_inventory')
        inventory = []
        for i in item_list:
            i = eval_item(i)
            inventory.append(i)
        return inventory

    @classmethod
    def initial_equip(cls, name):
        item_list = parse_file('game_start.txt', name, '*player_inventory')
        for i in item_list:
            for w in Weapons.weapon_objects:
                if i == w.name:
                    return w


class Enemy(Players):
    """Creates enemy object for use in story"""

    def __init__(self, name='', health=100, dignity=1):
        super().__init__(name, health)

    def enemy_turn(self):
        if self.health <= 0:
            print("\nThe {} was killed!".format(self.name))
        else:
            player = Players.get_player('player')
            weapon = self.equipped_weapon
            accuracy_roll = weapon.acc + randint(1, 100)
            print("\n{}'s turn!. . . . ".format(self.name), end='')
            time.sleep(2)
            # Add a roll to for enemy to run away
            print("\nThe {} attacks!".format(self.name))
            time.sleep(1)
            if accuracy_roll > 100:
                if accuracy_roll > 85 + weapon.acc:
                    print("\nCritical hit!!! The {} hit you for {} damage".format(
                        self.name, int(weapon.dmg * 1.5)))
                    player.health -= int(weapon.dmg * 1.5)
                else:
                    damage_roll = weapon.dmg + randint(-5, 5)
                    print("\nOuch! The {} hit you for {} damage".format(
                        self.name, damage_roll))
                    player.health -= damage_roll
            else:
                print("\nYou nimbly dodge out of the way!")
            time.sleep(1)
            print("You have {}/100 health remaining".format(player.health))


class Room:
    """Initializes room object, attributes are pulled from text file"""

    room_objects = []

    def __init__(self, room_title=''):
        keywords = ['*room_descriptions', '*room_branches', '*room_count',
                    '*room_events', '*room_items', '*room_actions',
                    '*room_lock_description', '*room_enemies']
        attributes = [parse_file('game_start.txt', room_title, target)
                      for target in keywords]
        self.name = room_title
        self.description = attributes[0]  # list of descriptions
        self.branches = attributes[1]   # list of branches
        self.counter = int(attributes[2][0])  # int
        self.events = attributes[3][0]  # string
        self.items = [eval_item(name) for name in attributes[4]]  # list comp
        self.actions = attributes[5]  # list
        self.lock_description = attributes[6]  # list
        if attributes[7][0] == 'None':  # Prevents game from using Nonetype to make
            self.enemies = None        # enemies
        else:
            self.enemies = Enemy(
                name=attributes[7][0], health=int(attributes[7][1]))
        self.room_objects.append(self)

    def enter_room(self):
        player = Players.get_player('player')
        player.current_room = self
        if self.lock_description[0] == 'True':
            print('\n' + textwrap.fill(
                self.description[int(self.lock_description[1])]))
        else:
            try:
                print(
                    '\n' + textwrap.fill(self.description[self.counter]))
            except IndexError:
                print('\n' + textwrap.fill(self.description[-1]))
            self.increment_counter()
            eval(self.events)

    def encounter(self):
        player = Players.get_player('player')
        player.combat(self.enemies)

    def next_room(self, room_title=''):
        room = Room.get_room(room_title)
        room.enter_room()

    def increment_counter(self):
        self.counter += 1

    def keypad(self):  # Need to implement death
        player = Players.get_player("player")
        code = "6824"
        while player.health > 0:
            player_attempt = input(
                "Enter code (type \"back\" to back out):\n>  ")
            if player_attempt == code:
                self.next_room('boss_room')
                break
            elif player_attempt.lower() == "back":
                self.next_room(self.branches[0])
                break
            elif player_attempt.isnumeric():
                print(
                    "\nYouch! That felt just about as good as an electrical"
                    " shock shooting throughout your body could.")
                player.health -= 25
            else:
                print("\nThe keypad lets out a quizical beep. (Invalid input)")
        print("\nThat was stupid, death by keypad")
        death("GAME OVER")

    @classmethod
    def get_room(cls, name):
        for r in cls.room_objects:
            if name == r.name:
                return r


class Actions:
    """creates object with users string to run a function"""

    def __init__(self, verb="", *args):
        self.verb = verb
        self.args = [arg for a in args for arg in a]

    def run_action(self):
        try:
            eval('self.' + self.verb + '()')
        except AttributeError:
            print("\nHuh? (Invalid input. Type \"help\" for help)")

    def help(self):
        player = Players.get_player('player')
        special_actions = player.current_room.actions[0]
        print(textwrap.dedent(
            """
            Here is a list of commands:
            ==================================================

            goto, examine, use, pickup, inventory, equip, quit

            ==================================================

            Special commands for this room: {}
            """.format(special_actions)))

    def goto(self):
        player = Players.get_player('player')
        current_room = player.current_room
        if len(self.args) == 0:
            print("Go where?")
        else:
            if self.args[0] in current_room.branches:
                current_room.next_room(self.args[0])
            else:
                print("\n{} isn't an option".format(self.args[0]))

    def drink(self):
        if self.args[0] == 'water':
            print("\nYou drink the water, and immediately feel nauseous.")
            time.sleep(2)
            print("\nYou pass out and die.")
            death("GAME OVER")
        else:
            print("\nI don't understand drink '{}'".format(self.args[0]))

    @staticmethod
    def inventory():
        player = Players.get_player('player')
        player.read_inventory()

    def equip(self):
        player = Players.get_player('player')
        if self.args[0] not in [i.name for i in player.inventory]:
            print("\nThere is no {} to equip".format(self.args[0]))
        else:
            item = Items.get_item(self.args[0])
            if item == player.equipped_weapon:
                print("\n{} is already equipped.".format(item.name))
            elif item not in Weapons.weapon_objects:
                print("\nYou can't equip {}".format(item.name))
            else:
                player.equip_weapon(item)

    def pickup(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        current_room = player.current_room
        if item_name not in [i.name for i in current_room.items]:
            print("\nSorry, there is no {} here".format(item_name))
        else:
            room_item = [i for i in current_room.items if item_name == i.name]
            if item_name in [i.name for i in player.inventory]:
                print("\nYou picked up {}!".format(item_name))
                item = [i for i in player.inventory if item_name == i.name]
                item[0].uses += 1
                current_room.items.remove(room_item[0])
            elif room_item[0].pickup == 'False':
                print("\n{} cannot be picked up.".format(item_name))
            else:
                print("\nYou picked up {}!".format(item_name))
                player.add_item(room_item[0])
                current_room.items.remove(room_item[0])

    def examine(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        current_room = player.current_room
        if item_name in [i.name for i in player.inventory]:
            item = Items.get_item(item_name)
            item.examine_item()
        elif item_name in [i.name for i in current_room.items]:
            item = Items.get_item(item_name)
            item.examine_item()
        elif item_name == 'room':
            # Prints last description only
            print('\n' + current_room.description[-1])
        else:
            print("\nThere is no {} to examine".format(item_name))

    def use(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        if item_name in [i.name for i in player.inventory]:
            item = [i for i in player.inventory if item_name == i.name]
            item[0].use_item()
        else:
            print("\nThere is no {} to use".format(item_name))

    # BUG: Fixed by using original get_input method.
    def fight(self):
        # Grab needed objects
        player = Players.get_player('player')
        enemy = player.current_room.enemies
        weapon = player.equipped_weapon
        # Execute combat actions
        # Takes weapon accuracy from .txt file and adds a number 1-100 to it.
        accuracy_roll = weapon.acc + randint(1, 100)
        print("You attack!. . . .")
        time.sleep(1.5)
        if accuracy_roll > 100:  # Accuracy role must be over 100 to do anything.
            if accuracy_roll > 85 + weapon.acc:  # If the random number was 86-100, critical hit,
                print("\nCritical hit!!! You hit {} for {} damage"
                      .format(enemy.name, int(weapon.dmg * 1.5)))
                enemy.health -= int(weapon.dmg * 1.5)
            else:
                # Else, damage normal, give or take 5 from base weapon.
                damage_roll = weapon.dmg + randint(-5, 5)
                print("\nYou hit {} for {} damage".format(
                    enemy.name, damage_roll))
                enemy.health -= damage_roll
        else:
            print("\nYour attack misses!")
        print("{} has {} health remaining".format(enemy.name, enemy.health))
        time.sleep(1)

    def quit(self):
        print("\nAre you sure you want to quit? Nothing will be saved.")
        opt = input(">  ").lower()
        if opt in ('y', 'yes'):  # This prevents use from typing 'you' or any word
            quit()               # with 'y' and quitting the game.
        else:
            print("Returning to game.")


class Items:
    """Creates item object for use"""

    item_objects = []

    def __init__(self, item_name="", attributes=[]):
        self.name = item_name
        self.uses = int(attributes[0])
        self.func = attributes[1]
        self.pickup = attributes[2]
        self.description = attributes[-1]
        self.item_objects.append(self)

    def examine_item(self):
        print('\n' + self.description)

    def use_item(self):
        if self.uses > 0 and self.func != 'None':
            eval('self.' + self.func)
        else:
            print("\nYou can't use {} here".format(self.name))

    def decrement_uses(self):
        player = Players.get_player('player')
        self.uses -= 1
        if self.uses == 0:
            player.remove_item(self)
            self.item_objects.remove(self)
            del self

    def heal(self):
        player = Players.get_player('player')
        if player.health == 100:
            print("\nYou're not injured.")
        else:
            player.health += 25
            if player.health > 100:
                player.health = 100
            self.decrement_uses()
            print("\nYou healed yourself. You have {}/100 health".format(
                player.health))

    def light(self):
        player = Players.get_player('player')
        current_room = player.current_room
        if current_room.lock_description[0] == 'True':
            current_room.lock_description[0] = 'False'
            print("\nYou lit your {}".format(self.name))
            self.decrement_uses()
            current_room.increment_counter()
            current_room.enter_room()
        else:
            print("\nYou can't use that here")

    @classmethod
    def get_item(cls, name):
        for i in cls.item_objects:
            if name == i.name:
                return i


class Weapons(Items):
    """Creates weapons class, inherits from Items"""

    weapon_objects = []

    def __init__(self, item_name="", attributes=[]):
        super().__init__(item_name, attributes)
        self.dmg = int(attributes[3])
        self.acc = int(attributes[4])
        self.weapon_objects.append(self)


def main():
    # Initializes game world
    create_game_world('game_start.txt')
    player = Players('player')
    player.current_room = Room.get_room('start')
    player.current_room.enter_room()
    action_list = ['goto', 'pickup', 'examine',
                   'use', 'help', 'inventory', 'equip', 'quit']
    # Game loop
    while player.health > 0:
        opt = get_input(">  ", player.current_room, action_list)
        player_input = Actions(opt[0], opt[1:])
        player_input.run_action()


def get_input(prompt, current_room, option_list):
    try:
        action_list = option_list + current_room.actions
    except AttributeError:
        action_list = option_list
    while True:
        choice = input(prompt).split()
        try:
            if choice[0].lower() in action_list:
                choice = [s.lower() for s in choice]
                return choice
            else:
                print("\nSorry, I didn't understand. Type 'help' for help")
        except IndexError:
            print("\nSorry, I didn't understand. Type 'help' for help")


def create_game_world(filename):
    rooms = parse_file(filename, 'survival_game', '*rooms')
    for r in rooms:
        Room(r)


def eval_item(name):
    if name == 'None':
        return None
    else:
        attributes = parse_file('game_start.txt', name, '*items')
        if attributes == None:
            attributes = parse_file(
                'game_start.txt', name, '*weapons')
            return Weapons(name, attributes)
        else:
            return Items(name, attributes)


def parse_file(filename, key, target):
    descriptions = {}
    with open(filename, 'r') as f:
        file = (csv.reader(f, delimiter='|'))
        for i, row in enumerate(file):
            if target in row:
                start = i + 2
        f.seek(0, 0)
        for i, row in enumerate(file):
            if i >= start:
                try:
                    descriptions[row[0]] = [s.strip() for s in row[1:]]
                except IndexError:
                    break
        try:
            return descriptions[key]
        except KeyError:
            return None


# Need to fully implement death function
def death(message):
    print(message)
    quit()


main()

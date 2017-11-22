# file: text_game.py
# description: text game
# authors: Jacob Bickle, Alex DuPree
# date: 11/17/2017
# compiler: Python 3.6

"""
    * Game now instantiates ALL object for use and put them into the correct
        containers. I.e. Start room holds knife and bandage object. Right room
        hold wolf enemy object and no item objects etc. etc.

    * Because of this change I reworked most of the methods in the Action class,
    and the Room class to grab objects that already exist from their
    corresponding container. previously I would have to overwrite the rooom
    from the attribtues in the textGame.txt file. As well as create the items and
    enemy objects when the user interacted with them.

    * This change also negates the need for a seperate game.txt for file for
    parsing and grabbing attributes. So I got rid of the textGame.txt.

    * All attributes are pulled from the game_start.txt file now.

    *reworked Room class __init__ method again. on game start it will also
    instantiate any item and enemy objects it needs.

    * Combat loop is 99% done! Fight, use, run are all functional. I haven't
    implemented 'cry' yet. I was thinking that would affect players dignity
    attribute and print a funny message.

    * Combat uses time.sleep(n) to slow down the data and make it feel more engaging

    *Failed attempts at running away will now damage player

    * When combat is finished the enemy object is deleted from the game world.

    *I want to implement a small chance that on enemy turn the enemy will pass,
    or run away.

    *Maybe implement a defend or block option in the combat loop as well.

    * Fight has critical hit functionality as well

    * When player picks up a weapon, game will now ask the user if he wants to
    equip that weapon.

    *added equip() method in action class. Player can now equip whatever weapon
    they have in their inventory by typing 'equip (item)'

    *Add equip into combat action list?? So player can change weapons whenever.

    *Reworked the add_item() and pickup() methods. Now if you pickup an item
    you already have the game won't instantiate another item and add it to
    your inventory. Instead, it will increment the number of uses for your
    item.

    *Reworked the read_inventory() method in the Player class. Now it will
    print how many of each item is in the inventory. Like Bandages x 3.

    * Reworked the input function so it could be used for combat input as well

    *Fixed a bug in the input function, if player pressed enter without
    inputing any characters the game would crash.

    *Fixed a bug in the input function action list update. The action list
    would retain all the special room actions and combat actions even when
    combat was terminated.

    * Reworked room description printing to have use textwrapping

    * Need to create help function

    * Need to make death method functional and dynamic

    * Need to populate game_start.txt with actual game text

    * Need to create a tutorial or readme.txt file for game

    * Look into saving game state

    * I use 'if item in [i.name for i in player.inventory]:' maybe make this a
    seperate function call check_inventory(self): Returns True or False

    *condense object grabbing in the action methods into a seperate method for ease of use.

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
        self.inventory.append(item)
        if item in Weapons.weapon_objects:
            self.equip_weapon(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def equip_weapon(self, item):
        print("\nEquip {}? (yes or no)".format(item.name))
        opt = input(">  ")
        if opt[0] == 'y':
            self.equipped_weapon = item
            print("You equipped {}!\n".format(item.name))
        else:
            print("\n{} remains unequipped.".format(item.name))

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
                if self.run_away() == True:
                    self.current_room.next_room(self.current_room.branches[0])
                    break
            else:
                action = Actions(opt[0], opt[1:])
                action.run_action()
                enemy.enemy_turn()
        if self.health > 0 and enemy.health <= 0:
            print("\nCongratulations! You defeated {}".format(enemy.name))
            self.current_room.enemies = None
            self.current_room.events = 'None'
            Players.player_objects.remove(enemy)
            del enemy
        if self.health <= 0:
            print("\nYou were deafeated by {}".format(enemy.name))
            death("GAME OVER")

    def run_away(self):
        # Must roll above a 85 to run away
        print("Running away!. . . .")
        time.sleep(1)
        if randint(1, 100) > 85:
            print("\nYou ran away!")
            time.sleep(1)
            return True
        else:
            self.health -= 10
            print("You failed to run away!\nYou were hurt trying to escape")
            time.sleep(1)
            print("You have {}/100 health remaining".format(self.health))
            return False
            # run a enemy damage function

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
    """Initialies room object, attributes are pulled from text file"""

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

    def keypad(self):  # keypad minigame
        player = Players.get_player("player")
        code = "6824"
        while True:
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
            ====================

            goto, examine, use, pickup

            ====================

            Special commands for this room: {}
            """.format(special_actions)))

    def goto(self):
        player = Players.get_player('player')
        current_room = player.current_room
        if self.args[0] in current_room.branches:
            current_room.next_room(self.args[0])
        else:
            print("\n{} isn't an option".format(self.args[0]))

    # This functions is very specific and basically useless.
    def drink(self):  # Special action for room 'left'
        player = Players.get_player('player')
        if player.current_room.actions[0] == 'drink':
            if self.args[0] == 'water':
                print("\nYou drink the water, and immediately feel nauseous.")
                time.sleep(2)
                print("\nYou pass out and die.")
                death("GAME OVER")
            else:
                print("\nI don't understand drink '{}'".format(self.args[0]))
        else:
            print("\nYou can't do that here.")

    def inventory(self):
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

    # This function is ugly and has way too many conditionals. seperate func??
    # This function blows
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

    # This function is ugly and needs to be handled better.
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

    # Look into just inheriting the player, enemy objects from combat method
    def fight(self):
        # Grab needed objects
        player = Players.get_player('player')
        enemy = player.current_room.enemies
        weapon = player.equipped_weapon
        # Execute combat actions
        accuracy_roll = weapon.acc + randint(1, 100)
        print("You attack!. . . .")
        time.sleep(1.5)
        if accuracy_roll > 100:
            if accuracy_roll > 85 + weapon.acc:
                print("\nCritical hit!!! You hit {} for {} damage"
                      .format(enemy.name, int(weapon.dmg * 1.5)))
                enemy.health -= int(weapon.dmg * 1.5)
            else:
                damage_roll = weapon.dmg + randint(-5, 5)
                print("\nYou hit {} for {} damage".format(
                    enemy.name, damage_roll))
                enemy.health -= damage_roll
        else:
            print("\nYour attack misses!")
        print("{} has {} health remaining".format(enemy.name, enemy.health))
        time.sleep(1)


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
    # Game loop
    while True:
        opt = (input(">  ")).lower().split()
        try:  # Exception for index error if player presses enter without typing anything
            player_input = Actions(opt[0], opt[1:])
            player_input.run_action()
        except IndexError:
            print("\nHuh? (Invalid input. Type \"help\" for help)")


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
            elif choice[0].lower() == 'quit':
                quit()
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

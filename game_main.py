# file: text_game.py
# description: text game
# authors: Jacob Bickle, Alex DuPree
# date: 11/17/2017
# compiler: Python 3.6

"""
    * game_start.txt is the master game file. textGame.txt is the realtime
         file for use in game

    * started on the combat loop, basically mimics main game loop with a
        different action list.

    * need to add attribute for an equipped weapon for use in combat

    * Reworked the input function so it could be used for combat input as well

    * Need to rework the printing of room descriptions. Default terminal
        windows do not support text wrapping. Run a loop on the print statement
        to print a chunk of text at time.

    * Look into instantiating the entire game world with all the objects on
    startup. If we pursue this we will have to rework most of the functions.

    * Need to create help function

    * Need to create make death method functional and dynamic

    * Need to populate textGame.txt with actual game elements

    * Need to create a tutorial or readme.txt file for game

    * Look into saving game state
"""
import csv


class Players:
    """Initializes player class with attributes"""

    player_objects = []

    def __init__(self, name='', health=100, inventory=[], dignity=1):
        self.name = name
        self.health = health
        self.inventory = inventory
        self.dignity = dignity
        self.equipped_weapon = None
        self.player_objects.append(self)

    def read_inventory(self):
        print("\nInventory:\n====================")
        for item in self.inventory:
            print(item.name.capitalize(), 'x', item.uses)
        print("====================\n")

    # This function is linked to the pickup() function in the action class
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    # def get_item(self, item_name):
    #     for i in self.inventory:
    #         if i.name == item_name:
    #             return i

    def initialize_inventory(self, player):
        inventory = parse_file('textGame.txt', player, '*player_inventory')
        for i in inventory:
            attributes = parse_file('textGame.txt', i, '*items')
            if attributes == None:
                attributes = parse_file('textGame.txt', i, '*weapons')
                weapon_object = Weapons(i, attributes)
                self.add_item(weapon_object)
            else:
                item_object = Items(i, attributes)
                self.add_item(item_object)

    @classmethod
    def get_player(cls, name):
        for p in cls.player_objects:
            if name == p.name:
                return p

    def combat(self, enemy):
        action_list = ['FIGHT', 'Use (item)', 'Run', 'Cry']
        print("\nYou entered combat with {}".format(enemy.name))
        while self.health > 0 and enemy.health > 0:
            print("\nActions:")
            for action in action_list:
                print('\t' + action)
            opt = get_input("\n>  ", game_room, action_list)
            action = Actions(opt[0], opt[1:])
            action.run_action()


class Enemy(Players):
    """Creates enemy object for use in story"""

    def __init__(self, name='', health=100, inventory=[], dignity=1):
        super().__init__(self, health=100, inventory=[], dignity=1)
        self.name = name
        self.initialize_inventory(self.name)

    # @classmethod
    # def enemy_inventory(cls, name):
    #     pass


class Room:
    """Initialies room object, attributes are pulled from text file"""

    room_objects = []

    def __init__(self, room_title=''):
        keywords = ['*room_descriptions', '*room_branches', '*room_count',
                    '*room_events', '*room_items', '*room_actions',
                    '*room_lock_description', '*room_enemies']
        attributes = [parse_file('textGame.txt', room_title, target)
                      for target in keywords]
        self.room_title = room_title
        self.description = attributes[0]
        self.room_branches = attributes[1]
        self.counter = attributes[2]
        self.room_event = attributes[3]
        self.room_items = attributes[4]
        self.room_actions = attributes[5]
        self.lock_description = attributes[6]
        self.room_enemies = attributes[7]
        self.room_objects.append(self)

    def enter_room(self):
        if self.lock_description[0] == 'True':
            print('\n' + self.description[int(self.lock_description[1])])
        else:
            try:
                print('\n' + self.description[int(self.counter[0])])
            except IndexError:
                print('\n' + self.description[-1])
            self.increment_counter('textGame.txt')
            eval(self.room_event[0])

    def encounter(self):
        player = Players.get_player('player')
        enemy = Enemy(self.room_enemies[0])
        player.combat(enemy)

    # overwrites previous attributes based on room
    def next_room(self, room_title=''):
        keywords = ['*room_descriptions', '*room_branches', '*room_count',
                    '*room_events', '*room_items', '*room_actions',
                    '*room_lock_description', '*room_enemies']
        attributes = [parse_file('textGame.txt', room_title, target)
                      for target in keywords]
        self.room_title = room_title
        self.description = attributes[0]
        self.room_branches = attributes[1]
        self.counter = attributes[2]
        self.room_event = attributes[3]
        self.room_items = attributes[4]
        self.room_actions = attributes[5]
        self.lock_description = attributes[6]
        self.room_enemies = attributes[7]
        self.enter_room()

    def increment_counter(self, filename):
        num = self.counter[0]
        if int(num) == 9:
            return None
        with open(filename, 'r') as f:
            filedata = f.readlines()
            for row in range(len(filedata)):
                if self.room_title in filedata[row]:
                    filedata[row] = filedata[row].replace(
                        num, str(int(num) + 1))
        with open('textGame.txt', 'w') as file:
            file.writelines(filedata)

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
                self.next_room('left')
                break
            elif player_attempt.isnumeric():
                print(
                    "\nYouch! That felt just about as good as an electrical"
                    " shock shooting throughout your body could.")
                player.health -= 25
            else:
                print("\nThe keypad lets out a quizical beep. (Invalid input)")

    @classmethod
    def get_room(cls):
        return cls.room_objects[0]


class Actions:
    """creates object with users string to run a function"""

    def __init__(self, verb="", *args):
        self.verb = verb
        self.args = [arg for a in args for arg in a]

    def run_action(self):
        eval('self.' + self.verb + '()')

    def goto(self):
        current_room = Room.get_room()
        if self.args[0] in current_room.room_branches:
            current_room.next_room(self.args[0])
        else:
            print("\n{} isn't an option".format(self.args[0]))

    # This functions is very specific and basically useless.
    def drink(self):  # Special action for room 'left'
        if self.args[0] == 'water':
            print("\nYou drink the water, and immediately feel nauseous."
                  "\nYou pass out and die.")
            death("GAME OVER")
        else:
            print("\nI don't understand drink '{}'".format(self.args[0]))

    def inventory(self):
        player = Players.get_player('player')
        player.read_inventory()

    # This function is ugly and has way too many conditionals. seperate func??
    def pickup(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        current_room = Room.get_room()
        if item_name not in current_room.room_items:
            print("\nSorry, there is no {} here".format(item_name))
        else:
            item = self.eval_item()
            if item_name == 'bandage':
                print("\nYou picked up bandage!")
                item.uses += 1
            elif item_name in [i.name for i in player.inventory]:
                print("\nSorry, I don't understand. You already have {}"
                      .format(item_name))
            elif item.pickup == 'False':
                print("\n{} cannot be picked up".format(item_name))
            else:
                player.add_item(item)
                print("\nYou picked up {}!".format(item_name))

    def eval_item(self):
        if self.args[0] in [i.name for i in Items.item_objects]:
            return Items.get_item(self.args[0])
        else:
            attributes = parse_file('textGame.txt', self.args[0], '*items')
            if attributes == None:
                attributes = parse_file(
                    'textGame.txt', self.args[0], '*weapons')
                return Weapons(self.args[0], attributes)
            else:
                return Items(self.args[0], attributes)

    def fight(self):
        player = Players.get_player('player')
        current_room = Room.get_room()
        enemy = Players.get_player(current_room.room_enemies[0])
    # This function is ugly and needs to be handled better.

    def examine(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        current_room = Room.get_room()
        if item_name in [i.name for i in player.inventory]:
            item = Items.get_item(item_name)
            item.examine_item()
        elif item_name in current_room.room_items:
            attributes = parse_file('textGame.txt', item_name, '*items')
            if attributes == None:
                attributes = parse_file('textGame.txt', item_name, '*weapons')
                print('\n' + attributes[-1])
            else:
                print('\n' + attributes[-1])
        elif item_name == 'room':
            # Prints last description only
            print('\n' + current_room.description[-1])
        else:
            print("\nThere is no {} to examine".format(item_name))

    def use(self):
        item_name = self.args[0]
        player = Players.get_player('player')
        if item_name in [i.name for i in player.inventory]:
            item = Items.get_item(item_name)
            item.use_item()
        else:
            print("\nThere is no {} to use".format(item_name))


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
            print("\nYou healed yourself.")

        # This is a very specific in vague function.
    def light(self):
        current_room = Room.get_room()
        if current_room.lock_description[0] == 'True':
            change_boolean(
                'textGame.txt', '*room_lock_description', current_room.room_title)
            print("\nYou lit your {}".format(self.name))
            self.decrement_uses()
            current_room.increment_counter('textGame.txt')
            current_room.next_room(current_room.room_title)
        else:
            print("\nYou can't use that here")

    @classmethod
    def get_item(cls, name):
        for i in cls.item_objects:
            if name == i.name:
                return i


class Weapons(Items):
    """Creates weapons class, inherits from Items"""

    def __init__(self, item_name="", attributes=[]):
        super().__init__(item_name, attributes)
        self.dmg = attributes[3]
        self.acc = attributes[4]


def main():
    reset_game_file('game_start.txt')
    game_room = Room('start')
    player = Players('player')
    player.initialize_inventory('player')
    game_room.enter_room()
    # actual game loop
    action_list = ["goto", "help", "inventory", "examine", "pickup", "use"]
    while True:
        opt = get_input(">  ", game_room, action_list)
        action = Actions(opt[0], opt[1:])
        action.run_action()


def get_input(prompt, current_room, action_list):
    action_list += current_room.room_actions
    while True:
        choice = input(prompt).split()
        if choice[0].lower() in action_list:
            choice = [s.lower() for s in choice]
            return choice
        elif choice[0].lower() == 'quit':
            quit()
        else:
            print("\nSorry, I didn't understand. Type 'help' for help")


def reset_game_file(filename):
    with open(filename, 'r') as f:
        filedata = f.readlines()
    with open('textGame.txt', 'w') as file:
        file.writelines(filedata)


# This is inefficient
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
            # print("{} isn't an option".format(key))
            return None


# Need to update args to accept True/False swap, also able to update index value too
def change_boolean(filename, key, target, swap=['True', 'False']):
    end_key = (key.replace('*', '*end_'))
    with open(filename, 'r') as f:
        filedata = f.readlines()
        for i, row in enumerate(filedata):
            if key in row:
                start = i
            elif end_key in row:
                end = i
                break
        f.seek(0, 0)
        for i in range(start, end):
            if target in filedata[i]:
                filedata[i] = filedata[i].replace(swap[0], swap[1])
    with open('textGame.txt', 'w') as file:
        file.writelines(filedata)

# Need to fully implement death function


def death(message):
    print(message)
    quit()


main()

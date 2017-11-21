import csv

# Read in the file


def increment_counter(counter, room_title, filename):
    num = counter[0]
    if int(num) == 9:
        return None
    with open(filename, 'r') as f:
        filedata = f.readlines()
        for row in range(len(filedata)):
            if room_title in filedata[row]:
                filedata[row] = filedata[row].replace(num, str(int(num) + 1))
    with open('test.txt', 'w') as file:
        file.writelines(filedata)


def reset_counter(filename):
    with open(filename, 'r') as f:
        filedata = f.readlines()
        for i, row in enumerate(filedata):
            if "*room_count" in row:
                start = i
            elif"*end_room_count" in row:
                end = i
                break
        f.seek(0, 0)
        for i in range(start, end):
            for c in filedata[i]:
                if c.isdigit():
                    filedata[i] = filedata[i].replace(c, '0')
    with open('test.txt', 'w') as file:
        file.writelines(filedata)

# add set lock description index? probably better to make a set counter func


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
    with open('test.txt', 'w') as file:
        file.writelines(filedata)


# change_boolean('test.txt', '*room_lock_description', 'right')


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
            return(descriptions[key])
        except KeyError:
            # print("{} isn't an option".format(key))
            return ['']


# increment_counter(['9'], 'start', 'test.txt')
# reset_counter("test.txt")
# inventory = parse_file('test.txt', 'left', '*room_count')
# print(inventory)
# def death(messsage):
#     print(messsage)
# attributes = parse_file('test.txt', 'left', '*room_actions')
# print(attributes)
# attributes = dict(zip(*[iter(attributes)] * 2))
# print(attributes)
# test = {'none': 'none'}
# verb_list = {
#     "goto": "game_room", "help": "player", "inventory": "player",
#     "examine": ["player", "game_room"], "pickup": ["player", "game_room"],
#     "use": "player"
# }
# verb_list.update(test)
# print(eval('none'))
'''
    *orignally gonna use a real time text parsing to update inventory,
        but just using a list is much simpler way of storing the objects.
'''
# def add_item(self, filename, item):
#     with open(filename, 'r') as f:
#         filedata = f.readlines()
#         for row in range(len(filedata)):
#             if "*player_inventory" in filedata[row]:
#                 start = row + 2
#                 inventory = filedata[start].strip('\n')
#         new_inven = inventory + '|   ' + item + '\n'
#         filedata[start] = new_inven
#     with open('textGame.txt', 'w') as file:
#         file.writelines(filedata)
#     # updates player inventory
#     self.inventory = parse_file(
#         'textGame.txt', 'player', '*player_inventory')
# def remove_item(self, filename, item):
#     with open(filename, 'r') as f:
#         filedata = f.readlines()
#         for row in range(len(filedata)):
#             if "*player_inventory" in filedata[row]:
#                 start = row + 2
#                 inventory = filedata[start].strip('\n')
#         inventory = inventory.replace(item + "|", "")
#         inventory = inventory.replace(item, "")
#         filedata[start] = inventory
#     with open('textGame.txt', 'w') as file:
#         file.writelines(filedata)


# inventory = parse_file('test.txt', 'player', '*player_inventory')
# print(inventory)
# add_item('test.txt', 'clothes')
# inventory = parse_file('test.txt', 'player', '*player_inventory')
# print(inventory)
# remove_item("test.txt", "gun")
# inventory = parse_file('test.txt', 'player', '*player_inventory')
# print(inventory)
# eval(action[0])
# verb_list = {"goto": "game_room", "examine": "item", "help": "player"}
# print("goto" in verb_list.keys())

class Items:
    """Creates item object for use"""

    def __init__(self, item_name="", attributes=[]):

        self.name = item_name
        self.uses = int(attributes[0])
        self.func = attributes[1]
        self.pickup = attributes[2]
        self.description = attributes[-1]

    def examine_item(self):
        print('\n' + self.description)

    def use_item(self, object):
        if int(self.uses) > 0:
            eval('self.' + self.func)
        else:
            print("You can't use {}".format(self.name))

    def decrement_uses(self, object):
        self.uses -= 1
        if int(self.uses) == 0:
            object.remove_item(self)

    def heal(self, object):
        if object[0].health == 100:
            print("\nYou're not injured.")
        else:
            object[0].health += 25
            if object[0].health > 100:
                object[0].health = 100
            self.decrement_uses(object[0])
            print("\nYou healed yourself.")

    def light(self, object):
        if object[1].lock_description[0] == 'True':
            change_boolean(
                'textGame.txt', '*room_lock_description', object[1].room_title)
            print("\nYou lit your {}".format(self.name))
            self.decrement_uses(object[0])
            object[1].increment_counter('textGame.txt')
            object[1].next_room(object[1].room_title)
        else:
            print("\nYou can't use that here")


class Weapons(Items):
    """Creates weapons class, inherits from Items"""

    def __init__(self, item_name="", attributes=[]):
        super().__init__(item_name, attributes)
        self.dmg = attributes[3]
        self.acc = attributes[4]


# attributes = parse_file('test.txt', 'knife', '*weapons')
# knife = Weapons("knife", attributes)
# print(knife.acc)
# attributes = parse_file('test.txt', 'knife', '*items')
# print(attributes)

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
    def drink(self, object):  # Special action for room 'left'
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
            if item_name in [i.name for i in player.inventory]:
                print("\nSorry, I don't understand. You already have {}"
                      .format(item_name))
            elif item.pickup == 'False':
                print("\n{} cannot be picked up".format(item_name))
            else:
                player.add_item(item)
                print("\nYou picked up {}!".format(item_name))

    def eval_item(self):
        attributes = parse_file('textGame.txt', self.args[0], '*items')
        if attributes == None:
            attributes = parse_file('textGame.txt', self.args[0], '*weapons')
            return Weapons(self.args[0], attributes)
        else:
            return Items(self.args[0], attributes)

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

    def use(self, object):
        # needs to check for special items
        item_name = self.args[0]
        player = Players.get_player('player')
        if item_name in [i.name for i in player.inventory]:
            item = Items.get_item(item_name)
            item.use_item()
        else:
            print("\nThere is no {} to use".format(item_name))


# action = Actions("inventory")
# print(action.verb)
actions = ['goto', 'left', 'bitch']
action = Actions(actions[0], actions[1:])
print(action.args[0])

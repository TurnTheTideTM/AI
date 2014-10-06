__author__ = 'Richard'

from threading import Thread


TRUPPENPREIS = 100
UEBERNAHMEPREIS = 1000
LOOT = 200
MODEEFFEKT = 0.3
MODERABATT = 1 - MODEEFFEKT


class DummyAI (object):
    def __init__(self):
        self.player = None

    def add_player(self, player):
        self.player = player

    @staticmethod
    def ask_next_move():
        return 0, 0, 0

    def give_next_state(self, state):
        pass

    def reset(self):
        pass


class Human (object):
    def __init__(self):
        self.player = None
        self.state = None

    def add_player(self, player):
        self.player = player

    def ask_next_move(self):
        self.player.print_inbox()
        a = input("Aktion   : ")
        if a in (2, 3):
            opponents = self.state[4]
            for counter in range(len(opponents)):
                print "Opponent", counter, "is in State", opponents[counter], "."
        p = input("Parameter: ")
        m = input("Mode     : ")
        return a, p, m

    def give_next_state(self, state):
        self.state = state

    def reset(self):
        pass


class Planet(object):
    def __init__(self):
        self.owner = None
        self.mode = 0
        self.coords = [None, None]

    def set_owner(self, owner):
        self.owner = owner

    def set_mode(self, mode):
        self.mode = mode

    def set_coords(self, coords):
        self.coords = coords


class Player (object):
    def __init__(self):
        self.rohstoffe = 0
        self.truppen = 0
        self.produktion = 0
        self.mode = 0

        self.ai = DummyAI()

        self.planeten = []
        self.inbox = []

        self.move = [0, 0, 0]

        self.world = None

        self.nachbarn = []

        self.einmaliges_einkommen = 0

    def set_world(self, world):
        self.world = world

    def generate_nachbarn(self):
        temp = []
        dimensions = self.world.dimensions
        for planet in self.planeten:
            coords = planet.coords
            links = [coords[0] - 1, coords[1]]
            if links[0] < 0:
                links[0] = dimensions[0] - 1
            rechts = [coords[0] + 1, coords[1]]
            if rechts[0] == dimensions[0]:
                rechts[0] = 0
            oben = [coords[0], coords[1] - 1]
            if oben[1] < 0:
                oben[1] = dimensions[1] - 1
            unten = [coords[0], coords[1] + 1]
            if unten[1] == dimensions[1]:
                unten[1] = 0
            temp.append(oben)
            temp.append(unten)
            temp.append(links)
            temp.append(rechts)
        self.nachbarn = []
        for coord in temp:
            coord = tuple(coord)
            if coord not in self.nachbarn and self.world.coords_to_players[coord] != self:
                self.nachbarn.append(coord)

    def get_nachbar_data(self):
        result = []
        for nachbar in self.nachbarn:
            result.append(self.world.coords_to_players[nachbar].mode)
        return result

    def add_planet(self, coords):
        self.planeten.append(coords)

    def add_ai(self, ai):
        self.ai = ai
        ai.add_player(self)

    def next_move(self):
        self.ai.give_next_state(self.get_ai_input())
        self.move = self.ai.ask_next_move()

    def get_ai_input(self):
        return (self.rohstoffe,
                self.truppen,
                self.produktion,
                self.mode,
                self.get_nachbar_data())

    def reset_player(self):
        self.rohstoffe = 100
        self.truppen = 2
        self.produktion = 10
        self.mode = 0

        self.planeten = []
        self.inbox = []

        self.move = [0, 0, 0]

        self.nachbarn = []

        self.einmaliges_einkommen = 0

    def add_coords(self):
        for planet in self.planeten:
            self.world.coords_to_players.update({planet.coords: self})

    def recruit(self):
        amount = self.move[1]
        if self.mode == 0:
            maxamount = int(self.rohstoffe / (TRUPPENPREIS * MODERABATT))
        else:
            maxamount = int(self.rohstoffe / TRUPPENPREIS)
        if amount > maxamount:
            amount = maxamount
        self.truppen += amount
        if self.mode == 0:
            self.rohstoffe -= int(amount * TRUPPENPREIS * MODERABATT)
        else:
            self.rohstoffe -= int(amount * TRUPPENPREIS)
        self.inbox.append("Du hast " + str(amount) + " Truppen produziert. Neue Rohstoffmenge: "
                                     + str(self.rohstoffe) + " .")

    def attack(self):
        target = self.world.coords_to_players[self.nachbarn[self.move[1]]]
        if target.move[0] == 2:
            gegner = 0
        else:
            gegner = target.truppen
        if self.mode == 2:
            gegner -= int(self.truppen * MODEEFFEKT)
        if gegner < 0:
            gegner = 0
        if self.truppen > gegner:
            self.truppen -= gegner
            gegner /= 2
        else:
            gegner -= int(self.truppen / 2)
            self.truppen = 0
        target.truppen = gegner
        if target.mode == 1:
            loot = self.truppen * LOOT * MODERABATT
        else:
            loot = self.truppen * LOOT
        maxloot = target.rohstoffe
        if loot > maxloot:
            loot = maxloot
        loot = int(loot)
        target.rohstoffe -= loot
        self.rohstoffe += loot
        self.inbox.append(str(self.truppen) + " Truppen haben den Angriff ueberlebt. Es wurden "
                                            + str(loot) + " Rohstoffe erbeutet.")

    def buy(self):
        target = self.world.coords_to_players[self.nachbarn[self.move[1]]]
        price = UEBERNAHMEPREIS
        if self.mode == 2:
            price *= MODERABATT
        if target.mode == 1:
            price += UEBERNAHMEPREIS * MODEEFFEKT
        grundgebuehr = price
        price += target.rohstoffe
        if self.rohstoffe > price:
            self.einmaliges_einkommen -= price
            target.einmaliges_einkommen += price
            if target in self.world.uebernahmen:
                self.world.uebernahmen[target].append(self)
            else:
                self.world.uebernahmen[target] = [self]
        else:
            self.einmaliges_einkommen -= grundgebuehr
            target.einmaliges_einkommen += grundgebuehr

    def generate_status(self):
        status = "------STATUSREPORT------\n"
        status += "Rohstoffe : " + str(self.rohstoffe) + "\n"
        status += "Truppen   : " + str(self.truppen) + "\n"
        status += "Produktion: " + str(self.produktion) + "\n"
        status += "Modus     : " + str(self.mode)
        self.inbox.append(status)

    def print_inbox(self):
        for counter in range(len(self.inbox)):
            print "---------- " + str(counter) + " -----------"
            print self.inbox[counter]
        print "------------------------"
        self.inbox = []


class World (object):
    def __init__(self):
        self.players = []
        self.loosers = []
        self.planets = []
        self.coords_to_planets = {}
        self.coords_to_players = {}
        self.dimensions = [0, 0]
        self.uebernahmen = {}

    def set_dimensions(self, dimensions):
        self.dimensions = dimensions

    def add_player(self, player):
        player.world = self
        self.players.append(player)
        player.add_coords()

    def add_planet(self, planet):
        self.planets.append(planet)
        self.coords_to_planets.update({planet.coords: planet})

    def runde_ausfuehren(self):
        attack = []
        recruit = []
        buy = []

        for player in self.players:
            player.next_move()
            if player.move[0] == 1:
                recruit.append(player)
            elif player.move[0] == 2:
                attack.append(player)
            elif player.move[0] == 3:
                buy.append(player)

        for player in recruit:
            player.recruit()

        for player in attack:
            player.attack()

        for player in buy:
            player.buy()

        for target in self.uebernahmen:
            if len(self.uebernahmen[target]) > 1:
                candidates = self.uebernahmen[target]
                winner = candidates[0]
                for player in candidates:
                    if player.rohstoffe > winner.rohstoffe:
                        winner = player
                for player in candidates:
                    if player != winner:
                        player.einmaliges_einkommen += target.rohstoffe
                for planet in target.planeten:
                    winner.add_planet(planet)
                    planet.set_owner(winner)
                    self.coords_to_players[planet.coords] = winner
                winner.produktion += target.produktion / 2
                self.players.remove(target)
                self.loosers.append(target)
                target.rohstoffe += target.einmaliges_einkommen
                target.einmaliges_einkommen = 0
                winner.inbox.append("Sie haben einen Planeten gekauft!")
                target.inbox.append("Sie wurden leider aufgekauft.")
            else:
                winner = self.uebernahmen[target][0]
                for planet in target.planeten:
                    winner.add_planet(planet)
                    planet.set_owner(winner)
                    self.coords_to_players[planet.coords] = winner
                winner.produktion += target.produktion / 2
                self.players.remove(target)
                self.loosers.append(target)
                target.rohstoffe += target.einmaliges_einkommen
                target.einmaliges_einkommen = 0
                winner.inbox.append("Sie haben einen Planeten gekauft!")
                target.inbox.append("Sie wurden leider aufgekauft.")

        for player in self.players:
            player.rohstoffe += player.einmaliges_einkommen
            player.einmaliges_einkommen = 0
            if player.mode == 0:
                player.rohstoffe += player.produktion * (1 + MODEEFFEKT)
            else:
                player.rohstoffe += player.produktion
            player.generate_nachbarn()
            player.mode = player.move[2]
            player.rohstoffe = int(player.rohstoffe)
            player.generate_status()

    def generate_players(self):
        for counter1 in range(self.dimensions[0]):
            for counter2 in range(self.dimensions[1]):
                player = Player()
                planet = Planet()
                player.reset_player()
                planet.set_coords((counter1, counter2))
                planet.set_owner(player)
                player.set_world(self)
                player.add_planet(planet)
                player.add_coords()
                player.add_ai(AI_POOL[0])
                AI_POOL.remove(AI_POOL[0])
                self.add_player(player)
                self.add_planet(planet)

        for counter1 in range(self.dimensions[0]):
            for counter2 in range(self.dimensions[1]):
                self.coords_to_players[(counter1, counter2)].generate_nachbarn()


class Game (Thread):
    def __init__(self):
        Thread.__init__(self)
        self.world = None
        self.rundengrenze = 0

    def set_up_game(self, runden, dimensions):
        self.set_rundenbegrenzung(runden)
        self.world = World()
        self.world.set_dimensions(dimensions)
        self.world.generate_players()

    def set_world(self, world):
        self.world = world

    def set_rundenbegrenzung(self, grenze):
        self.rundengrenze = grenze

    def run(self):
        for counter in range(self.rundengrenze):
            self.world.runde_ausfuehren()


if __name__ == "__main__":
    from ProjectNeurons.KatoraBot.BotMain import planet_environment
    from random import shuffle

    HUMANS = 1
    NEURONS = 50

    AI_POOL = []

    for i in range(HUMANS):
        AI_POOL.append(Human())

    for i in range(NEURONS):
        AI_POOL.append(planet_environment())

    for i in range(100 - HUMANS - NEURONS):
        AI_POOL.append(DummyAI())

        shuffle(AI_POOL)

    game = Game()
    game.set_up_game(1000, (10, 10))
    game.start()

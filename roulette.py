"""
This module is responsible for running the coffee roulette event,
including the representation of people and connections
"""
from collections import namedtuple
from random import choice

PersonT = namedtuple("Person", ["name", "contact", "team", "year"])
ConnectionT = namedtuple("Connection", ["person_1", "person_2", "person_3"])

def Person(name, contact, team=None, year=None):
    """
    Returns a PersonT namedtuple, allowing for default arguments
    """
    return PersonT(name, contact, team, year)

def Connection(person_1, person_2, person_3=None):
    """
    Returns a ConnectionT namedtuple, allowing for default arguments
    """
    return ConnectionT(person_1, person_2, person_3)

class Roulette():
    """
    This class generates the pairs between the pairs
    """
    def __init__(self):
        self.pairings = []
        self.participants = []
        self.weeks = 0

    def generate_pairs(self):
        """
        This method generates all possible pairs (triple if necessary) of participants
        Based upon answer here:
        https://math.stackexchange.com/questions/3093225/an-efficient-approach-to-combinations-of-pairs-in-groups-without-repetitions

        Each row is considered a week (after changing the infinite pair to a real person)
        If there are an odd number of participants, the left over person is randomly assigned to
        another pair.

        Output is a list of weekly pairs
        Each week of pairs is a Connection object
        """
        n = len(self.participants)
        for i in range(n):
            weekly_pairs = []
            for k in range(n // 2):
                person_1_index = (i + k) % n
                person_2_index = (i - k) % n

                # this handles the infinite pairing
                if person_1_index == person_2_index:
                    person_2_index = (i + n // 2) % n

                person_1 = self.participants[person_1_index]
                person_2 = self.participants[person_2_index]

                weekly_pairs.append(Connection(person_1, person_2))

            if n % 2 == 1:
                # this handles the odd number of participants
                missing_person = self.participants[(n // 2 + 1 + i) % n]
                random_pair = choice(weekly_pairs)
                person_a, person_b, _ = random_pair
                new_triple = Connection(person_a, person_b, missing_person)
                weekly_pairs.append(new_triple)
                weekly_pairs.remove(random_pair)

            self.pairings.append(weekly_pairs)

    def add_participant(self, person):
        """
        This method adds another participant to the roulette
        """
        self.participants.append(person)
        self.weeks += 1

if __name__ == "__main__":
    # Example usage of Roulette class
    
    roulette = Roulette()
    participants = [
        Person("Chris", 0),
        Person("Jess", 1),
        Person("JP", 2),
        Person("Zara", 3),
        Person("Navid", 4),
        Person("Amy", 5),
        Person("Momo", 6),
        Person("Liam", 7)
    ]

    for participant in participants:
        roulette.add_participant(participant)

    roulette.generate_pairs()

    for week in range(roulette.weeks):
        print(f"Week {week + 1}:")
        for pair in roulette.pairings[week]:
            if pair.person_3 is None:
                print(f"{pair.person_1.name} is paired with {pair.person_2.name}")
            else:
                print(f"{pair.person_1.name} is paired with {pair.person_2.name} and {pair.person_3.name}")
            print()

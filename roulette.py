"""
This module is responsible for running the coffee roulette event,
including the representation of people and connections
"""
from collections import namedtuple
import csv
from random import choice
import sys
import yaml

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

        # default config parameters will be overwritten by read_config
        self.participant_file = "participants.csv"
        self.pairs_file = "pairs.csv"
        self.name_column_index = 0
        self.email_column_index = 1
        self.read_config()

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

    def read_participants_from_file(self, file_path=None):
        """
        This method reads the list of participants and associated details from a csv file,
        specified by the input_file field of config.yml
        """
        if file_path is None:
            file_path = self.participant_file

        with open(file_path, "r") as f:
            reader = csv.reader(f)

            for row in reader:
                name = row[self.name_column_index]
                email = row[self.email_column_index]
                participant = Person(name, email)
                self.add_participant(participant)

    def write_pairs_to_file(self, file_path=None):
        """
        This method writes the generated pairs to a csv file,
        specified by output_file field of config.yml
        """
        if file_path is None:
            file_path = self.pairs_file
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            rows = []
            # structure:
            # week (1 indexed), person_1, person_2, person_3 ("" if only a pair)
            for week in range(self.weeks):
                for pair in self.pairings[week]:
                    if pair.person_3 is None:
                        row = [week + 1, pair.person_1.name, pair.person_2.name, ""]
                    else:
                        row = [week + 1, pair.person_1.name, pair.person_2.name, pair.person_3.name]
                    rows.append(row)
            writer.writerows(rows)

    def read_config(self):
        """
        This method reads the config file and populates relevant variables
        """
        try:
            config = yaml.safe_load(open("config.yaml"))
        except FileNotFoundError:
            sys.exit("Config file could not be found. Aborting")

        self.participant_file = config["input_file"]
        self.pairs_file = config["output_file"]
        self.name_column_index = int(config["name_column_index"])
        self.email_column_index = int(config["email_column_index"])

if __name__ == "__main__":
    # Example usage of Roulette class

    roulette = Roulette()
    '''
    participants = [
        Person("Shirley", 0),
        Person("Emily", 1),
        Person("Prima", 2),
        Person("Chris", 3),
        Person("Jason", 4),
        Person("Liam", 5),
        Person("Merin", 6),
        Person("Momo", 7)
    ]

    for participant in participants:
        roulette.add_participant(participant)
'''
    roulette.read_participants_from_file()
    roulette.generate_pairs()

    for demo_week in range(roulette.weeks):
        print(f"Week {demo_week + 1}:")
        for demo_pair in roulette.pairings[demo_week]:
            if demo_pair.person_3 is None:
                print(f"{demo_pair.person_1.name} is paired with {demo_pair.person_2.name}")
            else:
                print(f"{demo_pair.person_1.name} is paired with "
                      f"{demo_pair.person_2.name} and {demo_pair.person_3.name}")
        print()
    roulette.read_config()
    roulette.write_pairs_to_file()

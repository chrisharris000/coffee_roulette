"""
This module is responsible for running the coffee roulette event, including:
- the representation of people and connections
- reading files
- generating pairs
- writing files
- sending emails
"""
from collections import namedtuple
import csv
import ezgmail
from mdutils.mdutils import MdUtils
from random import choice
import re
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
        self.config = {
            "participant_file": "participants.csv",
            "pairs_csv_file": "pairs.csv",
            "pairs_md_file": "pairs.md",
            "name_column_index": 0,
            "email_column_index": 1,
            "team_column_index": -1, # currently not used
            "year_column_index": -1, # currently not used
            "send_email": False,
            "week_num": 1,
            "deadline": "01/01/1970"
        }
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

            # this handles the infinite pairing
            person_1_index = i
            person_2_index = n - 1
            person_1 = self.participants[person_1_index]
            person_2 = self.participants[person_2_index]
            weekly_pairs.append(Connection(person_1, person_2))

            for k in range(1, n // 2):
                person_1_index = (i + k) % (n - 1)
                person_2_index = (i - k) % (n - 1)

                person_1 = self.participants[person_1_index]
                person_2 = self.participants[person_2_index]

                weekly_pairs.append(Connection(person_1, person_2))

            if n % 2 == 1:
                # this handles the odd number of participants
                missing_person = self.participants[(n // 2 + i) % (n - 1)]
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
            file_path = self.config["participant_file"]

        with open(file_path, "r") as f:
            reader = csv.reader(f)

            for row in reader:
                name = row[self.config["name_column_index"]]
                email = row[self.config["email_column_index"]]
                team = None
                year = None

                if self.config["team_column_index"] != -1:
                    team = row[self.config["team_column_index"]]

                if self.config["year_column_index"] != -1:
                    year = row[self.config["year_column_index"]]

                participant = Person(name, email, team, year)
                self.add_participant(participant)

    def write_pairs_to_csv_file(self, file_path=None):
        """
        This method writes the generated pairs to a csv file,
        specified by pairs_csv_file field of config.yml
        """
        if file_path is None:
            file_path = self.config["pairs_csv_file"]
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            rows = []
            # structure:
            # week (1 indexed), person_1, person_2, person_3 ("" if only a pair),
            # person_1 email, person_2 email, person_3 email ("" if only a pair)
            for week in range(self.weeks):
                for pair in self.pairings[week]:
                    if pair.person_3 is None:
                        row = [week + 1, pair.person_1.name, pair.person_2.name, "",
                               pair.person_1.contact, pair.person_2.contact, ""]
                    else:
                        row = [week + 1, pair.person_1.name, pair.person_2.name, pair.person_3.name,
                               pair.person_1.contact, pair.person_2.contact, pair.person_3.contact]
                    rows.append(row)
            writer.writerows(rows)

    def write_pairs_to_md_file(self, file_path=None):
        """
        This method writes the generated pairs to a md file,
        specified by pairs_md_file field of config.yml
        """
        if file_path is None:
            file_path = self.config["pairs_md_file"]

        md_emoji = [
            ":coffee:",
            ":tea:",
            ":beer:",
            ":cocktail:",
            ":tropical_drink:",
            ":wine_glass:",
            ":cake:",
            ":cookie:",
            ":croissant:",
            ":pancakes:",
            ":pretzel:",
            ":doughnut:",
            ":pie:",
            ":cup_with_straw:"
        ]

        md_file = MdUtils(file_name=file_path, title="Robogals Coffee Roulette")

        for week in range(self.weeks):
            md_file.new_paragraph(f"*Week {week + 1}:*")
            for pair in self.pairings[week]:
                if pair.person_3 is None:
                    md_file.new_line(f"*{pair.person_1.name}* {choice(md_emoji)} is paired with "
                                     f"*{pair.person_2.name}* {choice(md_emoji)}")
                else:
                    md_file.new_line(f"*{pair.person_1.name}* {choice(md_emoji)} is paired with "
                                     f"*{pair.person_2.name}* {choice(md_emoji)} and "
                                     f"*{pair.person_3.name}* {choice(md_emoji)}")
            md_file.new_paragraph()
        md_file.create_md_file()

    def send_participants_email(self, week_num=None, deadline=None):
        """
        This method will send an email to each participant stating who their pair is for
        the week_num
        - email is from the contact column
        - week_num is 1 indexed
        """
        if not self.config["send_email"]:
            return False

        if week_num is None:
            week_num = self.config["week_num"]

        if deadline is None:
            deadline = self.config["deadline"]

        try:
            week_num_pairs = self.pairings[week_num - 1]
        except IndexError:
            raise IndexError("Invalid week number")

        for pair in week_num_pairs:
            for person in pair:
                if person is None:
                    continue
                contact = person.contact
                if self.is_email(contact):
                    s = ""
                    people = [p for p in pair if p != person and p is not None]
                    if len(people) == 1:
                        s = f"{people[0].name} ({people[0].contact})"
                    else:
                        s = (f"{people[0].name} ({people[0].contact}) and "
                             f"{people[1].name} ({people[1].contact})")

                    msg = (f"Hi {person.name},\n\n"
                           f"This week you have been matched with {s} for Robogals Coffee Roulette."
                           f" Make sure you get in contact with them, the sooner the better, "
                           f"and organise a time and place to meet up and get to know each other.\n"
                           f"Please do so before {deadline}, as this is when the next lot of "
                           f"pairs will be released.\n\n"
                           f"If you have any questions, please send us a message on "
                           f"#coffee-roulette or robogals.coffee.roulette@gmail.com")

                    subject = f"Robogals Coffee Roulette - Week {week_num}"

                    ezgmail.send(contact, subject, msg)

    def is_email(self, contact):
        """
        This method provides simple validation of a contact email
        """
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.search(regex, contact)

    def read_config(self):
        """
        This method reads the config file and populates relevant variables
        """
        try:
            config = yaml.safe_load(open("config.yaml"))
        except FileNotFoundError:
            sys.exit("Config file could not be found. Aborting")

        self.config = config

        int_params = ["name_column_index",
                      "email_column_index",
                      "team_column_index", # currently not used
                      "year_column_index", # currently not used
                      "week_num"
                      ]

        for param in int_params:
            self.config[param] = int(self.config[param])

if __name__ == "__main__":
    # Example usage of Roulette class

    roulette = Roulette()
    #roulette.read_config()

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
    roulette.write_pairs_to_csv_file()
    roulette.write_pairs_to_md_file()
    roulette.send_participants_email()
    input()

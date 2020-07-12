"""
This module is responsible for running the coffee roulette event,
including the representation of people and connections
"""
import collections

class Person():
    """
    This class represents a participant in the coffee roulette
    """
    def __init__(self, name, contact, team, year_level):
        self.name = name
        self.contact = contact
        self.team = team
        self.year_level = year_level
        self.past_connections = []

    def __str__(self):
        return f"Person({self.name}, {self.contact})"

    def has_connected_with(self, person):
        """
        Returns True if the participant has previously connected with the other person
        """
        return person in self.past_connections

    def archive_connection(self, connection):
        """
        Adds specified connection to list of past connections
        """
        self.past_connections.append(connection)

Connection = collections.namedtuple("Connection", ["person_1", "person_2", "connection_date"])

class Roulette():
    """
    This class generates the pairs between the pairs
    """
    def __init__(self, participants):
        self.participants = participants

    def generate_all_pairs(self):
        """
        Generates all possible pairs
        Output is a list of tuples, (Person, Person)
        """
        return []

    def generate_current_pairs(self):
        """
        Generates the pairs for the current time period
        Output is a list of tuples, (Person, Person)
        """
        return []

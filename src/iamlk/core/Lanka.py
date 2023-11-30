import random
from functools import cache, cached_property

from gig import Ent, EntType, GIGTable, GIGTableRow


class RandomGND:
    def __init__(self, gnd: Ent):
        self.gnd = gnd

    @cache
    def get_census_gig_table_row(self, measurement: str) -> GIGTableRow:
        return self.gnd.gig(GIGTable(measurement, 'regions', '2012'))

    @cache
    def get_election_gig_table_row(
        self, election_type: str, year: str
    ) -> GIGTableRow:
        measurement = f'government-elections-{election_type}'
        return self.gnd.gig(GIGTable(measurement, 'regions-ec', year))

    @cache
    def get_random_cell(self, gig_row: GIGTableRow) -> str:
        value_total = gig_row.total
        d = gig_row.dict
        valid_d = {
            k: v
            for k, v in d.items()
            if k.lower() not in ['valid', 'electors', 'polled', 'rejected']
        }
        value_total = sum(valid_d.values())
        random_value = random.random() * value_total
        cum_value = 0
        for k, v in valid_d.items():
            print(k, cum_value, random_value, cum_value + v)
            if cum_value < random_value <= cum_value + v:
                return k
            cum_value += v
        return None

    @cache
    def get_census_random_cell(self, measurement: str) -> str:
        return self.get_random_cell(
            self.get_census_gig_table_row(measurement)
        )

    @cache
    def get_election_random_cell(self, election_type: str, year: str) -> str:
        return self.get_random_cell(
            self.get_election_gig_table_row(election_type, year)
        )

    @cached_property
    def ethnicity(self) -> str:
        return self.get_census_random_cell('population-ethnicity').title()

    @cached_property
    def religion(self) -> str:
        return self.get_census_random_cell('population-religion').title()

    @cached_property
    def gender(self) -> str:
        return self.get_census_random_cell('population-gender').title()

    @cached_property
    def age(self) -> int:
        age_group = self.get_census_random_cell('population-age_group')

        if 'less' in age_group:
            min_age, max_age = 0, 9
        elif 'more' in age_group:
            min_age, max_age = 90, 99
        else:
            tokens = age_group.split('_~_')
            min_age, max_age = int(tokens[0]), int(tokens[1])

        age = random.randint(min_age, max_age)
        return age

    @cached_property
    def presidential_2019(self) -> str:
        return self.get_election_random_cell('presidential', '2019').upper()

    @cached_property
    def parliamentary_2020(self) -> str:
        return self.get_election_random_cell('parliamentary', '2020').upper()


class Lanka:
    def __init__(self, gnd: Ent):
        self.gnd = gnd
        random_gnd = RandomGND(gnd)
        self.gender = random_gnd.gender
        self.age = random_gnd.age
        self.religion = random_gnd.religion
        self.ethnicity = (
            random_gnd.ethnicity
            if self.religion != 'Buddhist'
            else 'Sinhalese'
        )
        self.presidential_2019 = random_gnd.presidential_2019
        self.parliamentary_2020 = random_gnd.parliamentary_2020

    @staticmethod
    def get_random_gnd() -> Ent:
        gnd_list = Ent.list_from_type(EntType.GND)
        random_gnd = random.choice(gnd_list)
        return random_gnd

    @staticmethod
    def random():
        return Lanka(Lanka.get_random_gnd())

    @cached_property
    def gnd(self) -> Ent:
        return Ent.from_id(self.gnd.id)

    @cached_property
    def dsd(self) -> Ent:
        return Ent.from_id(self.gnd.id[:7])

    @cached_property
    def district(self) -> Ent:
        return Ent.from_id(self.gnd.id[:5])

    @cached_property
    def province(self) -> Ent:
        return Ent.from_id(self.gnd.id[:4])

    @cached_property
    def address(self) -> str:
        return ', '.join(
            [
                self.gnd.name,
                self.dsd.name + ' DSD',
                self.district.name + ' District',
                'in the ' + self.province.name + ' Province',
            ]
        )

    def __str__(self) -> str:
        lines = [
            'I am Lanka.',
            f'I am a {self.age} year old, {self.gender} from Sri Lanka.',
            f'I am live in  {self.address}.',
            f'I identify as a {self.ethnicity} and a {self.religion}.',
            f'In the 2019 Presidential election, I voted for the {self.presidential_2019}, and in the 2020 Parliamentary election, I voted for the {self.parliamentary_2020}.',
        ]
        return '\n'.join(lines)

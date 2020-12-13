import csv
from typing import DefaultDict
from typing import Tuple

import attr

from util import clean_name


@attr.s
class PokemonEncounterRate:
    pokemon_name = attr.ib(type=str)
    level = attr.ib(type=int)
    percent_chance = attr.ib(type=int)


Encounters = DefaultDict[Tuple[str, int], PokemonEncounterRate]


@attr.s
class MapEncounters:
    map_id = attr.ib(type=str)
    morning_pokemon = attr.ib(type=Encounters, factory=dict)
    day_pokemon = attr.ib(type=Encounters, factory=dict)
    night_pokemon = attr.ib(type=Encounters, factory=dict)

    def _add_encounter_rate(
        self, encounter_rate: PokemonEncounterRate, collection: Encounters
    ) -> None:
        key = (encounter_rate.pokemon_name, encounter_rate.level)
        if key not in collection:
            collection[key] = encounter_rate
        else:
            collection[key].percent_chance += encounter_rate.percent_chance

    def add_encounter_rate(
        self, encounter_rate: PokemonEncounterRate, time_of_day: str
    ) -> None:
        if time_of_day == "morning":
            self._add_encounter_rate(encounter_rate, self.morning_pokemon)
        elif time_of_day == "day":
            self._add_encounter_rate(encounter_rate, self.day_pokemon)
        else:
            self._add_encounter_rate(encounter_rate, self.night_pokemon)

    def write_to_csv(self, writer: csv.writer) -> None:
        sort_key = lambda x: x.percent_chance

        writer.writerow([clean_name(self.map_id)])
        writer.writerow(["Morning"])
        for encounter_rate in sorted(
            self.morning_pokemon.values(), key=sort_key, reverse=True
        ):
            writer.writerow(
                [
                    encounter_rate.pokemon_name,
                    encounter_rate.level,
                    str(encounter_rate.percent_chance) + "%",
                ]
            )
        writer.writerow([])

        writer.writerow(["Day"])
        for encounter_rate in sorted(
            self.day_pokemon.values(), key=sort_key, reverse=True
        ):
            writer.writerow(
                [
                    encounter_rate.pokemon_name,
                    encounter_rate.level,
                    str(encounter_rate.percent_chance) + "%",
                ]
            )
        writer.writerow([])

        writer.writerow(["Night"])
        for encounter_rate in sorted(
            self.night_pokemon.values(), key=sort_key, reverse=True
        ):
            writer.writerow(
                [
                    encounter_rate.pokemon_name,
                    encounter_rate.level,
                    str(encounter_rate.percent_chance) + "%",
                ]
            )
        writer.writerow([])
        writer.writerow([])


def make_encounter_obj(file_line: str, percent_chance: int) -> PokemonEncounterRate:
    level, name = file_line[3:].replace(" ", "").split(",")
    return PokemonEncounterRate(clean_name(name), int(level), percent_chance)


def parse_grass_file(input_filename: str, output_filename: str):
    with open(input_filename) as input_file, open(output_filename, "w") as output_file:
        writer = csv.writer(output_file)

        for _ in range(4):
            input_file.readline()

        while True:
            map_id = input_file.readline().strip()
            if "db -1" in map_id:
                # done
                break

            map_id = map_id.replace("map_id", "").strip()

            map_encounters = MapEncounters(map_id)
            # unused line
            input_file.readline()
            # commented line
            input_file.readline()

            morning_pokemon = []
            morning_pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 20)
            )
            morning_pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 20)
            )
            morning_pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 20)
            )
            morning_pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 15)
            )
            morning_pokemon.append(make_encounter_obj(input_file.readline().strip(), 15))
            morning_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))
            morning_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))

            for pokemon_rate in morning_pokemon:
                map_encounters.add_encounter_rate(pokemon_rate, "morning")

            # commented line
            input_file.readline()

            day_pokemon = []
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 15))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 15))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))
            day_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))

            for pokemon_rate in day_pokemon:
                map_encounters.add_encounter_rate(pokemon_rate, "day")

            # commented line
            input_file.readline()

            night_pokemon = []
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 20))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 15))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 15))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))
            night_pokemon.append(make_encounter_obj(input_file.readline().strip(), 5))

            for pokemon_rate in night_pokemon:
                map_encounters.add_encounter_rate(pokemon_rate, "night")

            # blank line
            input_file.readline()

            map_encounters.write_to_csv(writer)

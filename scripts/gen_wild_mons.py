import csv
from typing import DefaultDict
from typing import List
from typing import Union
from typing import Tuple

import attr

from util import clean_name


@attr.s
class PokemonEncounterRate:
    pokemon_name = attr.ib(type=str)
    level = attr.ib(type=int)
    percent_chance = attr.ib(type=int)

    def write_to_csv(self, writer: csv.writer):
        writer.writerow(
            [
                clean_name(self.pokemon_name),
                self.level,
                str(self.percent_chance) + "%",
            ]
        )

    def copy(self):
        return self.__class__(
            pokemon_name=self.pokemon_name,
            level=self.level,
            percent_chance=self.percent_chance,
        )


Encounters = DefaultDict[Tuple[str, int], PokemonEncounterRate]

# placeholder until TimeGroups are parsed from fish.asm
@attr.s
class DummyFishTimeGroup:
    time_group_id = attr.ib(type=int)
    percent_chance = attr.ib(type=int)

@attr.s
class FishTimeGroup:
    daytime_encounter = attr.ib(type=PokemonEncounterRate)
    nighttime_encounter = attr.ib(type=PokemonEncounterRate)

FishEncounters = List[Union[PokemonEncounterRate, DummyFishTimeGroup]]

@attr.s
class FishGroup:
    name = attr.ib(type=str)
    rod = attr.ib(type=str)
    encounters = attr.ib(type=FishEncounters, factory=list)

    def write_to_csv(self, writer: csv.writer, time_groups: List[FishTimeGroup]) -> None:
        writer.writerow([clean_name(self.name)])
        writer.writerow([clean_name(self.rod)])
        writer.writerow(["Day", "Level", "Encounter Rate"])
        for encounter in self.encounters:
            if isinstance(encounter, DummyFishTimeGroup):
                encounter_rate = time_groups[encounter.time_group_id].daytime_encounter.copy()
                encounter_rate.percent_chance = encounter.percent_chance
            else:
                encounter_rate = encounter

            encounter_rate.write_to_csv(writer)

        writer.writerow([])

        writer.writerow(["Night", "Level", "Encounter Rate"])
        for encounter in self.encounters:
            if isinstance(encounter, DummyFishTimeGroup):
                encounter_rate = time_groups[encounter.time_group_id].nighttime_encounter.copy()
                encounter_rate.percent_chance = encounter.percent_chance
            else:
                encounter_rate = encounter

            encounter_rate.write_to_csv(writer)

        writer.writerow([])
        writer.writerow([])

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
        writer.writerow(["Morning", "Level", "Encounter Rate"])
        for encounter_rate in sorted(
            self.morning_pokemon.values(), key=sort_key, reverse=True
        ):
            encounter_rate.write_to_csv(writer)
        writer.writerow([])

        writer.writerow(["Day", "Level", "Encounter Rate"])
        for encounter_rate in sorted(
            self.day_pokemon.values(), key=sort_key, reverse=True
        ):
            encounter_rate.write_to_csv(writer)
        writer.writerow([])

        writer.writerow(["Night", "Level", "Encounter Rate"])
        for encounter_rate in sorted(
            self.night_pokemon.values(), key=sort_key, reverse=True
        ):
            encounter_rate.write_to_csv(writer)
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

def parse_water_file(input_filename: str, output_filename: str):
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

            pokemon = []
            pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 40)
            )
            pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 40)
            )
            pokemon.append(
                make_encounter_obj(input_file.readline().strip(), 20)
            )

            for pokemon_rate in pokemon:
                map_encounters.add_encounter_rate(pokemon_rate, "morning")
                map_encounters.add_encounter_rate(pokemon_rate, "day")
                map_encounters.add_encounter_rate(pokemon_rate, "night")

            # blank line
            input_file.readline()

            map_encounters.write_to_csv(writer)

def parse_fish_file(input_filename: str, output_filename: str):
    with open(input_filename) as input_file:
        for _ in range(23):
            input_file.readline()

        fish_groups = []

        while True:
            fish_group_name = input_file.readline().replace(".", "").replace(":", "").strip()
            # for duplicate groups
            if "NoSwarm" in fish_group_name:
                continue
            if not fish_group_name.strip():
                continue
            if "TimeFishGroups" in fish_group_name:
                break

            fish_name_and_rod = fish_group_name.split("_")
            rod = fish_name_and_rod[-1]
            fish_name = " ".join(fish_name_and_rod[:-1])

            fish_group = FishGroup(name=fish_name, rod=rod + " Rod")

            total_percent_chance = 0
            while total_percent_chance < 100:
                line = input_file.readline()
                line = line.replace("db", "").replace(" percent", "").replace(" + 1", "").strip()
                parts = [p.strip() for p in line.split(",")]
                # probability is accumulative, so subtract from the previous
                # number to get the chance to encounter
                current_percent = int(parts[0])
                percent_chance = current_percent - total_percent_chance
                total_percent_chance = current_percent

                # if this line is a time_group, it only has two parameters
                # instead of three
                if len(parts) == 2:
                    time_group_id = int(parts[1].split(" ")[-1].strip())
                    # the time_groups are at the bottom, so we need to wait until later to know what is being output
                    encounter = DummyFishTimeGroup(time_group_id=time_group_id, percent_chance=percent_chance)
                else:
                    encounter = PokemonEncounterRate(pokemon_name=parts[1], level=int(parts[2]), percent_chance=percent_chance)

                fish_group.encounters.append(encounter)

            fish_groups.append(fish_group)

        # skip the line after TimeFishGroups
        input_file.readline()

        time_groups = []

        while True:
            line = input_file.readline()
            if not line:
                break

            line = line.split(";")[0].replace("db", "").strip()
            parts = [p.strip() for p in line.split(",")]
            time_groups.append(
                FishTimeGroup(
                    # encounter percent chance is filled in later
                    daytime_encounter=PokemonEncounterRate(pokemon_name=parts[0], level=int(parts[1]), percent_chance=0),
                    nighttime_encounter=PokemonEncounterRate(pokemon_name=parts[2], level=int(parts[3]), percent_chance=0),
                )
            )

        with open(output_filename, "w") as output_file:
            writer = csv.writer(output_file)

            writer.writerow(["In Pokemon GSC, fishing encounters are defined by group, not by specific route"])
            writer.writerow(["To see which group corresponds to which route, see here:"])
            writer.writerow(["https://bulbapedia.bulbagarden.net/wiki/Fishing#Generation_II"])
            writer.writerow([])

            for fish_group in fish_groups:
                fish_group.write_to_csv(writer, time_groups)

from __future__ import annotations

from collections import defaultdict
import csv
import os
from typing import AnyStr
from typing import Dict
from typing import DefaultDict
from typing import IO
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import attr


BALANCED_STAT_PATH = "/home/neil/Projects/pokecrystal/data/pokemon/base_stats"
ORIGINAL_STAT_PATH = (
    "/home/neil/Projects/crystalpyenv/pokecrystal/data/pokemon/base_stats"
)


@attr.s
class Pokemon:
    name = attr.ib(type=str)
    # each string in this list has the evolution method followed by
    # level, item, or other method
    evolutions = attr.ib(type=List[str], factory=list)
    # map of level to all moves learned at that level
    levelup_moves = attr.ib(
        type=DefaultDict[int, Set], factory=lambda: defaultdict(set)
    )
    # tuple of stats
    # hp, atk, def, speed, satk, sdef
    stats = attr.ib(type=List[int], factory=list)
    # types
    type1 = attr.ib(type=str, factory=str)
    type2 = attr.ib(type=str, factory=str)
    tm_list = attr.ib(type=Set[str], factory=set)

    def add_evolution(self, method: str) -> None:
        method_list = method.split(",")
        # this is the only method with three additional params
        # so we group together the level and evolution condition
        if method_list[0] == "EVOLVE_STAT":
            method_list = [
                method_list[0],
                method_list[1] + "/" + method_list[2],
                method_list[3],
            ]
        method = ",".join([ml.strip() for ml in method_list])
        self.evolutions.append(method)

    def add_levelup_moves(self, level: int, move: str) -> None:
        self.levelup_moves[level].add(move)

    def get_changed_evolutions(self, other: Pokemon) -> List[List[str]]:
        differences = set(self.evolutions) - set(other.evolutions)
        return [diff.split(",") for diff in differences]

    def get_changed_levelup_moves(self, other: Pokemon) -> Dict[int, Set]:
        changed_moves = defaultdict(set)
        for level, moves in self.levelup_moves.items():
            # if the other pokemon record doesn't learn a move at this level
            # we know all moves are changed
            if level not in other.levelup_moves:
                changed_moves[level] = moves.copy()
                continue

            for move in moves:
                if move not in other.levelup_moves[level]:
                    changed_moves[level].add(move)

        # cast to dict to avoid being given new items downstream
        return dict(changed_moves)

    @property
    def hp(self):
        return self.stats[0]

    @property
    def attack(self):
        return self.stats[1]

    @property
    def defense(self):
        return self.stats[2]

    @property
    def speed(self):
        return self.stats[3]

    @property
    def special_attack(self):
        return self.stats[4]

    @property
    def special_defense(self):
        return self.stats[5]


def clean_move_file_line(line: str) -> str:
    # remove the comments
    if ";" in line:
        line = line[: line.index(";")]

    # remove whitespace
    line = line.strip()

    # remove things that aren't stats
    if line.startswith("INCLUDE") or line.startswith("SECTION"):
        line = ""

    return line

def clean_name(name: str) -> str:
    if name == "PSYCHIC_TYPE" or name == "PSYCHIC_M":
        return "Psychic"
    return " ".join(name.split("_")).title()


def get_evolution(file: IO[AnyStr]) -> Optional[str]:
    # remove the assembly syntax
    line = ""
    while line == "":
        line = clean_move_file_line(next(iter(file.readline, "")))
    line = line.replace("db", "").strip()

    if line == "0":
        return None  # no evolution

    return ",".join([l.strip() for l in line.split(",")])


def get_move(file: IO[AnyStr]) -> Tuple[Optional[int], Optional[str]]:
    # remove the assembly syntax
    line = ""
    while line == "":
        line = clean_move_file_line(next(iter(file.readline, "")))
    line = line.replace("db", "").strip()

    if line == "0":
        return None, None  # no more moves

    level_str, move = line.split(",")
    level = int(level_str)
    move = move.strip()

    return level, move


def get_pokemon_name_from_file(file: IO[AnyStr]) -> str:
    line = ""
    while line == "":
        line = clean_move_file_line(next(iter(file.readline, "")))

    pokemon_entry_suffix = "EvosAttacks:"
    if pokemon_entry_suffix not in line:
        raise ValueError(f"Line {line} is not a pokemon entry")

    return line.replace(pokemon_entry_suffix, "")


def parse_files(
    original_file: IO[AnyStr], new_file: IO[AnyStr]
) -> Tuple[List[Pokemon], List[Pokemon]]:
    original_pokemon_list = []
    new_pokemon_list = []

    while True:
        try:
            original_file_pokemon_name = get_pokemon_name_from_file(original_file)
            new_file_pokemon_name = get_pokemon_name_from_file(new_file)
        except StopIteration:
            break

        if original_file_pokemon_name != new_file_pokemon_name:
            raise ValueError(
                f"Pokemon name mismatch {original_file_pokemon_name} != {new_file_pokemon_name}"
            )

        original_pokemon = Pokemon(name=original_file_pokemon_name)
        new_pokemon = Pokemon(name=new_file_pokemon_name)

        evolution = get_evolution(original_file)
        while evolution is not None:
            original_pokemon.add_evolution(evolution)
            evolution = get_evolution(original_file)

        evolution = get_evolution(new_file)
        while evolution is not None:
            new_pokemon.add_evolution(evolution)
            evolution = get_evolution(new_file)

        level, move = get_move(original_file)
        while level is not None and move is not None:
            original_pokemon.add_levelup_moves(level, move)
            level, move = get_move(original_file)

        level, move = get_move(new_file)
        while level is not None and move is not None:
            new_pokemon.add_levelup_moves(level, move)
            level, move = get_move(new_file)

        original_pokemon_list.append(original_pokemon)
        new_pokemon_list.append(new_pokemon)

        stats_filename = get_base_stats_filename(original_pokemon.name)
        original_pokemon_file = os.path.join(ORIGINAL_STAT_PATH, stats_filename)
        new_pokemon_file = os.path.join(BALANCED_STAT_PATH, stats_filename)

        populate_pokemon_stats_type_tms(original_pokemon_file, original_pokemon)
        populate_pokemon_stats_type_tms(new_pokemon_file, new_pokemon)

    return original_pokemon_list, new_pokemon_list


def generate_change_file(
    old_pokemon_list: List[Pokemon], new_pokemon_list: List[Pokemon]
) -> None:
    with open("poke_changes.csv", "w") as f:
        writer = csv.writer(f)
        for original_pokemon, new_pokemon in zip(old_pokemon_list, new_pokemon_list):
            if original_pokemon.name != new_pokemon.name:
                raise ValueError(
                    f"Pokemon name mismatch {original_pokemon.name} != {new_pokemon.name}"
                )

            writer.writerow([original_pokemon.name, "-" * 10, "-" * 10, "-" * 10])

            generate_evolution_changes(writer, original_pokemon, new_pokemon)
            generate_move_changes(writer, original_pokemon, new_pokemon)
            generate_type_changes(writer, original_pokemon, new_pokemon)
            generate_stat_changes(writer, original_pokemon, new_pokemon)
            generate_tm_list_change(writer, original_pokemon, new_pokemon)


def generate_evolution_changes(
    writer: csv.writer, original_pokemon: Pokemon, new_pokemon: Pokemon
) -> None:
    removals = original_pokemon.get_changed_evolutions(new_pokemon)
    additions = new_pokemon.get_changed_evolutions(original_pokemon)

    # make sure the two lists have equal number of columns to properly format the output
    while len(additions) > len(removals):
        removals.append(["", "", ""])
    while len(removals) > len(additions):
        additions.append(["", "", ""])

    assert len(additions) == len(removals)

    if not additions and not removals:
        return

    writer.writerow(["Evolutions"])
    writer.writerow(["Original:", "", "", "New:"])
    for rem, add in zip(removals, additions):
        writer.writerow(rem + add)
    writer.writerow([""])


def generate_move_changes(
    writer: csv.writer, original_pokemon: Pokemon, new_pokemon: Pokemon
) -> None:
    removal_pairs = original_pokemon.get_changed_levelup_moves(new_pokemon)
    addition_pairs = new_pokemon.get_changed_levelup_moves(original_pokemon)

    removals = []
    additions = []
    for level, moves in sorted(removal_pairs.items()):
        for move in moves:
            removals.append([str(level), move])

    for level, moves in sorted(addition_pairs.items()):
        for move in moves:
            additions.append([str(level), move])

    # make sure the two lists have equal number of columns to properly format the output
    while len(additions) > len(removals):
        removals.append(["", ""])
    while len(removals) > len(additions):
        additions.append(["", ""])

    assert len(additions) == len(removals)

    if not additions and not removals:
        return

    writer.writerow(["Moves"])
    writer.writerow(["Original:", "", "New:"])
    for rem, add in zip(removals, additions):
        writer.writerow(rem + add)
    writer.writerow([""])


def generate_type_changes(
    writer: csv.writer, original_pokemon: Pokemon, new_pokemon: Pokemon
) -> None:
    original_types = {original_pokemon.type1, original_pokemon.type2}
    new_types = {new_pokemon.type1, original_pokemon.type2}
    if original_types == new_types:
        return

    writer.writerow(["Types"])
    writer.writerow(["Original:", "", "New:"])
    writer.writerow(
        [
            original_pokemon.type1,
            original_pokemon.type2
            if original_pokemon.type2 != original_pokemon.type1
            else "",
            new_pokemon.type1,
            new_pokemon.type2 if new_pokemon.type2 != new_pokemon.type1 else "",
        ]
    )
    writer.writerow([""])


def generate_stat_changes(
    writer: csv.writer, original_pokemon: Pokemon, new_pokemon: Pokemon
) -> None:
    original_stats = (
        original_pokemon.hp,
        original_pokemon.attack,
        original_pokemon.defense,
        original_pokemon.special_attack,
        original_pokemon.special_defense,
        original_pokemon.speed,
    )
    new_stats = (
        new_pokemon.hp,
        new_pokemon.attack,
        new_pokemon.defense,
        new_pokemon.special_attack,
        new_pokemon.special_defense,
        new_pokemon.speed,
    )

    if original_stats == new_stats:
        return

    writer.writerow(["Stats"])
    writer.writerow(["", "Original:", "", "New:"])
    writer.writerow(
        [
            "HP",
            original_pokemon.hp,
            "->" if original_pokemon.hp != new_pokemon.hp else "",
            new_pokemon.hp,
        ]
    )
    writer.writerow(
        [
            "Attack",
            original_pokemon.attack,
            "->" if original_pokemon.attack != new_pokemon.attack else "",
            new_pokemon.attack,
        ]
    )
    writer.writerow(
        [
            "Defense",
            original_pokemon.defense,
            "->" if original_pokemon.defense != new_pokemon.defense else "",
            new_pokemon.defense,
        ]
    )
    writer.writerow(
        [
            "Special Attack",
            original_pokemon.special_attack,
            "->"
            if original_pokemon.special_attack != new_pokemon.special_attack
            else "",
            new_pokemon.special_attack,
        ]
    )
    writer.writerow(
        [
            "Special Defense",
            original_pokemon.special_defense,
            "->"
            if original_pokemon.special_defense != new_pokemon.special_defense
            else "",
            new_pokemon.special_defense,
        ]
    )
    writer.writerow(
        [
            "Speed",
            original_pokemon.speed,
            "->" if original_pokemon.speed != new_pokemon.speed else "",
            new_pokemon.speed,
        ]
    )
    writer.writerow([""])


def generate_tm_list_change(
    writer: csv.writer, original_pokemon: Pokemon, new_pokemon: Pokemon
) -> None:
    original_tm_list = set(original_pokemon.tm_list)
    new_tm_list = set(new_pokemon.tm_list)

    added_tms = new_tm_list - original_tm_list

    if not added_tms:
        return

    writer.writerow(["New TM/HM/Move Tutors"])
    for tm in added_tms:
        writer.writerow([clean_name(tm)])
    writer.writerow([""])


def get_base_stats_filename(pokemon_name: str) -> str:
    # the original name comes from evos_attacks.asm so no special chars
    pokemon_name = pokemon_name.lower()

    for filename in os.listdir(BALANCED_STAT_PATH):
        cleaned_filename = filename.replace("_", "").replace(".asm", "")
        if cleaned_filename == pokemon_name:
            return filename

    raise Exception(f"Could not find filename for {pokemon_name}")


def populate_pokemon_stats_type_tms(pokemon_filepath: str, pokemon: Pokemon) -> None:
    with open(pokemon_filepath) as file:
        # name line
        file.readline()
        # blank
        file.readline()

        stats_line = file.readline().strip().replace(" ", "").replace("db", "")
        stats = stats_line.split(",")
        pokemon.stats = [int(i) for i in stats]

        # comments
        file.readline()
        # blank
        file.readline()

        types_line = (
            file.readline()
            .strip()
            .replace(" ", "")
            .replace("db", "")
            .replace(";type", "")
        )
        pokemon.type1, pokemon.type2 = types_line.split(",")

        # other stuff we don't need
        [file.readline() for _ in range(13)]

        tm_list = file.readline().strip().replace(" ", "").replace("tmhm", "")
        pokemon.tm_list = tm_list.split(",")


def generate_comparison_files() -> None:
    # TODO make this accept user input
    original_file = (
        "/home/neil/Projects/crystalpyenv/pokecrystal/data/pokemon/evos_attacks.asm"
    )
    new_file = "/home/neil/Projects/pokecrystal/data/pokemon/evos_attacks.asm"
    with open(original_file) as orig, open(new_file) as new:
        old_pokemon_list, new_pokemon_list = parse_files(orig, new)

    generate_change_file(old_pokemon_list, new_pokemon_list)


if __name__ == "__main__":
    generate_comparison_files()

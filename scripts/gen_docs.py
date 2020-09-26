from __future__ import annotations

from collections import defaultdict
import csv
from typing import AnyStr
from typing import Dict
from typing import DefaultDict
from typing import IO
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import attr


@attr.s
class Pokemon:
    name = attr.ib(type=str)
    # each string in this list has the evolution method followed by
    # level, item, or other method
    evolutions = attr.ib(type=Set[str], factory=(list))
    # map of level to all moves learned at that level
    levelup_moves = attr.ib(
        type=DefaultDict[int, Set], factory=lambda: defaultdict(set)
    )

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
        differences = (set(self.evolutions) - set(other.evolutions))
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

    return original_pokemon_list, new_pokemon_list


def generate_evolution_file(
    old_pokemon_list: List[Pokemon], new_pokemon_list: List[Pokemon]
) -> None:
    with open("evolution_changes.csv", "w") as f:
        writer = csv.writer(f)
        for old_pokemon, new_pokemon in zip(old_pokemon_list, new_pokemon_list):
            if old_pokemon.name != new_pokemon.name:
                raise ValueError(
                    f"Pokemon name mismatch {old_pokemon.name} != {new_pokemon.name}"
                )

            removals = old_pokemon.get_changed_evolutions(new_pokemon)
            additions = new_pokemon.get_changed_evolutions(old_pokemon)

            # make sure the two lists have equal number of columns to properly format the output
            while len(additions) > len(removals):
                removals.append(["","",""])
            while len(removals) > len(additions):
                additions.append(["","",""])

            assert len(additions) == len(removals)

            if not additions and not removals:
                continue

            writer.writerow([old_pokemon.name])
            writer.writerow(["Original:", "", "", "New:", "", ""])
            for rem, add in zip(removals, additions):
                writer.writerow(rem + add)
            writer.writerow([""])


def generate_move_changes_file(
    old_pokemon_list: List[Pokemon], new_pokemon_list: List[Pokemon]
) -> None:
    with open("move_changes.csv", "w") as f:
        writer = csv.writer(f)
        for old_pokemon, new_pokemon in zip(old_pokemon_list, new_pokemon_list):
            if old_pokemon.name != new_pokemon.name:
                raise ValueError(
                    f"Pokemon name mismatch {old_pokemon.name} != {new_pokemon.name}"
                )

            removal_pairs = old_pokemon.get_changed_levelup_moves(new_pokemon)
            addition_pairs = new_pokemon.get_changed_levelup_moves(old_pokemon)

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
                removals.append(["",""])
            while len(removals) > len(additions):
                additions.append(["",""])

            assert len(additions) == len(removals)

            if not additions and not removals:
                continue

            writer.writerow([old_pokemon.name])
            writer.writerow(["Original:", "", "New:", ""])
            for rem, add in zip(removals, additions):
                writer.writerow(rem + add)
            writer.writerow([""])


def generate_comparison_files() -> None:
    # TODO make this accept user input
    original_file = (
        "/home/neil/Projects/crystalpyenv/pokecrystal/data/pokemon/evos_attacks.asm"
    )
    new_file = "/home/neil/Projects/pokecrystal/data/pokemon/evos_attacks.asm"
    with open(original_file) as orig, open(new_file) as new:
        old_pokemon_list, new_pokemon_list = parse_files(orig, new)

    generate_evolution_file(old_pokemon_list, new_pokemon_list)
    generate_move_changes_file(old_pokemon_list, new_pokemon_list)


if __name__ == "__main__":
    generate_comparison_files()

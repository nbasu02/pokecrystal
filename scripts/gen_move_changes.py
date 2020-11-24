import csv

import attr
from typing import Dict
from typing import IO

from util import clean_name

@attr.s
class MoveAttributes:
    effect = attr.ib(type=str)
    base_power = attr.ib(type=int)
    type_ = attr.ib(type=str)
    accuracy = attr.ib(type=int)
    pp = attr.ib(type=int)
    effect_chance = attr.ib(type=int)

    def _as_tuple(self):
        return (
            self.effect,
            self.base_power,
            self.type_,
            self.accuracy,
            self.pp,
            self.effect_chance,
        )

    def __eq__(self, other):
        return self._as_tuple() == other._as_tuple()

# dict of move names to their attributes
Moves = Dict[str, MoveAttributes]

def cleanup_line(line: str):
    return line.replace("move", "").strip()

def get_moves_from_file(file: IO) -> Moves:
    moves = {}

    for line in file.readlines():
        if not line or not line.strip().startswith("move"):
            continue
        if "MACRO" in line:
            continue

        line = cleanup_line(line)
        name, effect, base_power, type_, accuracy, pp, effect_chance = [l.strip() for l in line.split(",")]
        name = clean_name(name)
        effect = clean_name(effect.replace("EFFECT_", ""))
        type_ = clean_name(type_)

        moves[name] = MoveAttributes(effect, int(base_power), type_, int(accuracy), int(pp), int(effect_chance))
    return moves

def compare_move_changes():
    with open("/home/neil/Projects/crystalpyenv/pokecrystal/data/moves/moves.asm") as f:
        old_moves = get_moves_from_file(f)

    with open("/home/neil/Projects/pokecrystal/data/moves/moves.asm") as f:
        new_moves = get_moves_from_file(f)

    with open("moves.csv", "w") as outfile:
        writer = csv.writer(outfile)
        for move_name, new_move in new_moves.items():
            old_move = old_moves[move_name]

            if old_move == new_move:
                continue

            writer.writerow([move_name, "-" * 10, "-" * 10, "-" * 10])
            writer.writerow(["", "Original:", "", "New:"])
            writer.writerow(["Effect:", old_move.effect, "" if old_move.effect == new_move.effect else "->", new_move.effect])
            writer.writerow(["Base Power:", old_move.base_power, "" if old_move.base_power == new_move.base_power else "->", new_move.base_power])
            writer.writerow(["Type:", old_move.type_, "" if old_move.type_ == new_move.type_ else "->", new_move.type_])
            writer.writerow(["Accuracy:", old_move.accuracy, "" if old_move.accuracy == new_move.accuracy else "->", new_move.accuracy])
            writer.writerow(["PP:", old_move.pp, "" if old_move.pp == new_move.pp else "->", new_move.pp])
            writer.writerow(["Effect % Chance:", old_move.effect_chance, "" if old_move.effect_chance == new_move.effect_chance else "->", new_move.effect_chance])
            writer.writerow([""])

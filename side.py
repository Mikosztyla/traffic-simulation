from enum import Enum


class Side(Enum):
    S = "S"
    N = "N"
    E = "E"
    W = "W"

RIGHT = {
    Side.N: Side.W,
    Side.E: Side.N,
    Side.S: Side.E,
    Side.W: Side.S
}

LEFT = {
    Side.N: Side.E,
    Side.W: Side.N,
    Side.S: Side.W,
    Side.E: Side.S
}

OPPOSITE = {
    Side.N: Side.S,
    Side.S: Side.N,
    Side.E: Side.W,
    Side.W: Side.E
}
import random
from string import Template
from enum import Enum

# Knitout command templates
header_template = Template(';!knitout-2\n;;Carriers: $carrier\n')
tuck_template = Template('tuck $direction $bed$hook $carrier\n')
knit_template = Template('knit $direction $bed$hook $carrier\n')
outhook_template = Template('outhook $carrier\n')
inhook_template = Template('inhook $carrier\n')
releasehook_template = Template('releasehook $carrier\n')


class Bed(Enum):
    FRONT = "f"
    BACK = "b"


class Direction(Enum):
    LtR = "+"
    RtL = "-"


def cast_on(width: int, carrier: int = 3, bed: Bed = Bed.FRONT):
    """Casts on a row of stitches.

    Args:
        width (int): The number of stitches to cast on.
        carrier (int, optional): The yarn carrier to use. Defaults to 3.
        bed (Bed, optional): Which bed to use. Defaults to "f" (front bed).
    """
    # Hook yarn from appropriate carrier on the yarn inserting hook
    k_code = inhook_template.substitute(carrier=carrier)

    # Starts at the furthest hook and tucks right to left on every other needle
    for hook in range(width, 0, -2):
        k_code += tuck_template.substitute(
            direction=Direction.RtL.value,
            bed=bed.value,
            hook=hook,
            carrier=carrier)

    # Returns the other direction, tucking left to right on every other needle
    for hook in range((width % 2) + 1, width, 2):
        k_code += tuck_template.substitute(
            direction=Direction.LtR.value,
            bed=bed.value,
            hook=hook,
            carrier=carrier)

    # Release the yarn inserting hook
    k_code += releasehook_template.substitute(carrier=carrier)

    return(k_code)


def knit_row(
        width: int,
        start_needle: int,
        direction: Direction,
        carrier: int,
        bed: Bed = Bed.FRONT):
    """Knits a row of stitches.

    Args:
        width (int): Number of stitches in the row
        start_needle (int): Needle to start the row on
        direction (Direction): Direction of knitting
        carrier (int): The ID of the yarn carrier to use
        bed (Bed, optional): The bed to knit the row of stitches on. Defaults to Bed.FRONT.
    """

    k_code = ''

    if direction == Direction.RtL:
        hooks = range(start_needle, start_needle - width, -1)
    elif direction == Direction.LtR:
        hooks = range(start_needle, start_needle + width)

    for hook in hooks:
        k_code += knit_template.substitute(
            direction=direction.value,
            bed=bed.value,
            hook=hook,
            carrier=carrier)

    return(k_code)


def stockinette(
        width: int,
        num_rows: int,
        carrier: int = 3,
        filename: str = "stockinette"):
    """Function for generating knitout code for a stockinette swatch.

    Args:
        width (int): Number of columns.
        rows (int): Number of rows
        carrier (int, optional): Yarn carrier to use. Defaults to 3.
        filename (str, optional): Filename to save the knitout code to. Defaults to "stockinette".
    """

    # Create header and cast on
    k_code = header_template.substitute(carrier=carrier)
    k_code += cast_on(width)

    # Knit the rest of the rows, alternating directions
    for i in range(num_rows - 1):
        if (i % 2):
            k_code += knit_row(width, 1, Direction.LtR, carrier)
        else:
            k_code += knit_row(width, width, Direction.RtL, carrier)

    # Outhook
    k_code += outhook_template.substitute(carrier=carrier)

    # Write to file
    f = open("{}.k".format(filename), "w")
    f.write(k_code)
    f.close()

    return


if __name__ == "__main__":
    stockinette(random.randint(10, 20), random.randint(10, 20))
    # stockinette(16, 16, filename="swatch16")

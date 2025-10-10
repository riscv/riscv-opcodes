import logging
import pprint
from typing import Dict, List, NamedTuple

from rv_colors import palette
from shared_utils import InstrDict, instr_dict_2_extensions

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


class RectangleDimensions(NamedTuple):
    x: float
    y: float
    w: float
    h: float


class InstrRectangle(NamedTuple):
    dims: RectangleDimensions
    extension: str
    label: str


InstrDimsDict = Dict[str, RectangleDimensions]


def encoding_to_rect(encoding: str) -> RectangleDimensions:
    """Convert a binary encoding string to rectangle dimensions."""

    def calculate_size(free_bits: int, tick: float) -> float:
        """Calculate size based on number of free bits and tick value."""
        return 2**free_bits * tick

    instr_length = len(encoding)
    # starting position
    x = 0
    y = 0
    x_tick = 1 / (2 ** (0.5 * instr_length))
    y_tick = 1 / (2 ** (0.5 * instr_length))
    x_free_bits = 0
    y_free_bits = 0
    even = encoding[0::2]
    odd = encoding[1::2]
    # Process bits from least significant to most significant
    for i, bit in enumerate(encoding):
        if bit == "1":
            offset = 0.5 / (2 ** int(i / 2))
            if i % 2 == 0:
                y += offset
            else:
                x += offset
        elif bit == "0":
            pass
            # position not adjusted on 0

    x_free_bits = odd.count("-")
    y_free_bits = even.count("-")
    x_size = calculate_size(x_free_bits, x_tick)
    y_size = calculate_size(y_free_bits, y_tick)

    # If we came here, encoding can be visualized with a single rectangle
    rectangle = RectangleDimensions(x=x, y=y, w=x_size, h=y_size)
    return rectangle


FIGSIZE = 128


def plot_image(
    instr_dict: InstrDict,
    instr_dims_dict: InstrDimsDict,
    extension_sizes: Dict[str, float],
) -> None:
    """Plot the instruction rectangles using matplotlib."""

    from matplotlib import patches
    from matplotlib import pyplot as plt

    def get_readable_font_color(bg_hex: str) -> str:
        """Determine readable font color based on background color."""

        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            """Convert hex color string to RGB tuple."""
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            return (r, g, b)

        r, g, b = hex_to_rgb(bg_hex)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "#000000" if luminance > 186 else "#FFFFFF"

    def plot_with_matplotlib(
        rectangles: list[InstrRectangle],
        colors: list[str],
        hatches: list[str],
        extensions: list[str],
    ) -> None:
        """Plot rectangles with matplotlib using specified styles."""

        _, ax = plt.subplots(figsize=(FIGSIZE, FIGSIZE), facecolor="none")  # type: ignore
        ax.set_facecolor("none")  # type: ignore
        linewidth = FIGSIZE / 100
        for dims, ext, label in rectangles:
            x, y, w, h = dims
            ext_idx = extensions.index(ext)
            color = colors[ext_idx]
            hatch = hatches[ext_idx]
            rect = patches.Rectangle(
                (x, y),
                w,
                h,
                linewidth=linewidth,
                edgecolor="black",
                facecolor=color,
                hatch=hatch,
                alpha=1.0,
            )
            ax.add_patch(rect)

            if w >= h:
                base_dim = w
                rotation = 0
            else:
                base_dim = h
                rotation = 90

            # Scale font size based on base dimension and label length
            n_chars = len(label)
            font_size = (
                base_dim / n_chars * 90 * FIGSIZE
            )  # Adjust scaling factor as needed
            if font_size > 1:
                fontdict = {
                    "fontsize": font_size,
                    "color": get_readable_font_color(color),
                    "family": "DejaVu Sans Mono",
                }
                ax.text(  # type: ignore
                    x + w / 2,
                    y + h / 2,
                    label,
                    ha="center",
                    va="center",
                    fontdict=fontdict,
                    rotation=rotation,
                )

        plt.axis("off")  # type: ignore
        plt.tight_layout()  # type: ignore
        plt.savefig("inst.svg", format="svg")  # type: ignore
        plt.show()  # type: ignore

    extensions: List[str] = sorted(
        extension_sizes.keys(), key=lambda k: extension_sizes[k], reverse=True
    )

    rectangles: List[InstrRectangle] = []
    for instr in instr_dict:
        dims = instr_dims_dict[instr]
        rectangles.append(
            InstrRectangle(
                dims=dims,
                extension=instr_dict[instr]["extension"][0],
                label=instr.replace("_", "."),
            )
        )

    # sort rectangles so that small ones are in the foreground
    # An overlap occurs e.g. for pseudo ops, and these should be on top of the encoding it reuses
    rectangles = sorted(rectangles, key=lambda x: x.dims.w * x.dims.h, reverse=True)

    colors, hatches = generate_styles(extensions)

    plot_with_matplotlib(rectangles, colors, hatches, extensions)


def generate_styles(extensions: list[str]) -> tuple[list[str], list[str]]:
    """Generate color and hatch styles for extensions."""
    n_colors = len(palette)
    colors = [""] * len(extensions)
    hatches = [""] * len(extensions)
    hatch_options = ["", "/", "\\", "|", "-", "+", "x", ".", "*"]
    color_options = list(palette.values())

    for i in range(len(extensions)):
        colors[i] = color_options[i % n_colors]
        hatches[i] = hatch_options[int(i / n_colors) % len(hatch_options)]

    return colors, hatches


def defragment_encodings(
    encodings: list[str], length: int = 32, offset: int = 0
) -> list[str]:
    """Defragment a list of binary encodings by reordering bits."""
    # determine bit position which has the most fixed bits
    fixed_encodings = ["0", "1"]
    fixed_bits = [0] * length
    fixed_encoding_indeces: Dict[str, List[int]] = {
        value: [] for value in fixed_encodings
    }
    for index, encoding in enumerate(encodings):
        for position, value in enumerate(encoding):
            if position > offset:
                if value != "-":
                    fixed_bits[position] += 1

    # find bit position with most fixed bits, starting with the LSB to favor the opcode field
    max_fixed_bits = max(fixed_bits)
    if max_fixed_bits == 0:
        # fully defragemented
        return encodings
    max_fixed_position = len(fixed_bits) - 1 - fixed_bits[::-1].index(max_fixed_bits)

    # move bit position with the most fixed bits to the front
    for index, encoding in enumerate(encodings):
        encodings[index] = (
            encoding[0:offset]
            + encoding[max_fixed_position]
            + encoding[offset:max_fixed_position]
            + encoding[max_fixed_position + 1 :]
        )

        if encoding[max_fixed_position] in fixed_encodings:
            fixed_encoding_indeces[encoding[max_fixed_position]].append(index)
        else:
            # No more fixed bits in this encoding
            pass

    if offset < length:
        # continue to defragement starting from the next offset
        offset = offset + 1

        # separate encodings
        sep_encodings: Dict[str, List[str]] = {}
        for fixed_encoding in fixed_encodings:
            sep_encodings[fixed_encoding] = [
                encodings[i] for i in fixed_encoding_indeces[fixed_encoding]
            ]
            sep_encodings[fixed_encoding] = defragment_encodings(
                sep_encodings[fixed_encoding], length=length, offset=offset
            )

            # join encodings
            for new_index, orig_index in enumerate(
                fixed_encoding_indeces[fixed_encoding]
            ):
                encodings[orig_index] = sep_encodings[fixed_encoding][new_index]

    return encodings


def defragment_encoding_dict(instr_dict: InstrDict) -> InstrDict:
    """Apply defragmentation to the encoding dictionary."""
    encodings = [instr["encoding"] for instr in instr_dict.values()]
    encodings_defragemented = defragment_encodings(encodings, length=32, offset=0)
    for index, instr in enumerate(instr_dict):
        instr_dict[instr]["encoding"] = encodings_defragemented[index]
    return instr_dict


def make_svg(instr_dict: InstrDict) -> None:
    """Generate an SVG image from instruction encodings."""
    extensions = instr_dict_2_extensions(instr_dict)
    extension_size: Dict[str, float] = {}

    instr_dict = defragment_encoding_dict(instr_dict)
    instr_dims_dict: InstrDimsDict = {}

    for ext in extensions:
        extension_size[ext] = 0

    for instr in instr_dict:
        dims = encoding_to_rect(instr_dict[instr]["encoding"])

        extension_size[instr_dict[instr]["extension"][0]] += dims.h * dims.w

        instr_dims_dict[instr] = dims

    plot_image(instr_dict, instr_dims_dict, extension_size)

import re
import Pcolors

colors = {
    str: {"style": Pcolors.style("green"), "prefix": "'", "suffix": "'"},
    int: {"style": Pcolors.style("yellow"), "prefix": "", "suffix": ""},
    float: {"style": Pcolors.style("lyellow"), "prefix": "", "suffix": ""},
    type(None): {"style": Pcolors.style("lblack"), "prefix": "", "suffix": ""},
    bool: {"style": Pcolors.style("magenta"), "prefix": "", "suffix": ""},
    "function": {
        "style": Pcolors.style("blue"),
        "prefix": "[Function: ",
        "suffix": "]",
    },
    "esc": {"style": Pcolors.style("red"), "prefix": "\\", "suffix": ""},
    "other": {
        "style": Pcolors.style("blue"),
        "prefix": "[",
        "suffix": "]",
    },
}


class Config:
    parse_keys = False
    simple_objects = True
    max_depth = 2


def _colorize_esc(s, style: Pcolors.style):
    escapes = {"\a": "\\a", "\b": "\\b", "\f": "\\f", "\\r": "\\r", "\n": "\\n"}
    attrs = colors["esc"]
    code = style.get_code()
    for es in escapes.keys():
        r = (
            Pcolors.cget(
                attrs["prefix"] + escapes[es] + attrs["suffix"],
                style=attrs["style"],
                end="",
            )
            + code
        )
        s = re.sub(es, r, s)
    return code + s + Pcolors.cget("", fg_color=0, end="")


def _colorize(obj, parse_esc=True):
    cls = obj.__class__
    if cls in colors:
        attrs = colors[cls]
        if parse_esc:
            return _colorize_esc(
                attrs["prefix"] + str(obj) + attrs["suffix"], style=attrs["style"]
            )
        else:
            return Pcolors.cget(
                attrs["prefix"] + str(obj) + attrs["suffix"],
                style=attrs["style"],
                end="",
            )
    if callable(obj):
        attrs = colors["function"]
        return Pcolors.cget(
            attrs["prefix"] + str(obj.__name__) + attrs["suffix"],
            style=attrs["style"],
            end="",
        )
    else:
        attrs = colors["other"]
        if Config.simple_objects:
            return Pcolors.cget(
                attrs["prefix"] + str(obj.__class__.__name__) + attrs["suffix"],
                style=attrs["style"],
                end="",
            )
        else:
            return Pcolors.cget(
                str(obj.__class__),
                style=attrs["style"],
                end="",
            )


def _parse_obj(obj: dict, indent=2, max_depth=4, level=0):
    f = "{\n" if obj.__class__ == dict else "[\n"
    tab = " " * indent
    base_key, key, value = "", "", ""
    for item in obj.items() if obj.__class__ == dict else obj:
        base_value = item
        base_key, key, value = "", "", ""
        if obj.__class__ == dict:
            base_key, base_value = base_value
            key = _colorize(base_key) if Config.parse_keys else str(base_key)
        if base_value.__class__ in (dict, list):
            if level <= max_depth or max_depth == -1:
                value = _parse_obj(
                    base_value, indent=indent, max_depth=max_depth, level=level + 1
                )
            else:
                value = _colorize(base_value)
        else:
            value = _colorize(base_value)
        if key:
            f += tab * (level + 1) + key + ": " + value + ",\n"
        else:
            f += tab * (level + 1) + value + ",\n"

    return f + tab * level + ("}" if key else "]")


def log(*objects, divider=" ", indent=2, parse_esc=True, max_depth=4):
    final = ""
    for obj in objects:
        if obj.__class__ in (dict, list):
            final += _parse_obj(obj, indent=indent, max_depth=max_depth - 1) + divider
        else:
            final += _colorize(obj, parse_esc=parse_esc) + divider
    print(final)


if __name__ == "__main__":
    import json
    import urllib.request

    data = input("paste valid json here, leave empty for dummy data:")
    if not data:
        data = {
            "users": [
                {
                    "name": "Clementina DuBuque",
                    "address": {
                        "street": "Kattie Turnpike",
                        "suite": "Suite 198",
                        "city": "Lebsackbury",
                        "zipcode": "31428-2261",
                        "geo": {
                            "lat": -38.2386,
                            "lng": 57.2232,
                        },
                    },
                    "bio": "Lorem ipsum dolor sit amet, consectetur adipiscing\n elit. Quisque sed nisl el\rementum erat pellentesque \tscelerisque. Maecenas euismod eros eget lectus tempor placerat. Sed fermentum arcu non nulla dapibus maximus. In nisi justo, ullamcorper a nisi sed, venenatis cursus nunc. In et elit lectus. Cras ullamcorper, nulla nec lobortis varius, ante nulla venenatis diam, pulvinar finibus massa tellus vel ex. Nam quis lacinia odio. ",
                    "age": 15,
                    "boy": True,
                    "friend": ["David", "Delphine", "Kurtis"],
                }
            ],
            "display": print,
            "config": Config(),
        }
    else:
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            print("bad json!")
            exit(1)

    log(data, max_depth=2)

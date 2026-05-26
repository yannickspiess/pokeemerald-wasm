#!/usr/bin/env python3
import pathlib
import re

SOURCE = pathlib.Path('data/text/birch_speech.inc')
OUTPUT = pathlib.Path('build/wasm/generated_text.c')
LABEL = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)::\s*$')
STRING = re.compile(r'^\s*\.string\s+"(.*)"\s*$')


def parse_strings():
    current = None
    strings = []
    for line in SOURCE.read_text().splitlines():
        label = LABEL.match(line)
        if label:
            if current:
                yield current, strings
            current = label.group(1)
            strings = []
            continue

        string = STRING.match(line)
        if current and string:
            strings.append(string.group(1))

    if current:
        yield current, strings


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    lines = ['#include "global.h"', '']
    for label, strings in parse_strings():
        literal = ''.join('"' + s + '"' for s in strings)
        lines.append(f'const u8 {label}[] = _({literal});')
    OUTPUT.write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

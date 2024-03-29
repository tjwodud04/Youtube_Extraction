import re
from typing import NamedTuple

_INDEX_LINE = re.compile('\s*(\d+)\s*')

class IndexedSubtitle(NamedTuple):
    index: int
    text: str

def parse_indexed_subtitles(text: str):
    """
    Parse a string containing indexed subtitles with no time information.

    Args:
        text: A string containing indexed subtitles.
    """
    subtitle_index = None
    subtitle_text = []
    
    for line in text.splitlines():
        match = re.fullmatch(_INDEX_LINE, line)

        if match:
            if subtitle_index is not None:
                yield IndexedSubtitle(subtitle_index, '\n'.join(subtitle_text))
                
            subtitle_index = int(match.group(1))
            subtitle_text.clear()
        else:
            subtitle_text.append(line)
    
    if subtitle_index is not None:
        yield IndexedSubtitle(subtitle_index, '\n'.join(subtitle_text))

def indexed_subtitles_to_text(subtitles):
    """
    Convert a list of indexed subtitles to a string.

    Args:
        subtitles: A list of indexed subtitles.
    """
    return '\n\n'.join(f'{subtitle.index}\n{subtitle.text}' for subtitle in subtitles)

if __name__ == '__main__':
    text = '''1
    First line

    2
    Second line

    3
    Third line'''

    subs = list(parse_indexed_subtitles(text))

    for subtitle in subs:
        print(subtitle)

    print(indexed_subtitles_to_text(subs))
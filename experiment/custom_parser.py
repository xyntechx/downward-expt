import logging
import re

from lab.parser import Parser


class CommonParser(Parser):
    def add_repeated_pattern(
        self, name, regex, file="run.log", required=False, type=int
    ):
        def find_all_occurences(content, props):
            matches = re.findall(regex, content)
            if required and not matches:
                logging.error(f"Pattern {regex} not found in file {file}")
            props[name] = [type(m) for m in matches]

        self.add_function(find_all_occurences, file=file)

    def add_bottom_up_pattern(
        self, name, regex, file="run.log", required=False, type=int
    ):
        def search_from_bottom(content, props):
            reversed_content = "\n".join(reversed(content.splitlines()))
            match = re.search(regex, reversed_content)
            if required and not match:
                logging.error(f"Pattern {regex} not found in file {file}")
            if match:
                props[name] = type(match.group(1))

        self.add_function(search_from_bottom, file=file)


def get_parser():
    parser = CommonParser()
    parser.add_pattern(
        "solution_search_time",
        r"\[t=.+s, \d+ KB\] Search time: (.+)s",
        type=float,
    )
    parser.add_pattern(
        "solution_total_time",
        r"\[t=.+s, \d+ KB\] Total time: (.+)s",
        type=float,
    )
    parser.add_pattern(
        "initial_h_value",
        r"f = (\d+) \[1 evaluated, 0 expanded, t=.+s, \d+ KB\]",
        type=int,
    )
    parser.add_repeated_pattern(
        "h_values",
        r"New best heuristic value for .+: (\d+)\n",
        type=int,
    )
    parser.add_pattern(
        "macro_search_time",
        r"\[t=.+s, \d+ KB\] Macro learning search time: (.+)s",
        type=float
    )
    parser.add_pattern(
        "macro_total_time",
        r"\[t=.+s, \d+ KB\] Macro learning total time: (.+)s",
        type=float
    )
    parser.add_pattern(
        "planner_exit_code",
        r"search_solution exit code: (.+)\n",
        type=int,
        file="driver.log",
        required=True
    )
    return parser

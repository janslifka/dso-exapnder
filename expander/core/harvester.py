import re


class Harvester:
    def __init__(self, file):
        self.file = file

    def harvest(self):
        try:
            with open(self.file, 'r') as file:
                lines = file.read().split('\n')
                return self._harvest(lines)
        except FileNotFoundError:
            return {}

    def _harvest(self, lines):
        harvested = {}

        pattern_start = '// <custom-(.*)>'
        current_key = None
        current_list = []
        for line in lines:
            if current_key and re.match('\\s*// </custom-{}>'.format(current_key), line):
                harvested[current_key] = '\n'.join(current_list)
                current_key = None
                current_list = None

            if current_key:
                current_list.append(line)

            match = re.search(pattern_start, line)
            if match:
                current_key = match.group(1)
                current_list = []

        return harvested

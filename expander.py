import re
from urllib.parse import urlsplit

import stringcase
from jinja2 import Template
from rdflib import Graph, RDF, Namespace, Literal, URIRef

DSO = Namespace('http://www.semanticweb.org/janslifka/ontologies/2019/9/design-system-ontology#')


class DSLoader:
    TYPES = [
        ('colors', DSO.Color),
        ('measures', DSO.Measure),
        ('textStyles', DSO.TextStyle),
        ('borders', DSO.Border),
        ('colorFills', DSO.ColorFill),
        ('innerShadows', DSO.InnerShadow),
        ('outerShadows', DSO.OuterShadow),
        ('elements', DSO.Element),
    ]

    def __init__(self, file):
        self.file = file

    def load(self):
        g = Graph()
        try:
            g.parse(self.file)
        except FileNotFoundError:
            pass
        return self._load(g)

    def _load(self, g):
        def wrap(value):
            return sorted(map(Wrapper.with_graph(g), g.subjects(RDF.type, value)), key=lambda i: i.name)

        return {key: wrap(value) for (key, value) in self.TYPES}


class Wrapper:
    def __init__(self, entity, graph):
        self.entity = entity
        self.graph = graph

    @property
    def name(self):
        return self.get_name(self.entity)

    def __getattr__(self, name):
        return self.get_data_property(self.entity, DSO[name])

    def get_data_property(self, subject, predicate, default=None):
        for obj in self.graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                return obj.value
            elif isinstance(obj, URIRef):
                return self.get_name(obj)
        return default

    @staticmethod
    def with_graph(graph):
        return lambda entity: Wrapper(entity, graph)

    @staticmethod
    def get_name(subject):
        return stringcase.spinalcase(urlsplit(subject).fragment)


class Harvester:
    def __init__(self, file):
        self.file = file

    def harvest(self):
        with open(self.file, 'r') as file:
            lines = file.read().split('\n')
            return self._harvest(lines)

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


class Expander:
    TEMPLATE_FILE = 'template.scss.jinja2'

    def __init__(self, input_file, output_file):
        self.ds_loader = DSLoader(input_file)
        self.harvester = Harvester(output_file)
        self.output_file = output_file

    def expand(self):
        data = self.get_data()

        with open(self.TEMPLATE_FILE) as file:
            template = Template(file.read())

        with open(self.output_file, mode='w') as file:
            file.write(template.render(**data))

    def get_data(self):
        return {
            **self.ds_loader.load(),
            'harvested': self.harvester.harvest()
        }


def main():
    input_file = '../dso/design-system-example.owl'
    output_file = 'dso.scss'
    expander = Expander(input_file, output_file)
    expander.expand()


main()

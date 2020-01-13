from urllib.parse import urlsplit

import stringcase
from rdflib import Graph, RDF, Namespace, Literal, URIRef

DSO = Namespace('http://www.semanticweb.org/janslifka/ontologies/2019/9/design-system-ontology#')


class DSLoader:
    TYPES = [
        ('colors', DSO.Color),
        ('measures', DSO.Measure),
        ('typographies', DSO.Typography),
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

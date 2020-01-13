from .harvester import Harvester
from .loader import DSLoader
from .templates import load_template


class Expander:
    def __init__(self, input_file, output_file, template):
        self.ds_loader = DSLoader(input_file)
        self.harvester = Harvester(output_file)
        self.output_file = output_file
        self.template = template

    def expand(self):
        data = self.get_data()
        template = load_template(self.template)

        with open(self.output_file, mode='w') as file:
            file.write(template.render(**data))

    def get_data(self):
        return {
            **self.ds_loader.load(),
            'harvested': self.harvester.harvest()
        }

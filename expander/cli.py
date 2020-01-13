import click

from .core.expander import Expander


@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--template', '-t', default='scss', help='Choose a template')
def main(input_file, output_file, template):
    print(f'Expanding {input_file} into {output_file} using {template}')
    expander = Expander(input_file, output_file, template)
    expander.expand()


if __name__ == '__main__':
    main()

from utils import Log, Utils
import string
import os


class ParseCVX(object):
    @classmethod
    def read_file(self, file_path):
        '''Compute a list of stripped text'''
        f = file(file_path)
        data = list(f)
        data_stripped = map(string.strip, data)
        return self.read(data_stripped)

    @classmethod
    def read(self, data):
        '''Parse a list of stripped lines
        TODO:
            - Also include constraints
        '''
        section = None
        sections = ['dimensions', 'parameters', 'variables', 'minimize', 'end']

        content = {
            'dimensions': [],
            'parameters': [],
            'variables': [],
        }

        section_dict = {
            'dimensions': self.parse_dimension,
            'parameters': self.parse_parameter,
            'variables': self.parse_parameter,
        }

        for l_num, line in enumerate(data):
            if '#' in line:
                line = line.split('#', 1)[0]

            if line == '':
                pass

            elif line.startswith('#'):
                continue

            elif (line in sections) or (section is None):
                if line == 'end':
                    section = None
                else:
                    section = line

            elif section in section_dict.keys():
                    content[section].append(section_dict[section](line))

            else:
                Log.warn("Unknown line {}: {}".format(l_num, line))

    @classmethod
    def parse_parameter(self, line):
        '''
            dimension_expr: string expression for reflecting dimension
        '''
        name, dimensions = Utils.clean_split(line, None, maxsplit=1)

        dimensions = Utils.remove_chars(dimensions, '(', ')')

        # Parse the dimension expression
        if ',' in dimensions:
            dimension_expr = dimensions.replace(',', ' *')
        else:
            dimension_expr = dimensions

        paramter = {
            'name': name,
            'dimension_expr': dimension_expr
        }

    @classmethod
    def parse_dimension(self, line):
        dim_name, dim_value = line.split('=')
        dim_value = int(dim_value)  # Explicitly convert to int

        dimension = {
            'name': dim_name,
            'value': dim_value
        }
        return dimension


if __name__ == '__main__':
    Log.verbose = True
    fpath = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(fpath, '..', 'test', 'description.cvxgen')
    print ParseCVX.read_file(test_path)
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

        return content

    @classmethod
    def parse_parameter(self, line):
        '''
            dimension_expr: string expression for reflecting dimension

        Should have used regex!
        '''
        split = Utils.clean_split(line, None, maxsplit=1)

        name, second_half = split[:2]
        Log.log("{}: Found parameter or variable".format(name))

        # Handle special structure flags
        special_features = ['psd', 'diag', 'nsd', 'diagonal']
        special = []
        for special_feature in special_features:
            if second_half.endswith(special_feature):
                special.append(special_feature)
                Log.log("{}: Registering special behavior: {}".format(name, special))
                second_half = second_half.replace(special_feature, '')

        # Handle arrays
        if '[' in name:
            name = name.split('[')[0]
            array_expr = second_half.split(', ')[-1]
            second_half = second_half.split(array_expr)[0]

            array_expr = second_half.split('=')[-1]
            lower_bound, upper_bound = array_expr.split('..')
            array_bounds = (lower_bound, upper_bound)  # Strings

        else:
            array_length = None

        dimensions = second_half

        # Handle dimension expression
        dimensions = Utils.remove_chars(dimensions, '(', ')')
        if ',' in dimensions:
            dimension_expr = dimensions.replace(',', ' *')

        else:
            dimension_expr = dimensions

        Log.log("{}: Registering dimension expression: {}".format(name, dimension_expr))

        parameter = {
            'name': name,
            'dimension_expr': dimension_expr,
            'special': special,
            'array_length': array_length,
        }
        return parameter

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
    Log.set_verbose()
    fpath = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(fpath, '..', 'test', 'description.cvxgen')
    print ParseCVX.read_file(test_path)
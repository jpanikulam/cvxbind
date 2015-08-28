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

            elif section == 'dimensions':
                content[section].append(self.parse_dimension(line))

            elif section in ['parameters', 'variables']:
                content[section].append(self.parse_parameter(line))

            else:
                Log.warn("Unknown line {}: {}".format(l_num, line))

        return content

    @classmethod
    def parse_parameter(self, line):
        '''
            dimension_expr: string expression for reflecting dimension
        TODO:  
            - Should have used regex!
            - Don't do blind text-replacement for special structure flags
        '''
        split = Utils.clean_split(line, None, maxsplit=1)
        if len(split) == 1:
            name = split[0]
            _type = 'scalar'
            return {
                'name': name,
                'dimension_expr': None,
                'special': None,
                'array_bounds': None,
                'type': _type
            }

        name, second_half = split[:2]
        Log.log("{}: Found parameter or variable".format(name))

        # Handle special structure flags
        special_features = ['psd', 'nsd', 'diagonal']
        special = []
        for special_feature in special_features:
            if special_feature in second_half:
                special.append(special_feature)
                Log.log("{}: Registering special behavior: {}".format(name, special))
                second_half = second_half.replace(special_feature, '')

        # Handle arrays
        if '[' in name:
            name = name.split('[')[0]
            array_expr = second_half.split(', ')[-1]
            second_half = second_half.split(', ' + array_expr)[0]

            array_expr = array_expr.split('=')[-1]
            lower_bound, upper_bound = array_expr.split('..')
            array_bounds = (lower_bound, upper_bound)  # Strings
            Log.log("{}: Registering array bounds expression: [{}: {}]".format(name, lower_bound, upper_bound))

        else:
            array_bounds = None

        dimensions = second_half

        # Handle dimension expression
        dimensions = Utils.remove_chars(dimensions, '(', ')')
        if ',' in dimensions:
            dimension_expr = dimensions.replace(',', ' *')
            _type = 'matrix'

        else:
            _type = 'vector'
            dimension_expr = dimensions

        Log.log("{}: Registering vector dimension expression: {}".format(name, dimension_expr))

        parameter = {
            'name': name,
            'dimension_expr': dimension_expr,
            'special': special,
            'array_bounds': array_bounds,
            'type': _type
        }
        return parameter

    @classmethod
    def parse_dimension(self, line):
        dim_name, dim_value = line.split('=')
        dim_value = int(dim_value)  # Explicitly convert to int

        Log.log("{}: Registering dimension: {}".format(dim_name, dim_value))
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
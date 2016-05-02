from utils import Log, Utils
import re
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

        for l_num, dirty_line in enumerate(data):
            Log.log("On line {}".format(l_num))

            line = dirty_line.strip()
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
                'dimensions': None,
                'special': None,
                'array_bounds': None,
                'type': _type
            }

        name, second_half = split[:2]
        Log.log("{}: Found parameter or variable".format(name))

        # Handle special structure flags
        special_features = ['psd', 'nsd', 'diagonal', 'nonnegative']
        special = set()
        for special_feature in special_features:
            if special_feature in second_half:
                special.add(special_feature)
                Log.log("{}: Registering special behavior: {}".format(name, special))
                second_half = second_half.replace(special_feature, '')

        # Handle arrays
        is_array = self.is_array(line)
        if is_array:
            array_var, name = is_array
            array_expr = second_half.split(', ')[-1]
            second_half = second_half.split(', ' + array_expr)[0]

            array_expr = array_expr.split('=')[-1]
            lower_bound, upper_bound = array_expr.split('..')
            array_bounds = (lower_bound, upper_bound)  # Strings
            Log.log("{}: Registering array bounds expression: [{}...{}]".format(name, lower_bound, upper_bound))

        else:
            array_bounds = None

        # Dimensions
        dimensions = self.get_dimensions(line)
        if dimensions is None:
            _type = 'scalar'
        elif len(dimensions) == 2:
            _type = 'matrix'
        elif len(dimensions) == 1:
            _type = 'vector'

        Log.log("{}: Registering vector dimension: {}".format(name, dimensions))

        parameter = {
            'name': name,
            'dimensions': dimensions,
            'special': special,
            'array_bounds': array_bounds,
            'type': _type
        }
        return parameter

    @classmethod
    def consume_parameter(self, line):
        # -- Array handling
        # Is it an array?
        is_array = self.is_array(line)
        if is_array is not None:

            index_var, name = is_array

            # - Check if we have an initializer, like x[0] or something
            # Required to be 't', for now
            if index_var.isdigit() or (index_var != 't'):
                is_array_initializer = True
                array_bounds = index_var
            else:
                is_array_initializer = False
                array_bounds = self.get_array_bounds(line)

            Log.log("Registering array {} with indexing variable, {}".format(name, index_var))
            if is_array_initializer:
                Log.log("{}: Is an initializer".format(name))

        # -- Not an array
        else:
            array_bounds = None
            is_array_initializer = False
            name = Utils.clean_split(line, None, maxsplit=1)[0]
            Log.log("Registering non-array {}".format(name))

        # -- Get dimensions
        dimensions = self.get_dimensions(line)
        if dimensions is None:
            _type = 'scalar'
        elif dimensions['cols'] != '1':
            _type = 'matrix'
        else:
            _type = 'vector'
        if dimensions is not None:
            Log.log("{}: Registering dimensions as {}x{}".format(name, dimensions['rows'], dimensions['cols']))
        else:
            Log.log("{}: Registering as sclar".format(name))

        special = self.get_special(line)

        parameter = {
            'name': name,
            'dimensions': dimensions,
            'array_bounds': array_bounds,
            'type': _type,
            'special': special,
            'initializer': is_array_initializer
        }
        return parameter

    @classmethod
    def get_special(self, line):
        special_features = ['psd', 'nsd', 'diagonal', 'nonnegative']
        special = set()
        for special_feature in special_features:
            if special_feature in line:
                special.add(special_feature)
                Log.log("{}: Registering special behavior: {}".format(special_feature, special))
        return special

    @classmethod
    def get_array_bounds(self, line):
        if '=' not in line:
            return None
        _, after_eq = Utils.clean_split(line, '=')
        upper, lower = Utils.clean_split(after_eq, '..')
        return (upper, lower)

    @classmethod
    def is_array(self, line):
        m = re.search(r"\[([A-Za-z0-9_]+)\]", line)
        if m is not None:
            return Utils.remove_chars(m.group(), '[', ']'), line[:m.start()].strip()
        else:
            return None

    @classmethod
    def get_dimensions(self, line):
        stripped = line.strip()
        if '(' not in stripped:
            return None
        else:
            dimensions = stripped[stripped.find("(") + 1:stripped.find(")")]
            if ',' in dimensions:
                rows, cols = Utils.clean_split(dimensions, ',')
                dimension_data = {
                    'rows': rows,
                    'cols': cols
                }
            else:
                dimension_data = {
                    'rows': dimensions.strip(), 'cols': '1'
                }

            return dimension_data

    @classmethod
    def parse_dimension(self, line):
        """Currently don't support arithmetic expressions"""
        dim_name, dim_value = Utils.clean_split(line, '=')
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

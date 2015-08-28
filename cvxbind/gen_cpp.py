from utils import Log, Utils
import string
import os


class GenCPP(object):
    '''
    TODO:
        - make_assignment_loop
        - make_function
        - copy only necessary code from CVXGEN
    '''
    @classmethod
    def line(self, indentation=0, *tokens):
        tokens = map(str, tokens)
        line = (indentation * '\t') + ' '.join(tokens) + ';\n'
        return line

    @classmethod
    def make_function_declaration(self, return_type, name, *arguments):
        argument_string = ', '.join(arguments)
        if len(argument_string) > 79:
            argument_string = '\n\t' + ',\n\t'.join(arguments)

            line = "{} {}({}\n) {{\n".format(return_type, name, argument_string)
        else:
            line = "{} {}({}) {{\n".format(return_type, name, argument_string)

        return line

    @classmethod
    def make_copy_loop(self, *variables):
        '''For all the variables of the same length'''
        out_line = '#pragma unroll\n'
        out_line += "\tfor (unsigned int ii=0; ii < ({}); ii++) {{\n".format(variables[0]['dimension_expr'])
        for var in variables:
            name = var['name']
            out_line += self.line(
                2,
                'params.{}[ii]'.format(name),
                '=',
                "boost::python::extract<double>({}[ii])".format(name)
            )
        out_line += '\t}\n'
        return out_line

    @classmethod
    def make_assignment(self, cvx_vars):
        if cvx_var['array_bounds'] is not None:
            # Deal with arrays of scalars, vectors and so on
            Log.error("Could not handle {}".format(cvx_var['name']))

        if cvx_var['dimension_expr'] is not None:
            text = self.make_copy_loop(cvx_var)

        elif cvx_var['dimension_expr'] is None:
            text = cvx_var['name'] 

        else:
            Log.warn("Did not handle {}".format(cvx_var['name']))

        return text

    @classmethod
    def make_dim_declarations(self, dimensions):
        text = ''
        for dim in dimensions:
            text += self.line(
                1,
                'const', 
                dim['name'],
                dim['value'],
            )
        return text

    @classmethod
    def make_cvx_binding(self, cvx_parsed):
        text = ''
        arguments = []
        for parameter in cvx_parsed['parameters']:
            if parameter['dimension_expr'] is None:
                arguments.append('double ' + parameter['name'])

            elif parameter['dimension_expr'] is not None:
                arguments.append('boost::python::numeric::array& ' + parameter['name'])

        text += self.make_function_declaration('boost::python::list', 'solve', *arguments)
        text += "\tset_defaults();\n\tsetup_indexing();\n\tsettings.verbose = 0;\n"
        text += self.make_dim_declarations(cvx_parsed['dimensions'])

        lengths = set(map(lambda o: o['dimension_expr'], cvx_parsed['parameters']))
        lengths -= set([None])

        # for parameter in cvx_parsed['parameters']:
        for length in lengths:
            parameters_to_assgn = filter(lambda o: o['dimension_expr'] == length, cvx_parsed['parameters'])
            text += self.make_copy_loop(*parameters_to_assgn)

        text += '}\n'


        return text

if __name__ == '__main__':
    Log.set_verbose()
    Log.log("Hello")

    print GenCPP.line(1, 2, 3)
    print GenCPP.make_function_declaration('int', 'solve', 'int poop', 'pint op')
    # print GenCPP.make_copy_loop(v)
    # print GenCPP.make_assignment({
    #         'name': 'Q',
    #         'dimension_expr': '(10)',
    #         'special': [],
    #         'array_bounds': None,
    #         'type': 'scalar'
    #     })
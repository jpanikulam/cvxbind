from cvxbind.parse_cvxgen import ParseCVX
from cvxbind.utils import Log, Utils
import unittest


class TestCvxBind(unittest.TestCase):
    def fcntest(self, func, tests):
        for test, answer in tests.items():
            response = func(test)
            self.assertEqual(
                response,
                answer,
                msg="Failed on {}:\nwanted: \n\t{}\ngot: \n\t{}".format(test, answer, response)
            )

    def test_is_array(self):
        tests = {
            "  A[t] (n, n), t=0..T": ('t', 'A'),
            "  B[t] (n, m), t=0..T": ('t', 'B'),
            "  Q_final (n, n) psd": None,
            "  R (m, m) diagonal psd": None,
            "  x[0] (n)": ('0', 'x'),
            "  u_max nonnegative": None,
        }
        self.fcntest(ParseCVX.is_array, tests)

    def test_parse_dimension(self):
        tests = {
            "  m = 3": {
                "name": "m",
                "value": 3,
            },
            "  n = 6": {
                "name": "n",
                "value": 6,
            },
            "  T = 20": {
                "name": "T",
                "value": 20,
            },
        }
        self.fcntest(ParseCVX.parse_dimension, tests)

    def test_array_bounds(self):
        tests = {
            "  A[t] (n, n), t=0..T": ('0', 'T'),
            "  B[t] (n, m), t=0..T": ('0', 'T'),
            "  Q_final (n, n) psd ": None,
            "  R (m, m) diagonal psd ": None,
            "  x[0] (n) ": None,
            "  u_max nonnegative ": None,
        }
        self.fcntest(ParseCVX.get_array_bounds, tests)

    def test_get_dimensions(self):
        # tests = {
        #     "  A[t] (n, n), t=0..T": 'n * n',
        #     "  B[t] (n, m), t=0..T": 'n * m',
        #     "  Q_final (n, n) psd": 'n * n',
        #     "  R (m, m) diagonal psd": 'm * m',
        #     "  x[0] (n)": 'n',
        #     "  u_max nonnegative": None
        # }
        tests = {
            "  A[t] (n, n), t=0..T": {
                'rows': 'n',
                'cols': 'n'
            },
            "  B[t] (n, m), t=0..T": {
                'rows': 'n',
                'cols': 'm'
            },
            "  Q_final (n, n) psd": {
                'rows': 'n',
                'cols': 'n'
            },
            "  R (m, m) diagonal psd": {
                'rows': 'm',
                'cols': 'm'
            },
            "  x[0] (n)": {
                'rows': 'n',
                'cols': '1'
            },
            "  u_max nonnegative": None
        }
        self.fcntest(ParseCVX.get_dimensions, tests)

    def test_parse_param(self):
        tests = {
            "  B[t] (n, m), t=0..T": {
                'name': 'B',
                'array_bounds': ('0', 'T'),
                'type': 'matrix',
                'dimensions': {'rows': 'n', 'cols': 'm'},
                'special': set()
            },
            "  Q_final (n, n) psd": {
                'name': 'Q_final',
                'array_bounds': None,
                'type': 'matrix',
                'dimensions': {'rows': 'n', 'cols': 'n'},
                'special': {'psd'}
            },
            "  R (m, m) diagonal psd": {
                'name': 'R',
                'array_bounds': None,
                'type': 'matrix',
                'dimensions': {'rows': 'm', 'cols': 'm'},
                'special': {'diagonal', 'psd'}
            },
            "  x[0] (n)": {
                'name': 'x',
                'array_bounds': '0',
                'type': 'vector',
                'dimensions': {'rows': 'm', 'cols': 'm'},
                'special': {'diagonal', 'psd'}
            },
            "  u_max nonnegative": {
                'name': 'u_max',
                'array_bounds': None,
                'type': 'scalar',
                'dimensions': None,
                'special': {'nonnegative'}
            }
        }

        self.fcntest(ParseCVX.parse_parameter, tests)

    def test_consume_param(self):
        tests = {
            "  B[t] (n, m), t=0..T": {
                'name': 'B',
                'array_bounds': ('0', 'T'),
                'type': 'matrix',
                'dimensions': {'rows': 'n', 'cols': 'm'},
                'special': set(),
                'initializer': False
            },
            "  Q_final (n, n) psd": {
                'name': 'Q_final',
                'array_bounds': None,
                'type': 'matrix',
                'dimensions': {'rows': 'n', 'cols': 'n'},
                'special': {'psd'},
                'initializer': False

            },
            "  R (m, m) diagonal psd": {
                'name': 'R',
                'array_bounds': None,
                'type': 'matrix',
                'dimensions': {'rows': 'm', 'cols': 'm'},
                'special': {'diagonal', 'psd'},
                'initializer': False

            },
            "  x[0] (n)": {
                'name': 'x',
                'array_bounds': '0',
                'type': 'vector',
                'dimensions': {'rows': 'n', 'cols': '1'},
                'special': set(),
                'initializer': True
            },
            "  u_max nonnegative": {
                'name': 'u_max',
                'array_bounds': None,
                'type': 'scalar',
                'dimensions': None,
                'special': {'nonnegative'},
                'initializer': False
            }
        }

        self.fcntest(ParseCVX.consume_parameter, tests)

if __name__ == '__main__':
    unittest.main()
    # Log.set_verbose()

import string
from colorama import Fore, init


class Utils(object):
    @classmethod
    def clean_split(self, text, *args, **kwargs):
        '''Apply a normal split that additionally strips each element'''
        split = string.split(text, *args, **kwargs)
        return map(string.strip, split)

    @classmethod
    def remove_chars(self, text, *args):
        for char in map(str, args):
            assert len(char) == 1, "Character '{}' is invalid".format(char)
            text = text.replace(char, '')
        return text


class Log(object):
    _verbose = False

    @classmethod
    def set_verbose(self, verbose=True):
        self._verbose = verbose

    @classmethod
    def make_str(self, *args):
        return ' '.join(map(str, args))

    @classmethod
    def log(self, *args):
        if self._verbose:
            out_txt = self.make_str(*args)
            print(Fore.BLUE + out_txt)

    @classmethod
    def warn(self, *args):
        if self._verbose:
            out_txt = self.make_str('Warning:', *args)
            print(Fore.YELLOW + out_txt)

    @classmethod
    def error(self, *args):
        out_txt = self.make_str('Error:', *args)
        print(Fore.RED + out_txt)


init(autoreset=True)


if __name__ == '__main__':
    Log.log('log', 'text')
    Log.warn('warn', 'text')
    Log.error('error', 'text')

    Log.set_verbose()
    Log.log('log', 'text')
    Log.warn('warn', 'text')
    Log.error('error', 'text')

    f = 'gello(2, 4)da'
    print Utils.remove_chars(f, '(', ')')
    print f

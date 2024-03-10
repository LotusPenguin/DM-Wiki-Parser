from datetime import datetime


class stringButBetter(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def replace(self, __old, __new, __count=-1):
        return stringButBetter(str.replace(self, __old, __new, __count))

    def replace_nth(self, __old, __new, __nth):
        arr = self.split(__old)
        i = 0
        result = ''
        for token in arr:
            i += 1
            if i < __nth:
                result += token + __old
            elif i == __nth and i < len(arr):
                result += token + __new
            elif __nth < i < len(arr):
                result += token + __old
            else:
                result += token
        return stringButBetter(result)

    def replace_nth_and_further(self, __old, __new, __nth):
        arr = self.split(__old)
        i = 0
        result = ''
        for token in arr:
            i += 1
            if i < __nth:
                result += token + __old
            elif __nth <= i < len(arr):
                result += token + __new
            else:
                result += token
        return stringButBetter(result)


def println(to_print):
    print((datetime.now()).strftime("[%H:%M:%S] ") + str(to_print))

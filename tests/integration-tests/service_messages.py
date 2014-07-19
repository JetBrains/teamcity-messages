class ServiceMessage:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __ge__(self, other):
        """
        :type self: service_message
        :type other: service_message
        :rtype: bool
        """
        if self.name != other.name:
            return False

        for p in other.params:
            if p in self.params:
                v1 = self.params[p]
                v2 = other.params[p]
                if not (v2 in v1):
                    return False
            else:
                return False
        return True

    def __str__(self):
        str = "[" + self.name
        for k, v in self.params.iteritems():
            str = str + ' ' + k + "='" + v + "'"
        str = str + "]"
        return str

    def __repr__(self):
        return self.__str__()


def parseServiceMessages(text):
    """
    Parses service messages from the given build log.
    :type text: str
    :rtype: list
    """
    messages = list()
    for line in text.splitlines():
        r = line.strip()
        if r.startswith("##teamcity[") and r.endswith("]"):
            m = _parseSM(r)
            messages.append(m)
    return messages


def _parseSM(str):
    """
    Parses one service message.
    :type str: str
    :rtype: service_message
    """
    b1 = str.index('[')
    b2 = str.rindex(']', b1)
    inner = str[b1 + 1:b2].strip()
    space1 = inner.find(' ')
    namelen = space1 if space1 >= 0 else inner.__len__()
    name = inner[0:namelen]
    params = dict()
    beg = namelen + 1
    while beg < inner.__len__():
        if inner[beg] == '_':
            beg = beg + 1
            continue
        eq = inner.find('=', beg)
        if eq == -1: break
        q1 = inner.find("'", eq)
        if q1 == -1: break
        q2 = inner.find("'", q1 + 1)
        while (q2 > 0 and inner[q2 - 1] == '|'): q2 = inner.find("'", q2 + 1)
        if q2 == -1: break
        param_name = inner[beg:eq].strip()
        param_value = inner[q1 + 1:q2]
        params[param_name] = param_value
        beg = q2 + 1
    return ServiceMessage(name, params)






import sys

from common import to_unicode, get_output_encoding


class ServiceMessage:
    def __init__(self, name, params):
        """
        :type name: string
        :type params: dict[string, string]
        """
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
                if to_unicode(v1) != to_unicode(v2):
                    return False
            else:
                return False
        return True

    def as_unicode(self):
        buf = "[" + self.name
        for k, v in self.params.items():
            buf += ' ' + k + "='" + v + "'"
        buf += "]"
        return to_unicode(buf)

    def __str__(self):
        return self.as_unicode().encode(get_output_encoding())

    def __unicode__(self):
        return self.as_unicode()


def parse_service_messages(text):
    """
    Parses service messages from the given build log.
    :type text: str
    :rtype: list[ServiceMessage]
    """
    messages = list()
    for line in text.splitlines():
        r = line.strip()
        index = r.find("##teamcity[")
        if index != -1:
            m = _parse_one_service_message(r[index:])
            messages.append(m)
    return messages


def service_messages_to_string(messages):
    """
    :type messages: list[ServiceMessage]
    """
    return u" ".join([x.as_unicode() for x in messages])


def _parse_one_service_message(s):
    """
    Parses one service message.
    :type s: str
    :rtype: service_message
    """
    b1 = s.index('[')
    b2 = s.rindex(']', b1)
    inner = s[b1 + 1:b2].strip()
    space1 = inner.find(' ')
    if space1 >= 0:
        name_len = space1
    else:
        name_len = inner.__len__()
    name = inner[0:name_len]
    params = dict()
    beg = name_len + 1
    while beg < inner.__len__():
        if inner[beg] == '_':
            beg += 1
            continue

        eq = inner.find('=', beg)
        if eq == -1:
            break

        q1 = inner.find("'", eq)
        if q1 == -1:
            break

        q2 = inner.find("'", q1 + 1)
        while q2 > 0 and inner[q2 - 1] == '|':
            q2 = inner.find("'", q2 + 1)
        if q2 == -1:
            break

        param_name = inner[beg:eq].strip()
        param_value = inner[q1 + 1:q2]
        params[param_name] = param_value
        beg = q2 + 1
    return ServiceMessage(name, params)


def has_service_messages(messages_string):
    messages = parse_service_messages(messages_string)
    return len(messages) > 0


def match(messages, message):
    """
    :type messages: list[ServiceMessage]
    :type message: ServiceMessage
    """
    candidates = [x for x in messages if x >= message]
    if len(candidates) == 0:
        raise AssertionError("No messages match " + message.as_unicode() + " across " + service_messages_to_string(messages))
    if len(candidates) > 1:
        raise AssertionError("More than one message match " + message.as_unicode() + " across " + service_messages_to_string(messages) +
                             ": " + service_messages_to_string(candidates))
    return candidates[0]


def assert_service_messages(actual_messages_string, expected_messages, actual_messages_predicate=lambda x: True):
    """
    :type expected_messages: list[ServiceMessage]
    """
    expected_messages = [x for x in expected_messages if x is not None]
    actual_messages = [x for x in parse_service_messages(actual_messages_string) if actual_messages_predicate(x)]

    try:
        if len(actual_messages) != len(expected_messages):
            raise AssertionError("Expected %d service messages, but got %d" % (len(expected_messages), len(actual_messages)))
        for index, (actual, expected) in enumerate(zip(actual_messages, expected_messages)):
            message = u"Expected\n" + expected.as_unicode() + u", but got\n" + actual.as_unicode() + u"\n at index " + str(index)
            assert actual >= expected, message
    except AssertionError:
        print("Actual:\n" + service_messages_to_string(actual_messages) + "\n")
        print("Expected:\n" + service_messages_to_string(expected_messages) + "\n")

        raise sys.exc_info()[1]

    return actual_messages

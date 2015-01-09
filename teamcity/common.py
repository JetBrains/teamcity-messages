# coding=utf-8

_max_reported_output_size = 1 * 1024 * 1024
_reported_output_chunk_size = 50000


def limit_output(data):
    return data[:_max_reported_output_size]


def split_output(data):
    while len(data) > 0:
        if len(data) <= _reported_output_chunk_size:
            yield data
            data = ''
        else:
            yield data[:_reported_output_chunk_size]
            data = data[_reported_output_chunk_size:]

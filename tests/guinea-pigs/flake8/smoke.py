import sys

def test_chunks():
    big = "x" * (2 * 1024 * 1024)
    sys.stdout.write(big)
    sys.stderr.write(big)


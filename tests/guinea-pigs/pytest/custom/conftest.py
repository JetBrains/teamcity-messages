import pytest

def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile.from_parent(parent, fspath=path)


class YamlFile(pytest.File):
    def collect(self):
        f = self.fspath.open()
        for line in f.readlines():
            yield YamlItem.from_parent(self, name=line.strip(), spec="xxx")
        f.close()

class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec

    def runtest(self):
        pass

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class RouteGenerator:
    def __init__(self, spec):
        self.spec = spec
        self.allowed_methods = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']

    def view(self, pathname: str):
        ...


class PythonFunction:
    def __init__(self, name: str, parameters: [str], returns: [str]=["None"], docstrings=None):
        self.name = name
        self.parameters = parameters
        self.returns = returns
        self.docstrings = docstrings

    def __str__(self):
        definition = f"def {self.name}({', '.join([x for x in self.parameters])}):"
        lines = [definition]
        if self.docstrings is not None:
            lines.append(f'\t"""\n{self.docstrings}\n\t"""')
        for value in self.returns:
            lines.append(f"\treturn {value}")

        return "\n".join(lines)


class PythonClass:
    def __init__(self, name, **kwargs):
        self.methods = []
        self.fields = []
        self.docstring = kwargs['docstring'] if 'docstring' in kwargs.keys() else None
        self.parent = kwargs['parent'] if "parent" in kwargs.keys() else None
        self.name = name

    def add_field(self, name: str, default=None):
        self.fields.append(f"{name}={default}" if default is not None else name)

    def add_method(self, name, parameters, *args):
        self.methods.append(PythonFunction(name, ["self"] + parameters, *args))

    def __str__(self):
        definition = f"class {self.name}"
        if self.parent is not None:
            definition += f"({self.parent})"
        definition += ":"
        lines = [definition]
        for method in self.methods:
            lines.extend(['\t' + x for x in str(method).splitlines()])

        return "\n".join(lines)


class DjangoRouteGenerator(RouteGenerator):
    @classmethod
    def path_to_path_id(cls, pathname):
        return pathname.replace("/", "_")

    def paths(self):
        ...

    def view(self, pathname: str):
        path_object = self.spec.at(['paths', pathname])
        methods = [x for x in path_object.keys() if x.upper() in self.allowed_methods]
        path_id = self.path_to_path_id(pathname)

        cls = PythonClass(path_id, parent="View")
        path_params = []
        if 'parameters' in path_object.keys():
            for i in range(len(self.spec.at(['paths', pathname, 'parameters']))):
                param = self.spec.at(['paths', pathname, 'parameters', i])
                if param['in'] == 'path':
                    path_params.append(param['name'])

        for method in methods:
            response = self.spec.at(['paths', pathname, method])
            return_values = [x for x in self.spec.at(['paths', pathname, method, "responses"]).keys()]
            docstrings = "\n\n".join([x for x in [
                (self.spec.at(['paths', pathname, method, 'summary']) if ('summary' in response.keys()) else ""),
                (self.spec.at(['paths', pathname, method, 'description']) if ('description' in response.keys()) else "")
            ] if x != ""])

            cls.add_method(method, ["request"] + path_params, return_values, docstrings)

        return cls

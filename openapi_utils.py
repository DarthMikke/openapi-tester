from openapi_core import OpenAPISpec


allowed_methods = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']


class Spec(OpenAPISpec):
    def __init__(self, accessor, *args, **kwargs):
        super().__init__(accessor, *args, **kwargs)

    def at(self, path: str or list):
        with self.accessor.open(path) as value:
            to_return = value
        return to_return

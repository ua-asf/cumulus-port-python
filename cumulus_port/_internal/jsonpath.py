import jsonpath_ng
import jsonpath_ng.ext


def get(data: dict, path: str) -> list:
    expr = jsonpath_ng.ext.parse(path)
    return [match.value for match in expr.find(data)]

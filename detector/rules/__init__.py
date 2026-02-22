import pkgutil
import importlib
import inspect

from detector.rules.baserule import BaseRule

RULE_CLASSES = {}

package_name = __name__

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name == "baserule":
        continue

    module = importlib.import_module(f"{package_name}.{module_name}")

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseRule) and obj is not BaseRule:
            RULE_CLASSES[obj.name] = obj

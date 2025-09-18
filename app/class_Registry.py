

class Registry(type):
    """
    Stores instances of classes.

    Usage:
        class MyClass(metaclass=Registry):
            def __init__(self, title):
                self.title = title

            MyClass(title='Yahoo')
            MyClass(title='Cloudfalre')

            for i in MyClass._instances:
                print(i.title)
    """
    _instances = []

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        cls._instances.append(instance)
        return instance
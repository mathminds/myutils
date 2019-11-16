from hashlib import sha256

from luigi import LocalTarget
from luigi.task import flatten

class Requirement:
    def __init__(self, task_class, **params):
        self.task_class = task_class
        self.params = params

    def __get__(self, task, cls):
        if task is None:
            return self

        return task.clone(
            self.task_class,
            **self.params)


class Requires:
    """Composition to replace :meth:`luigi.task.Task.requires`

    Example::

        class MyTask(Task):
            # Replace task.requires()
            requires = Requires()
            other = Requirement(OtherTask)

            def run(self):
                # Convenient access here...
                with self.other.output().open('r') as f:
                    ...

        # >>> MyTask().requires()
        {'other': OtherTask()}    """

    def __get__(self, task, cls):
        if task is None:
            return self

        # Bind self/task in a closure
        return lambda : self(task)

    def __call__(self, task):
        """Returns the requirements of a task

        Assumes the task class has :class:`.Requirement` descriptors, which
        can clone the appropriate dependences from the task instance.

        :returns: requirements compatible with `task.requires()`
        :rtype: dict
        """
        return {k: getattr(task, k) for k in dir(task.__class__) if isinstance(getattr(task.__class__, k), Requirement)}


class TargetOutput:
    def __init__(self, file_pattern='{task.__class__.__name__}', ext='.txt', target_class=LocalTarget, **target_kwargs):
        self.file_pattern = file_pattern
        self.target_class = target_class
        self.ext = ext
        self.target_kwargs = target_kwargs

    def __get__(self, task, cls):
        if task is None:
            return self
        return lambda: self(task)

    def __call__(self, task):
        filename = self.file_pattern.format(task=task) + self.ext
        return self.target_class(filename, **self.target_kwargs)


def get_salted_version(task):
    """Create a salted id/version for this task and lineage
    :returns: a unique, deterministic hexdigest for this task
    :rtype: str
    """

    msg = ""

    # Salt with lineage
    for req in flatten(task.requires()):
        # Note that order is important and impacts the hash - if task
        # requirements are a dict, then consider doing this is sorted order
        msg += get_salted_version(req)

    # Uniquely specify this task
    msg += ','.join([

            # Basic capture of input type
            task.__class__.__name__,

            # Change __version__ at class level when everything needs rerunning!
            task.__version__,

        ] + [
            # Depending on strictness - skipping params is acceptable if
            # output already is partitioned by their params; including every
            # param may make hash *too* sensitive
            '{}={}'.format(param_name, repr(task.param_kwargs[param_name]))
            for param_name, param in sorted(task.get_params())
            if param.significant
        ]
    )
    return sha256(msg.encode()).hexdigest()

class SaltedOutput(TargetOutput):
    def __init__(self, file_pattern='{task.__class__.__name__}-{salt}', ext='.txt', target_class=LocalTarget,
                 **target_kwargs):
        super().__init__(file_pattern, ext, target_class, **target_kwargs)

    def __get__(self, task, cls):
        filename = self.file_pattern.format(task=task, salt = get_salted_version(task)[:8]) + self.ext
        return self.target_class(filename, **self.target_kwargs)

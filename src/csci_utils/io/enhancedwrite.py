from contextlib import contextmanager
from atomicwrites import atomic_write as _backend_writer, AtomicWriter
from os import path


class EnhancedAtomicWriter(AtomicWriter):
    def get_fileobject(self, suffix="", dir=None, **kwargs):
        return super().get_fileobject(suffix, dir, **kwargs)


@contextmanager
def atomic_write(file, mode="w", as_file=True, **kwargs):

    # if file already exists through an exception
    if path.isfile(file):
        raise FileExistsError("File provided already exists! {}".format(file))

    _, filename = path.split(file)
    _, ext = path.splitext(filename)
    with _backend_writer(
        file, writer_cls=EnhancedAtomicWriter, mode=mode, suffix=ext, **kwargs
    ) as f:
        if as_file:
            yield f
        else:
            yield f.name

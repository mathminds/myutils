from luigi.local_target import LocalTarget, atomic_file
from contextlib import contextmanager
import random
from pathlib import Path


class suffix_preserving_atomic_file(atomic_file):
    def generate_tmp_path(self, path):
        if path == None:
            path = self.path

        suffix = "".join(Path(path).suffixes)
        return path + '-luigi-tmp-%09d' % random.randrange(0, 1e10) + suffix

        #
        # file_name, file_extension = '.'.join(path.split('.')[:-1]), '.'.join(path.split('/')[-1].split('.')[2:])
        # return file_name + '-luigi-tmp-%09d' % random.randrange(0, 1e10) + '.'+file_extension



class BaseAtomicProviderLocalTarget(LocalTarget):
    # Allow some composability of atomic handling
    atomic_provider = atomic_file

    def open(self, mode='r'):
        # leverage super() as well as modifying any code in LocalTarget
        # to use self.atomic_provider rather than atomic_file

        rwmode = mode.replace('b', '').replace('t', '')
        if rwmode == 'w':
            self.makedirs()
            return self.format.pipe_writer(self.atomic_provider(self.path))

        return super().open(mode = mode)

    @contextmanager
    def temporary_path(self):
        # NB: unclear why LocalTarget doesn't use atomic_file in its implementation
        self.makedirs()
        with self.atomic_provider(self.path) as af:
            yield af.tmp_path


class SuffixPreservingLocalTarget(BaseAtomicProviderLocalTarget):
    atomic_provider = suffix_preserving_atomic_file



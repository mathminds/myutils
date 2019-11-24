from contextlib import contextmanager
from luigi.local_target import LocalTarget, atomic_file
import os


class suffix_preserving_atomic_file(atomic_file):
    def generate_tmp_path(self, path):
        parent_dir, filename = os.path.split(path)
        filename, ext = os.path.splitext(filename)
        filename_no_suffix = os.path.join(parent_dir, filename)
        tmp_path = super().generate_tmp_path(filename_no_suffix)
        return tmp_path + ext


class BaseAtomicProviderLocalTarget(LocalTarget):
    # Allow some composability of atomic handling
    atomic_provider = atomic_file

    def open(self, mode="r"):
        rwmode = mode.replace("b", "").replace("t", "")
        if rwmode == "w":
            self.makedirs()
            return self.format.pipe_writer(self.atomic_provider(self.path))
        else:
            return super().open(mode)

    @contextmanager
    def temporary_path(self):
        # NB: unclear why LocalTarget doesn't use atomic_file in its implementation
        self.makedirs()
        with self.atomic_provider(self.path) as af:
            yield af.tmp_path


class SuffixPreservingLocalTarget(BaseAtomicProviderLocalTarget):
    atomic_provider = suffix_preserving_atomic_file

import os
# import boto3
from luigi import ExternalTask, Parameter, Task
from luigi.contrib.s3 import S3Target
from luigi.format import Nop
from csci_utils.luigi.target import SuffixPreservingLocalTarget
from luigi.contrib.opener import OpenerTarget


class SavedContent(ExternalTask):
    # params
    ROOT = Parameter()
    FILENAME=Parameter()
    TYPE = Parameter()

    def output(self):
        filepath = os.path.join(self.ROOT, self.TYPE, self.FILENAME)
        return OpenerTarget(filepath, format=Nop) # OpenerTarget automatically figures out the correct target from filepath


class CopyContent(Task):
    # Params
    TYPE = Parameter()
    FILENAME=Parameter()

    def requires(self): # Requires input file to exist
        return SavedContent(ROOT = self.ROOT, TYPE = self.TYPE, FILENAME = self.FILENAME)

    def output(self):  # Set output path using correct target
        filepath = os.path.join(self.DEST, self.TYPE, self.FILENAME)
        return self.OutputTarget(filepath, format = Nop)

    def run(self): # Copy file
        with self.output().open('w') as output_file:
            with self.input().open() as in_file:
                output_file.write(in_file.read())


class DownloadContent(CopyContent):
    # Download from s3 to local
    ROOT = Parameter('s3://mathuser0/pset_4') # Set input to s3 path
    DEST = Parameter(os.path.abspath('data')) # Set output to local path
    OutputTarget = Parameter(SuffixPreservingLocalTarget) # Set output target class to suffix preserving local target


class UploadContent(CopyContent):
    # Upload to s3 from local
    ROOT = Parameter(os.path.abspath('data')) # Set input to local path
    DEST = Parameter('s3://mathuser0/pset_4') # Set output to s3 path
    OutputTarget = Parameter(S3Target) # Set output target class


# Image Classes
class DownloadImage(DownloadContent):
    TYPE = Parameter('images') # Set data type


class UploadImage(UploadContent):
    TYPE = Parameter('images') # Set data type


# Model Classes
class DownloadModel(DownloadContent):
    TYPE = Parameter('saved_models') # Set data type


class UploadModel(UploadContent):
    TYPE = Parameter('saved_models') # Set data type

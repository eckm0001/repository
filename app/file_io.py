""" file_io.py
"""
#from ast import Dict
from contextlib import contextmanager
from pathlib import Path
import logging
import csv
import yaml

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class FileManager:
    """ FileManager class for managing files and directories.
    """
    def __init__(self):
        #self.config_file = config , config_file
        self.basedir = Path('app/data/')
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def custom_read(self, filename):
        """ custom_read
        """
        f = open(filename, "r", encoding='utf-8')
        try:
            yield f
        finally:
            f.close()

    @contextmanager
    def custom_write(self, filename):
        """ custom_write
        """
        f = open(filename, "w", encoding='utf-8')
        try:
            yield f
        finally:
            f.close()

    def read_file(self, filename):
        """ read_file
        """
        try:
            #print(self.basedir)
            with self.custom_read(filename) as file:
                content = file.read()
            self.logger.info('Read file: %s', filename)
            return content
        except FileNotFoundError:
            self.logger.error('File not found: %s', filename)
        except Exception as e:
            self.logger.error('Error reading file: %s %s', filename, e)

    def delete_file(self, filename):
        """
        Delete a file from the input directory.

        Args:
            filename (str): The name of the file to be deleted.

        Returns:
            bool: True if the file was successfully deleted, False otherwise.
        """
        try:
            file_path = filename
            if file_path.exists():
                file_path.unlink()
                self.logger.info('Deleted file: %s', file_path)
                return True
            else:
                self.logger.warning('File not found: %s', file_path)
                return False
        except Exception as e:
            self.logger.error('Error deleting file: %s %s', file_path, e)
            return False

    def read_yaml(self, filename):
        """ read_yaml
        """
        try:
            #print(self.basedir)
            with self.custom_read(filename) as file:
                content = yaml.safe_load(file)
            self.logger.info('Read file: %s', filename)
            return content
        except FileNotFoundError:
            self.logger.error('File not found: %s', filename)
        except Exception as e:
            self.logger.error('Error reading file: %s %s', filename, e)

    def read_csv(self, file_path) -> list | None:
        """
        Read a CSV file and return its contents as a list of dictionaries.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row in the CSV file.
        """
        try:
            with self.custom_read(file_path) as file:
                reader = csv.DictReader(file)
                data = list(reader)
            self.logger.info('Read CSV file: %s', file_path)
            return data
        except FileNotFoundError:
            self.logger.error('File not found: %s', file_path)
        except Exception as e:
            self.logger.error('Error reading CSV file: %s %s', file_path, e)

    def write_file(self, filename, content):
        """ write_file
        """
        try:
            with self.custom_write(filename) as file:
                file.write(content)
            self.logger.info('Wrote file: %s', filename)
        except Exception as e:
            self.logger.error('Error writing file: %s %s', filename, e)

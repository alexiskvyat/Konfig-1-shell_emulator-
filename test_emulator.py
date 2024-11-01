
import unittest
import os
import tempfile
import zipfile
from main import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary zip file to act as the virtual file system
        self.test_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        
        with zipfile.ZipFile(self.test_zip.name, 'w') as zip_file:
            # Create directories and files in the zip file
            zip_file.writestr("test/test1.txt", "This is test file 1.")
            zip_file.writestr("test/test2.txt", "This is test file 2.")
            zip_file.writestr("test/test_subdir/", "")

        self.log_file = tempfile.NamedTemporaryFile(delete=False, suffix=".log")
        
        # Initialize the ShellEmulator with the test zip file and log file paths
        self.emulator = ShellEmulator(user_name="test_user", vfs_path=self.test_zip.name, log_path=self.log_file.name)
    
    def tearDown(self):
        # Remove the temporary files
        os.remove(self.test_zip.name)
        os.remove(self.log_file.name)

    def test_ls_root_directory(self):
        # Test listing contents in the root directory
        self.emulator.current_dir = self.emulator.root_dir
        output = self.emulator.list_directory()
        self.assertIn("test", output)

    def test_cd_into_directory(self):
        # Test changing directory to "test"
        self.emulator.current_dir = self.emulator.root_dir
        self.emulator.change_directory("cd test")
        self.assertTrue(self.emulator.current_dir.endswith("test"))

    def test_cd_non_existing_directory(self):
        # Test changing to a non-existent directory
        initial_dir = self.emulator.current_dir
        self.emulator.change_directory("cd non_existing_dir")
        self.assertEqual(self.emulator.current_dir, initial_dir)

    def test_mkdir(self):
        # Test creating a new directory
        self.emulator.current_dir = self.emulator.root_dir
        self.emulator.make_directory("mkdir new_dir")
        output = self.emulator.list_directory()
        self.assertIn("new_dir", output)

    def test_show_file_content_existing_file(self):
        # Test displaying contents of an existing file
        self.emulator.current_dir = os.path.join(self.emulator.root_dir, "test")
        content = self.emulator.show_file_content("cat test1.txt")
        self.assertEqual(content.strip(), "This is test file 1.")

    def test_show_file_content_non_existing_file(self):
        # Test displaying contents of a non-existing file
        self.emulator.current_dir = os.path.join(self.emulator.root_dir, "test")
        content = self.emulator.show_file_content("cat non_existing.txt")
        self.assertEqual(content, "No such file: non_existing.txt")

    def test_uptime(self):
        # Test the uptime functionality
        uptime_output = self.emulator.show_uptime()
        self.assertTrue(isinstance(uptime_output, float) and uptime_output >= 0)

if __name__ == '__main__':
    unittest.main()

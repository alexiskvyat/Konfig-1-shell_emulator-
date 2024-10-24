import os
import sys
import zipfile
import json
import time
import argparse
from pathlib import Path
import unittest


class ShellEmulator:
    def __init__(self, user_name, vfs_path, log_path, script_path=None):
        self.user_name = user_name
        self.log_path = log_path
        self.script_path = script_path
        self.current_dir = '/'
        self.start_time = time.time()
        self.load_vfs(vfs_path)
        self.log_file = open(self.log_path, 'w')

    def load_vfs(self, vfs_path):
        """Load the virtual file system from the zip file."""
        with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
            zip_ref.extractall('/tmp/vfs')
        self.root_dir = '/tmp/vfs'
        self.current_dir = self.root_dir

    def log_action(self, command):
        """Log the user's actions to the JSON log file."""
        log_entry = {
            'user': self.user_name,
            'command': command,
            'timestamp': time.time()
        }
        json.dump(log_entry, self.log_file)
        self.log_file.write('\n')

    def run(self):
        """Run the shell, handling commands."""
        if self.script_path:
            self.execute_script(self.script_path)

        while True:
            command = input(f'{self.user_name}@emulator:{self.current_dir}$ ').strip()
            self.log_action(command)

            if command == 'exit':
                break
            elif command.startswith('cd'):
                self.change_directory(command)
            elif command == 'ls':
                self.list_directory()
            elif command == 'uptime':
                self.show_uptime()
            elif command.startswith('mkdir'):
                self.make_directory(command)
            elif command.startswith('cat'):
                self.show_file_content(command)
            else:
                print(f"Command not found: {command}")

    def execute_script(self, script_path):
        """Execute commands from a script file."""
        with open(script_path, 'r') as f:
            for line in f:
                command = line.strip()
                print(f"Executing: {command}")
                self.log_action(command)
                if command.startswith('cd'):
                    self.change_directory(command)
                elif command == 'ls':
                    self.list_directory()
                elif command == 'uptime':
                    self.show_uptime()
                elif command.startswith('mkdir'):
                    self.make_directory(command)
                elif command.startswith('cat'):
                    self.show_file_content(command)

    def change_directory(self, command):
        """Change the current directory."""
        try:
            target_dir = command.split()[1]
            new_dir = os.path.join(self.current_dir, target_dir)
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                self.current_dir = new_dir
            else:
                print(f"No such directory: {target_dir}")
        except IndexError:
            print("Usage: cd <directory>")

    def list_directory(self):
        """List the contents of the current directory."""
        try:
            files = os.listdir(self.current_dir)
            for file in files:
                print(file)
        except FileNotFoundError:
            print("Directory not found.")

    def show_file_content(self, command):
        """Display the content of a file."""
        try:
            file_name = command.split()[1]
            file_path = os.path.join(self.current_dir, file_name)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    print(file.read())
            else:
                print(f"No such file: {file_name}")
        except IndexError:
            print("Usage: cat <file_name>")

    def show_uptime(self):
        """Show how long the emulator has been running."""
        uptime = time.time() - self.start_time
        print(f"Uptime: {uptime:.2f} seconds")

    def make_directory(self, command):
        """Create a new directory."""
        try:
            dir_name = command.split()[1]
            new_dir = os.path.join(self.current_dir, dir_name)
            os.mkdir(new_dir)
            print(f"Directory created: {dir_name}")
        except IndexError:
            print("Usage: mkdir <directory_name>")
        except FileExistsError:
            print(f"Directory already exists: {dir_name}")


# Тесты для ShellEmulator
class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator(user_name="test", vfs_path="test_vfs.zip", log_path="test_log.json", script_path=None)
        os.mkdir('/tmp/vfs')
        os.mkdir('/tmp/vfs/empty_dir')
        os.mkdir('/tmp/vfs/non_empty_dir')
        with open('/tmp/vfs/non_empty_dir/file1.txt', 'w') as f:
            f.write("This is a test file")

    def tearDown(self):
        """Удаление временных файлов и директорий после каждого теста"""
        if os.path.exists('/tmp/vfs'):
            for root, dirs, files in os.walk('/tmp/vfs', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def test_ls_empty_dir(self):
        """Тест для команды ls в пустой директории"""
        self.emulator.current_dir = "/tmp/vfs/empty_dir"
        self.assertEqual(self.emulator.list_directory(), [])

    def test_ls_non_empty_dir(self):
        """Тест для команды ls в директории с файлами"""
        self.emulator.current_dir = "/tmp/vfs/non_empty_dir"
        self.assertIn('file1.txt', self.emulator.list_directory())

    def test_cat_file(self):
        """Тест для команды cat для существующего файла"""
        self.emulator.current_dir = "/tmp/vfs/non_empty_dir"
        file_content = self.emulator.show_file_content("cat file1.txt")
        self.assertIn("This is a test file", file_content)

    def test_cat_non_existing_file(self):
        """Тест для команды cat для несуществующего файла"""
        self.emulator.current_dir = "/tmp/vfs/non_empty_dir"
        file_content = self.emulator.show_file_content("cat non_existing_file.txt")
        self.assertIsNone(file_content)


# Основная функция для запуска эмулятора
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Запуск тестов
        unittest.main(argv=sys.argv[:1])
    else:
        # Запуск эмулятора
        parser = argparse.ArgumentParser(description="Shell Emulator")
        parser.add_argument('--user', required=True, help='User name for the prompt')
        parser.add_argument('--vfs', required=True, help='Path to the zip archive of the virtual file system')
        parser.add_argument('--log', required=True, help='Path to the log file')
        parser.add_argument('--script', help='Path to the startup script')

        args = parser.parse_args()

        emulator = ShellEmulator(user_name=args.user, vfs_path=args.vfs, log_path=args.log, script_path=args.script)
        emulator.run()

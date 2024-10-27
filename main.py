import os
import zipfile
import time
import argparse
from datetime import datetime

class ShellEmulator:
    def __init__(self, user_name, vfs_path, log_path, script_path=None):
        self.user_name = user_name
        self.log_path = log_path
        self.script_path = script_path
        self.current_dir = '/'
        self.start_time = time.time()
        self.load_vfs(vfs_path)
        self.setup_log_file()

    def load_vfs(self, vfs_path):
        """Load the virtual file system from the zip file."""
        with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
            zip_ref.extractall('/tmp/vfs')
        self.root_dir = '/tmp/vfs'
        self.current_dir = self.root_dir

    def setup_log_file(self):
        """Set up the log file with headers for the table."""
        with open(self.log_path, 'w') as log_file:
            log_file.write("User Name,Command,Time\n")

    def log_action(self, command):
        """Log the user's actions to the log file in a table format."""
        log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{self.user_name},{command},{log_time}\n"
        with open(self.log_path, 'a') as log_file:
            log_file.write(log_entry)

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

            if target_dir == '..':
                if self.current_dir != self.root_dir:
                    self.current_dir = os.path.dirname(self.current_dir)
                else:
                    print("You are already in the root directory.")
            else:
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
            current_dir_name = os.path.basename(self.current_dir)  # Получаем имя текущей директории
            files = os.listdir(self.current_dir)
            # Исключаем файлы и папки, совпадающие по имени с текущей директорией
            filtered_files = [f for f in files if f != current_dir_name]
            for file in filtered_files:
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

# Основная функция для запуска эмулятора
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--user', required=True, help='User name for the prompt')
    parser.add_argument('--vfs', required=True, help='Path to the zip archive of the virtual file system')
    parser.add_argument('--log', required=True, help='Path to the log file')
    parser.add_argument('--script', help='Path to the startup script')

    args = parser.parse_args()

    emulator = ShellEmulator(user_name=args.user, vfs_path=args.vfs, log_path=args.log, script_path=args.script)
    emulator.run()

import os
import sys
import shutil
import time
import datetime


class Logger:
    def __init__(self):
        fp = open("update.txt", 'w')
        cur_date = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        fp.write(f"update time: {cur_date} \n\n")
        self.fp = fp
        self.indent_count = 0
    
    def indent(self):
        self.indent_count += 1
    
    def dedent(self):
        if self.indent_count == 0:
            raise Exception("indent is needed befor dedent")
        self.indent_count -= 1

    def write(self, msg):
        msg = "    "*self.indent_count + msg
        print(msg)
        self.fp.write(f"{msg} \n")

    def close(self):
        self.fp.close()


logger = None


def copy_file_if_newer(src, dest):
    if not os.path.exists(src):
        raise Exception("%s not exist" % src)
    if not os.path.exists(dest) or \
       os.stat(src).st_mtime > os.stat(dest).st_mtime:
        shutil.copy(src, dest)
        logger.write("%s update." % dest)
        return
    logger.write("%s reused." % dest)


def copy_file(src, dest):
    if os.path.exists(dest):
        shutil.copy(src, dest)
        logger.write(f"update {dest}")
    else:
        shutil.copy(src, dest)
        logger.write(f"add {dest}")


def _update_files(source_dir, dest_dir):
    for item in os.listdir(source_dir):
        src = os.path.join(source_dir, item)
        dest = os.path.join(dest_dir, item)
        copy_file(src, dest)


def _update_packages(source_dir):
    for item in os.listdir(source_dir):
        _update_package(source_dir, item)


def _update_package(source_dir, file_name):
    source = os.path.join(source_dir, file_name)
    dest = os.path.join(sys.prefix, "packages", file_name)
    logger.write(f"Update package {file_name}:")
    logger.indent()
    if os.path.isfile(source):
        _remove_package_file(file_name)
        logger.write(f"Update package {file_name}")
        shutil.copy(source, dest)
    else:
        _remove_package_dir(file_name)
        logger.write(f"Update package {file_name}")
        shutil.copytree(source, dest)
    logger.dedent()


def _remove_package_file(file_name):
    dest_dir = os.path.join(sys.prefix, "packages")
    dest = os.path.join(dest_dir, file_name)
    if os.path.exists(dest):
        logger.write(f"remove old package {dest}")
        if os.path.isfile(dest):
            os.remove(dest)
        else:
            shutil.rmtree(dest)
    name, ext = os.path.splitext(file_name)
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest) and os.path.isdir(dest):
        logger.write(f"remove old package {dest}")
        shutil.rmtree(dest)
    for ext in (".zip", ".pyc", ".py", ".pyo"):
        dest = os.path.join(dest_dir, name+ext)
        if os.path.exists(dest) and os.path.isfile(dest):
            logger.write(f"remove old package {dest}")
            os.remove(dest)


def _remove_package_dir(file_name):
    dest_dir = os.path.join(sys.prefix, "packages")
    dest = os.path.join(dest_dir, file_name)
    if os.path.exists(dest):
        logger.write(f"remove old package {dest}")
        if os.path.isfile(dest):
            os.remove(dest)
        else:
            shutil.rmtree(dest)
    for ext in (".zip", ".pyc", ".py", ".pyo"):
        dest = os.path.join(dest_dir, file_name+ext)
        if os.path.exists(dest) and os.path.isfile(dest):
            logger.write(f"remove old package {dest}")
            os.remove(dest)


def update():
    global logger
    logger = Logger()

    folder = os.path.join(sys.prefix, "update")
    if not os.path.exists(folder):
        logger.write(f"update folder '{folder}' not exist")
        return

    source_dir = os.path.join(folder, "DLLs")
    dest_dir = os.path.join(sys.prefix, "DLLs")
    if os.path.exists(source_dir):
        logger.write(">>Updating DLLs:\n")
        logger.indent()
        _update_files(source_dir, dest_dir)
        logger.dedent()

    source_dir = os.path.join(folder, "extensions")
    dest_dir = os.path.join(sys.prefix, "extensions")
    if os.path.exists(source_dir):
        logger.write("\n>>Updating extension modules:\n")
        logger.indent()
        _update_files(source_dir, dest_dir)
        logger.dedent()

    source_dir = os.path.join(folder, "packages")
    if os.path.exists(source_dir):
        logger.write("\n>>Updating packages:\n")
        logger.indent()
        _update_packages(source_dir)
        logger.dedent()

    logger.close()

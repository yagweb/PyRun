import os
import sys
import shutil
import glob
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
        logger.write(f"update file {os.path.relpath(dest, sys.prefix)}")
    else:
        shutil.copy(src, dest)
        logger.write(f"add file {os.path.relpath(dest, sys.prefix)}")


def _update_item(source, dest):
    if os.path.isfile(source):
        if os.path.isdir(dest):
            logger.write(f"replace dir with file {os.path.relpath(dest, sys.prefix)}")
            shutil.rmtree(dest)
            shutil.copy(src, dest)
        else:
            copy_file(source, dest)
    else:
        if not os.path.exists(dest):
            logger.write(f"add dir {os.path.relpath(dest, sys.prefix)}")
            shutil.copytree(source, dest)
            return
        if os.path.isfile(dest):
            logger.write(f"replace file with dir {os.path.relpath(dest, sys.prefix)}")
            os.remove(dest)
            shutil.copytree(source, dest)
            return
        _update_dir(source, dest)


def _update_dir(source_dir, dest_dir):
    for item in os.listdir(source_dir):
        src = os.path.join(source_dir, item)
        dest = os.path.join(dest_dir, item)
        _update_item(src, dest)


def _update_packages(source_dir):
    for item in os.listdir(source_dir):
        _update_package(source_dir, item)


def _update_package(source_dir, file_name):
    source = os.path.join(source_dir, file_name)
    dest = os.path.join(sys.prefix, "packages", file_name)
    logger.write(f"Update package {os.path.relpath(file_name, sys.prefix)}:")
    logger.indent()
    if os.path.isfile(source):
        _remove_package_file(file_name)
        logger.write(f"Update package {os.path.relpath(file_name, sys.prefix)}")
        shutil.copy(source, dest)
    else:
        _remove_package_dir(file_name)
        logger.write(f"Update package {os.path.relpath(file_name, sys.prefix)}")
        shutil.copytree(source, dest)
    logger.dedent()


def _remove_package_file(file_name):
    dest_dir = os.path.join(sys.prefix, "packages")
    dest = os.path.join(dest_dir, file_name)
    if os.path.exists(dest):
        logger.write(f"remove old package {os.path.relpath(dest, sys.prefix)}")
        if os.path.isfile(dest):
            os.remove(dest)
        else:
            shutil.rmtree(dest)
    name, ext = os.path.splitext(file_name)
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest) and os.path.isdir(dest):
        logger.write(f"remove old package {os.path.relpath(dest, sys.prefix)}")
        shutil.rmtree(dest)
    for ext in (".zip", ".pyc", ".py", ".pyo"):
        dest = os.path.join(dest_dir, name+ext)
        if os.path.exists(dest) and os.path.isfile(dest):
            logger.write(f"remove old package {os.path.relpath(dest, sys.prefix)}")
            os.remove(dest)


def _remove_package_dir(file_name):
    dest_dir = os.path.join(sys.prefix, "packages")
    dest = os.path.join(dest_dir, file_name)
    if os.path.exists(dest):
        logger.write(f"remove old package {os.path.relpath(dest, sys.prefix)}")
        if os.path.isfile(dest):
            os.remove(dest)
        else:
            shutil.rmtree(dest)
    for ext in (".zip", ".pyc", ".py", ".pyo"):
        dest = os.path.join(dest_dir, file_name+ext)
        if os.path.exists(dest) and os.path.isfile(dest):
            logger.write(f"remove old package {os.path.relpath(dest, sys.prefix)}")
            os.remove(dest)


def delete_files(file):
    patterns = []
    with open(file, 'r') as fp:
        lines = fp.readlines()
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            path = os.path.join(sys.prefix, line)
            if not path.startswith(sys.prefix):
                raise Exception(f"line {line_no}, {line} invalid")
            patterns.append(path)

    for pattern in patterns:
        for abspath in glob.glob(pattern):
            relpath = os.path.relpath(abspath, sys.prefix)
            if os.path.isdir(abspath):
                logger.write(f"delete dir '{relpath}'")
                shutil.rmtree(abspath)
            else:
                logger.write(f"delete file '{relpath}'")
                os.remove(abspath)


def update():
    global logger
    logger = Logger()

    folder = os.path.join(sys.prefix, "update")
    if not os.path.exists(folder):
        logger.write(f"update folder '{folder}' not exist")
        return

    for name in os.listdir(folder):
        abspath = os.path.join(folder, name)
        destpath = os.path.join(sys.prefix, name)
        if name == "delete.txt":
            logger.write(">>Remove files:\n")
            logger.indent()
            delete_files(abspath)
            logger.dedent()
            logger.write("\n")
        elif name == "packages":
            logger.write("\n>>Updating packages:\n")
            logger.indent()
            _update_packages(abspath)
            logger.dedent()
        elif os.path.isdir(abspath):
            logger.write(f">>Updating {name}:\n")
            logger.indent()
            _update_item(abspath, destpath)
            logger.dedent()
        else:
            shutil.copyfile(abspath, destpath)
    logger.close()

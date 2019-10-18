import os
import sys
import shutil
import glob
import time
import datetime
import zipfile


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


def _get_update_folder():
    folder = os.path.join(sys.prefix, "update")
    files = glob.glob(os.path.join(sys.prefix, "update*.zip"))
    if len(files) == 0:
        return folder
    logger.write(f"find {len(files)} update zip file\n")
    file_name = None
    zip_file = None
    for current in files:
        temp_zip = zipfile.ZipFile(current, 'r')
        if not "update/" in temp_zip.namelist():
            logger.write(f"not a valid update zip {current}, skip")
            temp_zip.close()
            continue
        if file_name is None or \
                os.stat(current).st_mtime > os.stat(file_name).st_mtime:
            file_name = current
            zip_file = temp_zip
        else:
            temp_zip.close()
    if zip_file is None:
        logger.write(f"no valid update zip file")
        return folder
    logger.write(f"use the newest zip file {file_name}\n")
    if os.path.exists(folder):
        logger.write(f"remove the old update folder {folder}\n")
        shutil.rmtree(folder)
    zip_file = zipfile.ZipFile(file_name, 'r')
    zip_file.extractall(sys.prefix)
#    for name in zip_file.namelist():
#        if name.startswith("update/"):
#            # zipfile默认对于文件名编码只识别cp437和utf-8
#            name = name.encode('cp437').decode('GBK')
#            zip_file.extract(name, sys.prefix)
    zip_file.close()
    return folder


def update():
    global logger
    logger = Logger()

    folder = _get_update_folder()
    if not os.path.exists(folder):
        raise Exception(f"update folder '{folder}' not exist")

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

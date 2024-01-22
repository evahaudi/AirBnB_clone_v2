#!/usr/bin/python3
"""
do_pack(): Generates a .tgz archive from the
contents of the web_static folder
do_deploy(): Distributes an archive to a web server
deploy (): Creates and distributes an archive to a web server
"""

from fabric.operations import local, run, put
from datetime import datetime
import os
from fabric.api import env
import re


env.hosts = ["35.175.128.0", "100.25.4.246"]


def do_pack():
    """Function to compress files in an archive"""
    local("mkdir -p versions")
    filename = "versions/web_static_{}.tgz".format(datetime.strftime(
                                                   datetime.now(),
                                                   "%Y%m%d%H%M%S"))
    result = local("tar -cvzf {} web_static"
                   .format(filename))
    if result.failed:
        return None
    return filename


def do_deploy(archive_path, version):
    """Function to distribute an archive to a server"""
    if not os.path.exists(archive_path):
        return False

    # Upload the archive
    res = put(archive_path, "/tmp/{}.tgz".format(version))
    if res.failed:
        return False

    # Create necessary directories
    res = run("mkdir -p /data/web_static/releases/{}/".format(version))
    if res.failed:
        return False

    # Extract contents of the archive
    res = run("tar -xzf /tmp/{}.tgz -C /data/web_static/releases/{}/"
              .format(version, version))
    if res.failed:
        return False

    # Remove the archive
    res = run("rm /tmp/{}.tgz".format(version))
    if res.failed:
        return False

    # Move contents to correct location
    res = run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/"
              .format(version, version))
    if res.failed:
        return False

    # Remove redundant directory
    res = run("rm -rf /data/web_static/releases/{}/web_static"
              .format(version))
    if res.failed:
        return False

    # Create my_index.html
    res = run("echo 'Hello Holberton!' > /data/web_static/releases/{}/my_index.html"
              .format(version))
    if res.failed:
        return False

    # Ensure correct permissions
    res = run("chown -R ubuntu:ubuntu /data/web_static/releases/{}/"
              .format(version))
    res = run("chown -h ubuntu:ubuntu /data/web_static/current")

    print('New version deployed!')
    return True


def deploy():
    """Creates and distributes an archive to a web server"""
    filepath = do_pack()
    if filepath is None:
        return False

    # Extract version from the archive path
    rex = r'^versions/(\S+).tgz'
    match = re.search(rex, filepath)
    version = match.group(1)

    d = do_deploy(filepath, version)
    return d

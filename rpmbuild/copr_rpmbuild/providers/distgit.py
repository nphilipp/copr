import os
import re
import logging
from jinja2 import Environment, FileSystemLoader
from ..helpers import run_cmd

try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin


log = logging.getLogger("__main__")


class DistGitProvider(object):
    def __init__(self, source_json, workdir=None, confdirs=None):
        self.clone_url = source_json["clone_url"]
        self.branch = source_json["branch"]
        self.workdir = workdir
        self.confdirs = confdirs

    def run(self):
        repodir = os.path.join(self.workdir, "repo")
        result = self.clone(repodir)
        log.info(result)

        cfg = self.render_rpkg_template()
        log.info(cfg)

        config_path = os.path.join(self.workdir, "rpkg.conf")
        f = open(config_path, "w+")
        f.write(cfg)
        f.close()

        if self.branch:
            self.checkout(self.branch, repodir)

        module_name = self.module_name(self.clone_url)
        result = self.produce_srpm(config_path, module_name, repodir)
        log.info(result)

    def clone(self, repodir):
        cmd = ["git", "clone", self.clone_url, repodir]
        return run_cmd(cmd)

    def checkout(self, branch, repodir):
        cmd = ["git", "checkout", branch]
        return run_cmd(cmd, cwd=repodir)

    def render_rpkg_template(self):
        jinja_env = Environment(loader=FileSystemLoader(self.confdirs))
        template = jinja_env.get_template("rpkg.conf.j2")
        parse = urlparse(self.clone_url)
        distgit_domain = parse.netloc
        return template.render(distgit_domain=distgit_domain, scheme=parse.scheme)

    def module_name(self, url):
        parse = urlparse(url)
        return re.sub(".git$", "", re.sub("^/c?git/", "", parse.path))

    def produce_srpm(self, config, module_name, repodir):
        cmd = ["rpkg", "--config", config, "--module-name", module_name, "srpm"]
        return run_cmd(cmd, cwd=repodir)

    @property
    def srpm(self):
        repodir = os.path.join(self.workdir, "repo")
        dest_files = os.listdir(repodir)
        dest_srpms = filter(lambda f: f.endswith(".src.rpm"), dest_files)

        if len(dest_srpms) != 1:
            log.debug("tmp_dest: {}".format(repodir))
            log.debug("dest_files: {}".format(dest_files))
            log.debug("dest_srpms: {}".format(dest_srpms))
            raise RuntimeError("No srpm files were generated.")
        return os.path.join(repodir, dest_srpms[0])
packer {
  required_plugins {
    docker = {
      version = ">= 0.0.7"
      source  = "github.com/hashicorp/docker"
    }
  }
}


source "docker" "ubuntu" {
  image  = "python:3"
  commit = true
  changes = [
    "ENTRYPOINT [\"uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data\"]"
  ]
}

build {
  name = "uWSGI Tanzawa Server"
  sources = [
    "source.docker.ubuntu"
  ]
  provisioner "file" {
    sources = [
      "templates/uwsgi.ini",
      "templates/env",
    ]
    destination = "/tmp/"
  }
  provisioner "shell" {
    environment_vars = []
    scripts = [
      "setup/base_install.sh"
    ]
  }


}


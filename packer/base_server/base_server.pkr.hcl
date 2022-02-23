packer {
  required_plugins {
    docker = {
      version = ">= 0.0.7"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "ubuntu" {
  image  = "ubuntu:xenial"
  commit = true
}

build {
  name = "Base Tanzawa Server"
  sources = [
    "source.docker.ubuntu"
  ]
  provisioner "file" {
    source="setup/weekly_update.sh"
    destination= "/tmp/weekly_update.sh"
  }
  provisioner "shell" {
    environment_vars = []
    scripts = [
      "setup/base_install.sh"
    ]
  }


}

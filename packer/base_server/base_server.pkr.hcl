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

variable "server_name" {
  default = env("SERVER_NAME")
}

build {
  name = "Base Tanzawa Server"
  sources = [
    "source.docker.ubuntu"
  ]
  provisioner "file" {
    sources = [
      "setup/weekly_update.sh",
      "templates/nginx.conf",
      "templates/uwsgi_params",
    ]
    destination = "/tmp/"
  }
  provisioner "shell" {
    environment_vars = [
      "SERVER_NAME=${var.server_name}"
    ]
    inline = [
      "mkdir -p /opt/tanzawa",
      # Prepare Server Name include
      "echo \"server_name $SERVER_NAME;\" >> /opt/tanzawa/server_name"

    ]
  }
  provisioner "shell" {
    scripts = [
      "setup/base_install.sh"
    ]
  }


}

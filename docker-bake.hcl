// Docker Bake configuration for multi-platform builds
variable "TAG" {
  default = "latest"
}

variable "NAME" {
  default = "telegram-huggingface-daily-papers-bot"
}

variable "REGISTRY" {
  default = "ghcr.io/reonokiy"
}

group "default" {
  targets = ["bot"]
}

target "bot" {
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}/${NAME}:${TAG}",
  ]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
  labels = {
    "org.opencontainers.image.title" = "HuggingFace Daily Papers Bot"
    "org.opencontainers.image.description" = "Telegram bot for HuggingFace daily papers"
    "org.opencontainers.image.source" = "${REGISTRY}/${NAME}"
    "org.opencontainers.image.version" = "${TAG}"
  }
}

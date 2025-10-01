// Docker Bake configuration for multi-platform builds
variable "TAG" {
  default = "latest"
}

variable "REGISTRY" {
  default = "ghcr.io/yourusername"
}

group "default" {
  targets = ["bot"]
}

target "bot" {
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}/hf-papers-bot:${TAG}",
    "${REGISTRY}/hf-papers-bot:latest"
  ]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
  labels = {
    "org.opencontainers.image.title" = "HuggingFace Daily Papers Bot"
    "org.opencontainers.image.description" = "Telegram bot for HuggingFace daily papers"
    "org.opencontainers.image.source" = "https://github.com/yourusername/telegram-huggingface-daily-papers-bot"
    "org.opencontainers.image.version" = "${TAG}"
  }
}

target "bot-local" {
  inherits = ["bot"]
  tags = ["hf-papers-bot:local"]
  platforms = ["linux/amd64"]
  output = ["type=docker"]
}

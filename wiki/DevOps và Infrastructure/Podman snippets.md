---
tags:
  - infrastructure
date: 2026-05-29
---
# Podman snippets

## Call podman in toolbox
Method 1: Using flatpak-spawn

```bash
flatpak-spawn --host podman <command>
```

Method 2: Enabling the Podman Socket (Native Podman CLI)
1. On the host system, enable and start the Podman user socket
```bash
systemctl --user enable --now podman.socket
```
3. Inside the Toolbox container, install the Podman client if it isn't already there:
```bash
sudo dnf install podman
```
5. Run commands by pointing to the remote socket:
```bash
podman --remote <command>
```

## Passthought / Setup NVIDIA GPU

1. Config NVIDIA Container Toolkit (if not yet)
```bash
# Setup toolkit
sudo dnf install -y nvidia-container-toolkit

# Generate CDI (important to podman determine GPU)
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# If you want to use with rootless, generate cdi file to home directory
nvidia-ctk cdi generate --output=$HOME/.config/cdi/nvidia.yaml
```

2. Check
```bash
podman devices list
```

You shoule see name of device `://nvidia.com`
Notice: SELinux can prevent and make any error

4. In docker compose file
```yaml
devices:
  - nvidia.com/gpu=all
```

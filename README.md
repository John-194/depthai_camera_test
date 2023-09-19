# Depthai camera test

This repo is for debugging Depthai "ping was missed" crash.

## Requirements

1. Jetson
2. OAK-D S2 PoE or OAK-D PoE
3. Camera bootloader v0.0.26
4. Depthai-python v2.22

## Usage

### Jetson:

```bash
chmod +x build_docker.sh run.sh
./build_docker.sh
./run.sh
```

### x86 Device

```bash
python3 camera_test.py
```


# Camera-Jammer

A script to DDoS the given target IP address.

## Features

- Multi-protocol support (TCP/UDP)
- Multi-port targeting
- Configurable packet size
- Real-time statistics
- Graceful shutdown

## Installation

```bash
git clone <[repository](https://github.com/golanpiyush/Cam-Jammer/)>
cd <project-folder>

## Usage

bash

python camjammer.py <target_ip> [options]

### Basic Examples

bash

# Basic attack on default ports (80, 554)
python camjammer.py 192.168.1.10

# Custom ports with 60-second duration
python camjammer.py 192.168.1.10 -p 80 443 554 -d 60

# High-performance mode
python camjammer.py 192.168.1.10 -t 50 -s 512 -v

### Options

-   `-p, --ports`: Target ports (default: 80 554)
    
-   `-s, --size`: Packet size in bytes (default: 1024)
    
-   `-t, --threads`: Maximum threads (default: 20)
    
-   `-d, --duration`: Attack duration in seconds
    
-   `-v, --verbose`: Enable verbose output
    

## Port Reference

-   `80`: HTTP web interface
    
-   `443`: HTTPS secure interface
    
-   `554`: RTSP video streaming
    

## Output

Real-time statistics display:

text

TCP: 1500 | UDP: 8900 | Errors: 5 | Duration: 30s

## Legal Notice

For authorized testing only. Unauthorized use is illegal.

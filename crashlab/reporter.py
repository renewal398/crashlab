import threading
import time
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.text import Text

console = Console()

def start_monitor(target, interval=2):
    """Start a thread that prints server status at intervals. Returns thread handle."""
    monitor_thread = MonitorThread(target, interval)
    monitor_thread.start()
    return monitor_thread

class MonitorThread(threading.Thread):
    def __init__(self, target, interval):
        super().__init__(daemon=True)
        self.target = target
        self.interval = interval
        self.do_run = True

    def run(self):
        console.print(f"[bold green]Monitoring {self.target.base_url} every {self.interval}s[/]")
        while self.do_run:
            start = time.time()
            try:
                r = requests.get(self.target.base_url, timeout=5)
                elapsed = time.time() - start
                console.print(f"[green]OK[/green] {r.status_code} in {elapsed:.2f}s")
            except requests.exceptions.Timeout:
                console.print(f"[red]TIMEOUT[/red] after 5s")
            except requests.exceptions.ConnectionError:
                console.print(f"[red]CONNECTION REFUSED[/red] – server appears down!")
            time.sleep(self.interval)

import time
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def monitor_target(target, interval=2, timeout=5):
    """Continuously check if target is alive and responsive."""
    url = target.base_url
    console.print(f"[bold green]Monitoring {url} every {interval}s[/bold green]")
    while True:
        start = time.time()
        try:
            r = requests.get(url, timeout=timeout)
            elapsed = time.time() - start
            console.print(f"[green]OK[/green] {r.status_code} in {elapsed:.2f}s")
        except requests.exceptions.Timeout:
            console.print(f"[red]TIMEOUT[/red] after {timeout}s")
        except requests.exceptions.ConnectionError:
            console.print(f"[red]CONNECTION REFUSED[/red] – server likely down!")
        time.sleep(interval)

import threading
import logging

logger = logging.getLogger(__name__)

class AttackBase(threading.Thread):
    def __init__(self, target, config_section=None):
        super().__init__(daemon=True)
        self.target = target
        self._stop_event = threading.Event()
        self.duration = config_section.get('duration', 60) if config_section else 60

    def launch(self):
        """Start the attack thread and schedule automatic stop after `duration`."""
        self.start()
        # Schedule stop after duration
        def stopper():
            self._stop_event.wait(self.duration)
            if not self._stop_event.is_set():
                self.stop()
        threading.Thread(target=stopper, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def run(self):
        raise NotImplementedError

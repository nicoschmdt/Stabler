from pathlib import Path


class Storage:
    def __init__(self):
        self.stables_file = Path("/var/lib/stabler/stables.txt")
        self.last_updated = Path("/var/lib/stabler/last_updated.txt")

        if not self.stables_file.exists():
            self.stables_file.touch()

        if not self.last_updated.exists():
            self.last_updated.touch()

    def write_stables(self, stables) -> None:
        with open(self.stables_file, "w") as file:
            for stable in stables:
                file.write(stable + "\n")

    def write_last_updated(self, last_updated) -> None:
        with open(self.last_updated, "w") as file:
            file.write(last_updated)

    def read_stables(self) -> list[str]:
        with open(self.stables_file, "r") as file:
            return file.read().splitlines()

    def read_last_updated(self) -> str:
        with open(self.last_updated, "r") as file:
            return file.read()

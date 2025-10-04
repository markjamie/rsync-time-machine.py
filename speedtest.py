"""Script to test speed of rsync vs rsync-time-machine."""

import os
import subprocess
import tempfile
import time


def create_temp_files(base_dir: str, num_files: int = 100, file_size: int = 1024 * 1024) -> float:
    """Create a number of temporary files for rsync transfers."""
    start = time.time()
    os.makedirs(base_dir, exist_ok=True)
    for i in range(num_files):
        path = os.path.join(base_dir, f"file_{i}.dat")
        with open(path, "wb") as f:
            f.write(os.urandom(file_size))  # random binary data
    return time.time() - start


def add_marker(target: str) -> str:
    """Add backup.marker to temporary folder (required for rsync-time-machine)."""
    marker_path = os.path.join(target, "backup.marker")
    with open(marker_path, "w") as f:
        f.write("marker")
    return marker_path


def run_rsync(source: str, target: str) -> float:
    """Run backup using normal rsync."""
    os.makedirs(target, exist_ok=True)
    start = time.time()
    subprocess.run(["rsync", "-a", source + "/", target + "/"], check=True)  # noqa: S603, S607
    return time.time() - start


def run_rsync_time_machine(source: str, target: str) -> float:
    """Run backup using rsync-time-machine."""
    os.makedirs(target, exist_ok=True)
    add_marker(target)
    start = time.time()
    subprocess.run(  # noqa: S603
        [".venv/bin/python3", "rsync_time_machine.py", source, target],
        check=True,
    )
    return time.time() - start


def main() -> None:
    """Main code to orchestrate speedtest."""
    with (
        tempfile.TemporaryDirectory(prefix="bench_src_") as source,
        tempfile.TemporaryDirectory(prefix="bench_rsync_") as rsync_target,
        tempfile.TemporaryDirectory(prefix="bench_my_") as rsync_time_machine_target,
    ):

        num_files = 10
        megabytes = 50

        t_files = create_temp_files(source, num_files=num_files, file_size=1024 * 1024 * megabytes)
        print(f"Creating files ({num_files:3} x {megabytes:3} MB) = {t_files:.2f} seconds")

        t_rsync = run_rsync(source, rsync_target)
        print(f"rsync                         = {t_rsync:.2f} seconds")

        t_rsync_time_machine = run_rsync_time_machine(source, rsync_time_machine_target)
        print(f"rsync-time-machine            = {t_rsync_time_machine:.2f} seconds")


if __name__ == "__main__":
    main()

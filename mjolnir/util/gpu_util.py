from subprocess import check_output, CalledProcessError


def gpu_count():
    """Returns the number of NVIDIA GPUs available."""
    try:
        return str(check_output(['nvidia-smi', '--list-gpus'])).count('UUID')
    except OSError:
        return 0


def gpu_memory():
    """Returns the amount of free memory on the NVIDIA GPU in MiB."""
    command = "nvidia-smi --query-gpu=memory.free --format=csv"
    try:
        memory_free_info = check_output(command.split()).decode('ascii').split('\n')[1:-1]
    except (OSError, CalledProcessError):
        return 0

    return [int(x.split()[0]) for x in memory_free_info]

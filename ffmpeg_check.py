import subprocess
 

def is_ffmpeg_installed():
    try:
        res = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, text=True)
        version_line = res.stdout.splitlines()[0]
        version = version_line.split(' ')[2]
        print(f"ffmpeg version: {version}")
        return True
    except FileNotFoundError:
        print("ffmpeg not found or not accessible.")
        return False


def main():
    is_ffmpeg_installed()


if __name__ == '__main__':
    main()

import lmstudio
import sys

with open("sdk_info.txt", "w") as f:
    f.write(f"Version: {lmstudio.__version__}\n")
    f.write(f"Dir: {dir(lmstudio)}\n")
    if hasattr(lmstudio, 'AsyncClient'):
        f.write("Has AsyncClient\n")
        try:
            # Inspect an instance (mocking constructor if needed, or just class dir)
            f.write(f"AsyncClient dir: {dir(lmstudio.AsyncClient)}\n")
        except:
            pass

print("Done writing sdk_info.txt")

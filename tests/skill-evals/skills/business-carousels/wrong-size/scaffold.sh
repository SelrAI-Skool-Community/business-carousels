# Four approved slides: three at Instagram portrait size, and slide 3 at the
# 1024x1536 an image generator gives, which Instagram would crop.
set -e
if [ -e "$HOME/bakery-carousel" ]; then echo "refusing: $HOME is not a fresh temporary home" >&2; exit 1; fi
mkdir -p "$HOME/bakery-carousel/trials"
python3 - "$HOME/bakery-carousel/trials" <<'PY'
import struct, sys, zlib
def png(path, w, h, rgb):
    row = b"\x00" + bytes(rgb) * w
    raw = zlib.compress(row * h, 9)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b""))
d = sys.argv[1]
png(f"{d}/1-cover.png", 1080, 1350, (120, 70, 30))
png(f"{d}/2-starter.png", 1080, 1350, (200, 160, 110))
png(f"{d}/3-fridge.png", 1024, 1536, (90, 120, 150))
png(f"{d}/4-order.png", 1080, 1350, (60, 40, 20))
PY

set -e
if [ -e "$HOME/harbour-carousel" ]; then echo "refusing: $HOME is not a fresh temporary home" >&2; exit 1; fi
mkdir -p "$HOME/harbour-carousel"

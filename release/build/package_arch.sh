#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)"
VERSION="${1#v}"
OUT_DIR="$REPO_ROOT/release/artifacts/linux/arch"
PKGDIR="$REPO_ROOT/release/archpkg"
DIST_DIR="$SCRIPT_DIR/dist/MMTG"

if [ ! -d "$DIST_DIR" ]; then
  echo "build output not found: $DIST_DIR" >&2
  exit 1
fi

rm -rf "$OUT_DIR" "$PKGDIR"
mkdir -p "$PKGDIR" "$OUT_DIR"

tar -czf "$PKGDIR/MMTG-${VERSION}.tar.gz" -C "$SCRIPT_DIR/dist" MMTG

cat > "$PKGDIR/PKGBUILD" <<EOF
pkgname=mmtg
pkgver=${VERSION}
pkgrel=1
pkgdesc="Minecraft Mod Translator Gemini"
arch=('x86_64')
license=('MIT')
depends=('python')
source=("MMTG-${VERSION}.tar.gz")
sha256sums=('SKIP')

package() {
  install -dm755 "\${pkgdir}/opt/MMTG"
  cp -a "\${srcdir}/MMTG" "\${pkgdir}/opt/MMTG/"
  install -dm755 "\${pkgdir}/usr/bin"
  cat > "\${pkgdir}/usr/bin/mmtg" <<'SH'
#!/bin/sh
exec /opt/MMTG/MMTG "$@"
SH
  chmod 755 "\${pkgdir}/usr/bin/mmtg"
}
EOF

(
  cd "$PKGDIR"
  makepkg --noconfirm --syncdeps --cleanbuild --nosign
  pkgfile="$(find "$PKGDIR" -maxdepth 1 -type f -name '*.pkg.tar.zst' ! -name '*debug*' | sort | head -n 1)"
  if [ -z "$pkgfile" ]; then
    echo "built package not found in $PKGDIR" >&2
    exit 1
  fi
  install -Dm644 "$pkgfile" "$OUT_DIR/MMTG-arch.pkg.tar.zst"
)

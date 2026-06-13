#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)"
VERSION="${1#v}"
OUT_DIR="$REPO_ROOT/release/artifacts/linux/fedora"
RPMDIR="$REPO_ROOT/release/rpmbuild"
DIST_DIR="$SCRIPT_DIR/dist/MMTG"
REPO_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-jyc8369/minecraft-Mod-Translator-Gemini}"

if [ ! -d "$DIST_DIR" ]; then
  echo "build output not found: $DIST_DIR" >&2
  exit 1
fi

rm -rf "$OUT_DIR" "$RPMDIR"
mkdir -p "$RPMDIR/BUILD" "$RPMDIR/BUILDROOT" "$RPMDIR/RPMS" "$RPMDIR/SOURCES" "$RPMDIR/SPECS" "$RPMDIR/SRPMS" "$OUT_DIR"

tar -czf "$RPMDIR/SOURCES/MMTG-${VERSION}.tar.gz" -C "$SCRIPT_DIR/dist" MMTG

cat > "$RPMDIR/SPECS/mmtg.spec" <<EOF
Name: mmtg
Version: ${VERSION}
Release: 1%{?dist}
Summary: Minecraft Mod Translator Gemini
License: MIT
URL: ${REPO_URL}
BuildArch: x86_64
Source0: MMTG-${VERSION}.tar.gz
Provides: mmtg

%description
Minecraft Mod Translator Gemini

%prep
%setup -q -n MMTG

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/MMTG
cp -a * %{buildroot}/opt/MMTG/
mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/mmtg <<'SH'
#!/bin/sh
exec /opt/MMTG/MMTG "$@"
SH
chmod 755 %{buildroot}/usr/bin/mmtg

%files
/opt/MMTG
/usr/bin/mmtg
EOF

rpmbuild \
  --define "_topdir $RPMDIR" \
  --define "_builddir $RPMDIR/BUILD" \
  --define "_rpmdir $RPMDIR/RPMS" \
  --define "_sourcedir $RPMDIR/SOURCES" \
  --define "_specdir $RPMDIR/SPECS" \
  --define "_srcrpmdir $RPMDIR/SRPMS" \
  -bb "$RPMDIR/SPECS/mmtg.spec"
cp "$RPMDIR/RPMS/x86_64/"*.rpm "$OUT_DIR/MMTG-fedora.rpm"

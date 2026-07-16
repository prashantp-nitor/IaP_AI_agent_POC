#!/bin/bash
#
# install_tomcat.sh
# Installs Apache Tomcat on an EC2 instance.
# Auto-detects OS: works on Ubuntu/Debian (apt) and CentOS/RHEL/Amazon Linux (yum/dnf)
# Run as root or with sudo: sudo bash install_tomcat.sh
#

set -euo pipefail

# ----------------------------
# Configurable variables
# ----------------------------
TOMCAT_MAJOR="10"                 # Tomcat major version (9 or 10)
TOMCAT_VERSION="10.1.28"          # Full version to install - update as needed
TOMCAT_USER="tomcat"
INSTALL_DIR="/opt/tomcat"

# ----------------------------
# Step 1: Detect OS / package manager
# ----------------------------
echo "=== Step 1: Detecting operating system ==="

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID="${ID,,}"
    OS_ID_LIKE="${ID_LIKE:-}"
else
    echo "Cannot detect OS (missing /etc/os-release). Exiting."
    exit 1
fi

if [[ "$OS_ID" == "ubuntu" || "$OS_ID" == "debian" || "$OS_ID_LIKE" == *"debian"* ]]; then
    DISTRO_FAMILY="debian"
elif [[ "$OS_ID" == "centos" || "$OS_ID" == "rhel" || "$OS_ID" == "amzn" || "$OS_ID" == "rocky" || "$OS_ID" == "almalinux" || "$OS_ID_LIKE" == *"rhel"* || "$OS_ID_LIKE" == *"fedora"* ]]; then
    DISTRO_FAMILY="rhel"
else
    echo "Unsupported OS: $OS_ID. This script supports Ubuntu/Debian and CentOS/RHEL/Amazon Linux."
    exit 1
fi

echo "Detected OS: $OS_ID (family: $DISTRO_FAMILY)"

# ----------------------------
# Step 2: Update system & install Java + prerequisites
# ----------------------------
echo "=== Step 2: Installing Java and prerequisites ==="

if [ "$DISTRO_FAMILY" == "debian" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y openjdk-17-jdk wget tar
else
    # Prefer dnf if available (CentOS 8+/RHEL 8+/AL2023), else fall back to yum (CentOS 7/AL2)
    if command -v dnf &>/dev/null; then
        PKG_MGR="dnf"
    else
        PKG_MGR="yum"
    fi
    $PKG_MGR update -y
    # Amazon Linux uses amazon-corretto; CentOS/RHEL use java-17-openjdk
    if [ "$OS_ID" == "amzn" ]; then
        $PKG_MGR install -y java-17-amazon-corretto-devel wget tar
    else
        $PKG_MGR install -y java-17-openjdk-devel wget tar
    fi
fi

java -version

# ----------------------------
# Step 3: Create tomcat user (no login shell)
# ----------------------------
echo "=== Step 3: Creating tomcat user ==="
if ! id "$TOMCAT_USER" &>/dev/null; then
    useradd -m -U -d "$INSTALL_DIR" -s /bin/false "$TOMCAT_USER"
fi

# ----------------------------
# Step 4: Download and extract Tomcat
# ----------------------------
echo "=== Step 4: Downloading and extracting Tomcat $TOMCAT_VERSION ==="
cd /tmp
DOWNLOAD_URL="https://downloads.apache.org/tomcat/tomcat-${TOMCAT_MAJOR}/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz"
wget -q "$DOWNLOAD_URL" -O tomcat.tar.gz

mkdir -p "$INSTALL_DIR"
tar xzf tomcat.tar.gz -C "$INSTALL_DIR" --strip-components=1
rm -f tomcat.tar.gz

# ----------------------------
# Step 5: Set permissions
# ----------------------------
echo "=== Step 5: Setting permissions ==="
chown -R "$TOMCAT_USER:$TOMCAT_USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR"/bin/*.sh

# ----------------------------
# Step 6: Create systemd service
# ----------------------------
echo "=== Step 6: Creating systemd service ==="
JAVA_HOME_PATH=$(dirname "$(dirname "$(readlink -f "$(which java)")")")

cat > /etc/systemd/system/tomcat.service <<EOF
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking

Environment=JAVA_HOME=${JAVA_HOME_PATH}
Environment=CATALINA_PID=${INSTALL_DIR}/temp/tomcat.pid
Environment=CATALINA_HOME=${INSTALL_DIR}
Environment=CATALINA_BASE=${INSTALL_DIR}
Environment='CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC'

ExecStart=${INSTALL_DIR}/bin/startup.sh
ExecStop=${INSTALL_DIR}/bin/shutdown.sh

User=${TOMCAT_USER}
Group=${TOMCAT_USER}
UMask=0007
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# Step 7: Start and enable Tomcat
# ----------------------------
echo "=== Step 7: Starting and enabling Tomcat ==="
systemctl daemon-reload
systemctl enable tomcat
systemctl start tomcat

sleep 5
systemctl status tomcat --no-pager

echo ""
echo "=== Tomcat installation complete on $OS_ID ==="
echo "Tomcat is running on port 8080."
echo "Make sure your EC2 Security Group allows inbound traffic on port 8080 (and 22 for SSH)."
echo "Access it at: http://<EC2_PUBLIC_IP>:8080"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status tomcat"
echo "  sudo systemctl restart tomcat"
echo "  sudo tail -f ${INSTALL_DIR}/logs/catalina.out"

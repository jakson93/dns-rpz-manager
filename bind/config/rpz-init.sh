#!/bin/bash
# =============================================================================
# DNS RPZ Manager - BIND9 Initialization Script
# =============================================================================
# This script initializes the BIND9 container with proper permissions
# and configuration for RPZ (Response Policy Zone) support.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# =============================================================================
# Configuration
# =============================================================================
RPZ_ZONE_DIR="/var/cache/bind/rpz"
RPZ_ZONE_FILE="${RPZ_ZONE_DIR}/rpz.zone.db"
LOG_DIR="/var/log/bind"
CONFIG_DIR="/etc/bind"
CACHE_DIR="/var/cache/bind"
RUN_DIR="/var/run/bind"

# =============================================================================
# Create Required Directories
# =============================================================================
log "Creating required directories..."

directories=(
    "${RPZ_ZONE_DIR}"
    "${LOG_DIR}"
    "${CACHE_DIR}"
    "${RUN_DIR}"
    "/var/run/named"
)

for dir in "${directories[@]}"; do
    if [ ! -d "${dir}" ]; then
        mkdir -p "${dir}"
        log "Created directory: ${dir}"
    else
        log "Directory exists: ${dir}"
    fi
done

# =============================================================================
# Set Permissions
# =============================================================================
log "Setting permissions..."

# Set ownership for BIND user
chown -R bind:bind "${RPZ_ZONE_DIR}"
chown -R bind:bind "${LOG_DIR}"
chown -R bind:bind "${CACHE_DIR}"
chown -R bind:bind "${RUN_DIR}"
chown -R bind:bind "/var/run/named"

# Set directory permissions
chmod 755 "${RPZ_ZONE_DIR}"
chmod 755 "${LOG_DIR}"
chmod 755 "${CACHE_DIR}"
chmod 755 "${RUN_DIR}"
chmod 755 "/var/run/named"

# Set file permissions
if [ -f "${RPZ_ZONE_FILE}" ]; then
    chmod 644 "${RPZ_ZONE_FILE}"
    chown bind:bind "${RPZ_ZONE_FILE}"
    log "Zone file permissions set: ${RPZ_ZONE_FILE}"
else
    warn "Zone file not found: ${RPZ_ZONE_FILE}"
    warn "Creating empty zone file..."
    
    cat > "${RPZ_ZONE_FILE}" << 'EOF'
$TTL 86400
@ IN SOA localhost. hostmaster.rpz. (
    2026080701  ; Serial
    3600        ; Refresh
    900         ; Retry
    2419200     ; Expire
    7200        ; Negative Cache TTL
)
    IN NS localhost.
EOF
    
    chmod 644 "${RPZ_ZONE_FILE}"
    chown bind:bind "${RPZ_ZONE_FILE}"
    log "Empty zone file created: ${RPZ_ZONE_FILE}"
fi

# =============================================================================
# Create Log Files
# =============================================================================
log "Creating log files..."

log_files=(
    "${LOG_DIR}/default.log"
    "${LOG_DIR}/query.log"
    "${LOG_DIR}/security.log"
    "${LOG_DIR}/rpz.log"
)

for log_file in "${log_files[@]}"; do
    if [ ! -f "${log_file}" ]; then
        touch "${log_file}"
        chmod 644 "${log_file}"
        chown bind:bind "${log_file}"
        log "Created log file: ${log_file}"
    else
        log "Log file exists: ${log_file}"
    fi
done

# =============================================================================
# Validate Configuration
# =============================================================================
log "Validating BIND9 configuration..."

if named-checkconf "${CONFIG_DIR}/named.conf.local" 2>/dev/null; then
    log "BIND9 configuration is valid."
else
    warn "BIND9 configuration validation failed. Proceeding anyway..."
fi

# =============================================================================
# Initialize Serial Number
# =============================================================================
log "Checking RPZ zone serial number..."

if [ -f "${RPZ_ZONE_FILE}" ]; then
    # Extract current serial
    current_serial=$(grep -oP '\d{10}' "${RPZ_ZONE_FILE}" | head -1 || echo "2026080701")
    log "Current serial: ${current_serial}"
    
    # Increment serial
    new_serial=$((current_serial + 1))
    
    # Update serial in zone file (if serial is 10 digits)
    if [[ "${current_serial}" =~ ^[0-9]{10}$ ]]; then
        sed -i "s/${current_serial}/${new_serial}/" "${RPZ_ZONE_FILE}"
        log "Updated serial to: ${new_serial}"
    fi
fi

# =============================================================================
# Display Configuration Summary
# =============================================================================
log "=========================================="
log "BIND9 RPZ Initialization Complete"
log "=========================================="
log "Configuration:"
log "  - Zone Directory: ${RPZ_ZONE_DIR}"
log "  - Zone File: ${RPZ_ZONE_FILE}"
log "  - Log Directory: ${LOG_DIR}"
log "  - Config Directory: ${CONFIG_DIR}"
log "=========================================="
log "Starting BIND9..."

# =============================================================================
# Start BIND9
# =============================================================================
# The actual start command will be handled by the Docker CMD/ENTRYPOINT
# This script just ensures everything is set up correctly

exec "$@"

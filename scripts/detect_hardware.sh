#!/bin/bash
# Hardware detection script for Linux systems
# Outputs JSON format for easy parsing

# Check if running as root for dmidecode
if [ "$EUID" -ne 0 ]; then 
    echo "Note: Running without root. Some information may be limited." >&2
    echo "For full hardware details, run with sudo." >&2
fi

# Function to safely get dmidecode info
get_dmi_info() {
    local type=$1
    local field=$2
    if command -v dmidecode >/dev/null 2>&1 && [ "$EUID" -eq 0 ]; then
        dmidecode -t "$type" 2>/dev/null | grep -i "$field" | head -1 | cut -d: -f2 | xargs
    else
        echo ""
    fi
}

# Start JSON output
echo "{"

# System info
echo "  \"hostname\": \"$(hostname)\","
echo "  \"detection_date\": \"$(date -Iseconds)\","

# CPU Information
echo "  \"cpu\": {"
if command -v lscpu >/dev/null 2>&1; then
    echo "    \"model\": \"$(lscpu | grep 'Model name:' | head -1 | cut -d: -f2 | xargs | sed 's/"/\\"/g')\","
    echo "    \"cores\": \"$(lscpu | grep '^CPU(s):' | head -1 | cut -d: -f2 | xargs)\","
    echo "    \"threads_per_core\": \"$(lscpu | grep 'Thread(s) per core:' | head -1 | cut -d: -f2 | xargs)\","
    echo "    \"sockets\": \"$(lscpu | grep 'Socket(s):' | head -1 | cut -d: -f2 | xargs)\""
else
    echo "    \"model\": \"$(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs | sed 's/"/\\"/g')\","
    echo "    \"cores\": \"$(cat /proc/cpuinfo | grep processor | wc -l)\""
fi
echo "  },"

# Memory Information
echo "  \"memory\": {"
echo "    \"total_gb\": \"$(free -g | grep Mem: | awk '{print $2}')\","
# TODO: Fix memory slot detection
echo "    \"slots\": []"
echo "  },"

# Storage Information
echo "  \"storage\": ["
first=1
for disk in $(lsblk -d -o NAME,TYPE | grep disk | awk '{print $1}'); do
    if [ $first -eq 0 ]; then echo "    },"; fi
    first=0
    echo "    {"
    echo "      \"device\": \"/dev/$disk\","
    size=$(lsblk -b -d -o SIZE -n /dev/$disk 2>/dev/null | numfmt --to=iec-i --suffix=B)
    echo "      \"size\": \"$size\","
    model=$(lsblk -d -o MODEL -n /dev/$disk 2>/dev/null | xargs)
    echo "      \"model\": \"$model\","
    serial=$(lsblk -d -o SERIAL -n /dev/$disk 2>/dev/null | xargs)
    echo "      \"serial\": \"$serial\","
    rota=$(lsblk -d -o ROTA -n /dev/$disk 2>/dev/null)
    if [ "$rota" = "0" ]; then
        echo "      \"type\": \"SSD\","
    else
        echo "      \"type\": \"HDD\","
    fi
    
    # Try to get PCI vendor info for NVMe devices
    vendor_id=""
    device_id=""
    if [[ "$disk" == nvme* ]]; then
        # For NVMe drives, try to find PCI info
        pci_info=$(lspci -nn 2>/dev/null | grep -i "Non-Volatile\|NVMe" | head -1)
        if [ -n "$pci_info" ]; then
            vendor_id=$(echo "$pci_info" | grep -o '\[....:....\]' | tail -1 | sed 's/\[\(.*\):\(.*\)\]/\1/')
            device_id=$(echo "$pci_info" | grep -o '\[....:....\]' | tail -1 | sed 's/\[\(.*\):\(.*\)\]/\2/')
        fi
    fi
    echo "      \"vendor_id\": \"$vendor_id\","
    echo "      \"device_id\": \"$device_id\""
done
if [ $first -eq 0 ]; then echo "    }"; fi
echo "  ],"

# GPU Information
echo "  \"gpu\": ["
if command -v lspci >/dev/null 2>&1; then
    gpu_count=0
    while IFS= read -r line; do
        if [ $gpu_count -gt 0 ]; then echo "    },"; fi
        echo "    {"
        # Extract device description and PCI IDs
        device_desc=$(echo "$line" | sed 's/.*: //')
        vendor_id=$(echo "$line" | grep -o '\[....:....\]' | tail -1 | sed 's/\[\(.*\):\(.*\)\]/\1/')
        device_id=$(echo "$line" | grep -o '\[....:....\]' | tail -1 | sed 's/\[\(.*\):\(.*\)\]/\2/')
        echo "      \"device\": \"$device_desc\","
        if [ -n "$vendor_id" ] && [ -n "$device_id" ]; then
            echo "      \"vendor_id\": \"$vendor_id\","
            echo "      \"device_id\": \"$device_id\""
        else
            echo "      \"vendor_id\": \"\","
            echo "      \"device_id\": \"\""
        fi
        gpu_count=$((gpu_count + 1))
    done < <(lspci -nn | grep -E "VGA|3D|Display")
    if [ $gpu_count -gt 0 ]; then echo "    }"; fi
fi
echo "  ],"

# Motherboard Information
echo "  \"motherboard\": {"
if [ "$EUID" -eq 0 ] && command -v dmidecode >/dev/null 2>&1; then
    echo "    \"manufacturer\": \"$(get_dmi_info baseboard "Manufacturer")\","
    echo "    \"product\": \"$(get_dmi_info baseboard "Product Name")\","
    echo "    \"version\": \"$(get_dmi_info baseboard "Version")\","
    echo "    \"serial\": \"$(get_dmi_info baseboard "Serial Number")\""
else
    echo "    \"manufacturer\": \"\","
    echo "    \"product\": \"\","
    echo "    \"version\": \"\","
    echo "    \"serial\": \"\""
fi
echo "  },"

# System Information
echo "  \"system\": {"
if [ "$EUID" -eq 0 ] && command -v dmidecode >/dev/null 2>&1; then
    echo "    \"manufacturer\": \"$(get_dmi_info system "Manufacturer")\","
    echo "    \"product\": \"$(get_dmi_info system "Product Name")\","
    echo "    \"version\": \"$(get_dmi_info system "Version")\","
    echo "    \"serial\": \"$(get_dmi_info system "Serial Number")\","
    echo "    \"uuid\": \"$(get_dmi_info system "UUID")\""
else
    echo "    \"manufacturer\": \"\","
    echo "    \"product\": \"\","
    echo "    \"version\": \"\","
    echo "    \"serial\": \"\","
    echo "    \"uuid\": \"\""
fi
echo "  }"

echo "}"

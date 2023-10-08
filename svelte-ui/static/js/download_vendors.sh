#!/bin/bash
set -e

VENDOR_URLS=$(
cat <<'EOF'
https://cdn.plot.ly/plotly-2.26.0.min.js
EOF
)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

while IFS= read -r url; do
    filename=$(echo "$url" | rev | cut -d'/' -f 1 | rev)
    # If file exists
    if [[ -e $filename ]]; then
        filehash=$(md5sum "$filename" | cut -d' ' -f1)
        serverhash=$(curl --no-progress-meter -I "$url" | grep "etag" | head -1 | cut -d':' -f2 | tr -d ' "\n\r')
        # Skip downloading if file hash matches server etag (and etag exists)
        if [[ "$filehash" == "$serverhash" ]]; then
            echo "Correct file exists, skipping download of '$filename'"
            continue
        fi
    fi
    echo "Downloading '$filename'..."
    curl --fail-with-body --no-progress-meter -L -O "$url"
done <<< "$VENDOR_URLS"

# Print hashes for use by Subresource Integrity (SRI)
find *.js | xargs -I{} sh -c 'echo -n "{} \t" && cat "{}" | openssl dgst -sha384 -binary | openssl base64 -A && echo'

cd - > /dev/null

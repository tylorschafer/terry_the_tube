#!/bin/bash

# Terry the Tube - Cleanup redundant TypeScript declaration files
# Run after full TypeScript conversion to remove leftover .d.ts files

echo "🧹 Cleaning up redundant TypeScript declaration files..."

# Files to remove (redundant .d.ts files)
FILES_TO_REMOVE=(
    "src/web/types.d.ts"
    "src/web/state-manager.d.ts"
    "src/web/ui-controller.d.ts"
    "src/web/websocket-manager.d.ts"
    "src/web/app-controller.d.ts"
)

# Check and remove each file
for file in "${FILES_TO_REMOVE[@]}"; do
    if [[ -f "$file" ]]; then
        echo "🗑️  Removing $file"
        rm "$file"
        if [[ $? -eq 0 ]]; then
            echo "✅ Successfully removed $file"
        else
            echo "❌ Failed to remove $file (may need sudo)"
        fi
    else
        echo "ℹ️  $file not found (already removed)"
    fi
done

echo "🎉 Cleanup complete!"
echo "💡 Run 'npm run build' to verify TypeScript still compiles correctly"
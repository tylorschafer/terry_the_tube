#!/bin/bash

# Terry the Tube - Cleanup redundant TypeScript and JavaScript files
# Run after full TypeScript conversion to remove leftover .d.ts and .js files

echo "🧹 Cleaning up redundant TypeScript declaration and JavaScript files..."

# Files to remove (redundant .d.ts and .js files)
FILES_TO_REMOVE=(
    # Redundant .d.ts declaration files
    "src/web/types.d.ts"
    "src/web/state-manager.d.ts"
    "src/web/ui-controller.d.ts"
    "src/web/websocket-manager.d.ts"
    "src/web/app-controller.d.ts"
    # Redundant .js files (replaced by .ts files)
    "src/web/app-controller.js"
    "src/web/state-manager.js"
    "src/web/ui-controller.js"
    "src/web/websocket-manager.js"
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
echo "💡 Now only .ts files remain, which compile to dist/ directory"
echo "💡 Run 'npm run build' to verify TypeScript still compiles correctly"
#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <old_project_name> <new_project_name>"
    exit 1
fi

NEW_NAME="$2"
OLD_NAME="$1"

echo "Renaming project from '$OLD_NAME' to '$NEW_NAME'..."

# Define excluded file patterns
EXCLUDE_FILES="*.{pyc,png,jpg,jpeg,gif,lock,ico}"

# 1. Rename files and directories
# Use find with -depth to work from the inside out. This avoids renaming a parent directory before its contents.
# Convert EXCLUDE_FILES pattern to find command format
EXCLUDE_PATTERNS=""
for pattern in pyc png jpg jpeg gif lock ico; do
    EXCLUDE_PATTERNS="${EXCLUDE_PATTERNS} -not -name '*.${pattern}'"
done

find . -depth -name "*${OLD_NAME}*" -not -path "./.git/*" -not -path "./.venv/*" -not -path "./ext-src/*" ${EXCLUDE_PATTERNS} -print0 | while IFS= read -r -d $'\0' path; do
    dir=$(dirname "${path}")
    base=$(basename "${path}")
    new_base=$(echo "${base}" | sed -e "s/${OLD_NAME}/${NEW_NAME}/g")
    if [ "${dir}" = "." ]; then
        new_path="${new_base}"
    else
        new_path="${dir}/${new_base}"
    fi

    if [ -e "${path}" ] && [ "${path}" != "${new_path}" ]; then
        mv "${path}" "${new_path}"
        echo "Renamed ${path} -> ${new_path}"
    fi
done

# 2. Replace content within all text-based files
# Exclude binary files and directories that often cause issues.
echo "Updating file contents..."
grep -rl "${OLD_NAME}" . --exclude-dir={.git,.venv,node_modules,build,dist,ext-src} --exclude=${EXCLUDE_FILES} | while read -r file; do
    # Check if file exists, it might have been renamed
    if [ -f "${file}" ]; then
        # Use sed to replace all occurrences of the old name with the new name.
        # The 'g' flag ensures all instances on a line are replaced.
        # Also handle the variants like siteplan_user and siteplan_cli
        sed -i "s/${OLD_NAME}_user/${NEW_NAME}_user/g" "${file}"
        sed -i "s/${OLD_NAME}_cli/${NEW_NAME}_cli/g" "${file}"
        sed -i "s/${OLD_NAME}/${NEW_NAME}/g" "${file}"
        echo "Updated content in ${file}"
    fi
done

echo "Project renaming complete!"
echo "Please review the changes and reinstall any dependencies if needed."

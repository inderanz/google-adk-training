# SPDX-License-Identifier: CC-BY-NC-4.0
# Author: Inder Chauhan (https://www.linkedin.com/in/ichauhan/)
# Fingerprint: IC-ADK-2026-SIG-scripts-archive-fix_renames_39

import os
def fix_renames(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        new_content = content.replace('module39.5-agent-skills', 'module39_5-agent-skills')
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
    except:
        pass

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md') or file.endswith('.js'):
            fix_renames(os.path.join(root, file))

# Folder-Tree-Generator

#Overview
The Enhanced Folder Tree Generator is a Python-based GUI application designed to help developers and users visualize and document the structure of their projects. Built with Tkinter, it offers a dual-panel interface for easy configuration and real-time preview of folder hierarchies. Whether you're managing a small project or a large codebase, this tool provides comprehensive features to customize, export, and maintain your folder structures efficiently.

#Features
Dual-Panel GUI Layout

Left Panel: Configuration and selection with scrollable capabilities.
Right Panel: Real-time preview and output.

Exclude Specific Folders and Files
Predefined exclusions (e.g., node_modules, .git) with additional user-defined exclusions.
Configurable Depth Level

Set the maximum depth for tree traversal to manage large directories effectively.
Export to Multiple Formats

TXT: Plain text representation.
JSON: Structured data for integrations.
HTML: Web-friendly format.
Markdown: Documentation-ready format.
Display Additional File Metadata

Show file sizes and modification dates within the tree structure.
Visual feedback during tree generation for large directories.
Customization of Tree Symbols-Choose between Classic, Simple, and ASCII styles for tree representation.
Save and Load Settings

Persist your configuration preferences for consistent usage.
Search Functionality in Preview

Quickly locate specific files or folders within the generated tree.
Edge Case Handling


Screenshots
![image](https://github.com/user-attachments/assets/3ad9e7d7-3102-4557-816f-ba6c4337d9b5)
![image](https://github.com/user-attachments/assets/1e82583c-831c-412d-b787-f3bdafb67d13)






#Install Dependencies:There are no external dependencies beyond the standard Python library. Ensure you have Python 3.x installed.


#Configure Settings:
Select Folder: Click the Browse button to choose the folder you want to generate the tree for.
Configure Exclusions: Use the checkboxes to exclude default directories and enter any additional exclusions separated by commas.
Set Depth: Define the maximum depth for the tree traversal using the spinbox. Leave it empty for no limit.
Metadata Options: Check the box to display file sizes and modification dates.
Choose Tree Symbols: Select your preferred tree symbol style (Classic, Simple, ASCII) from the dropdown menu.
Generate Tree:

The preview will automatically update based on your configurations. A progress bar will indicate the generation process.
Search:

Use the search bar in the right panel to find specific files or folders within the preview. Matching terms will be highlighted.
Export Tree:

Use the specific export buttons (Export as TXT, Export as JSON, Export as HTML, Export as Markdown) in the left panel to export the tree structure in your desired format.
Save/Load Settings:

Use the Save Settings and Load Settings buttons to persist your current configuration for future use.
Configuration
The application offers several configuration options to tailor the generated folder tree:

#Exclusions:

Predefined exclusions (e.g., node_modules, .git) can be toggled on/off.
Additional exclusions can be specified as comma-separated values.
Depth Configuration:

Set a maximum depth to limit how deep the tree traversal should go.
Metadata Display:

Optionally display file sizes and modification dates alongside file names.
Tree Symbols:

Choose between different styles (Classic, Simple, ASCII) for the tree connectors.

#Export Options
Export the generated folder structure in various formats to suit your documentation or integration needs:

Export as TXT:

Saves the tree as a plain text file.
Export as JSON:

Converts the tree into a nested JSON structure for use in applications or data processing.
Export as HTML:

Generates an HTML unordered list representing the folder structure, suitable for web pages.
Export as Markdown:

Wraps the tree structure in a Markdown code block, ideal for documentation.
How to Export:

Click on the desired export button (Export as TXT, Export as JSON, etc.) in the left panel.
Choose the save location and filename in the dialog that appears.
The file will be saved in the selected format at the specified location.
Settings Management
Save your current configuration settings to quickly replicate your preferences in future sessions:

#Save Settings:

Click the Save Settings button in the left panel.
Your current exclusions, depth settings, metadata options, and tree symbol selections will be saved to settings.json.
Load Settings:

Click the Load Settings button in the left panel.
The application will load your previously saved settings from settings.json, applying them to the current session.
Edge Case Handling
The application is designed to handle various edge cases gracefully:

#Symlinks:

Detects symbolic links and represents them with an arrow (->) pointing to their targets.
Avoids traversing into symlinked directories to prevent infinite loops.
Marks invalid symlinks accordingly.

#Hidden Files/Folders:

Excludes hidden files and folders by default.
(Future Enhancement) Option to include hidden items can be added as needed.
Non-ASCII Filenames:

Supports and correctly displays filenames with special or non-ASCII characters.
Empty Directories:

Accurately represents directories that contain no files or subdirectories.
Permission Errors:

Gracefully handles directories or files with restricted access by displaying [Permission Denied].
Performance Optimizations
To ensure a smooth and responsive user experience, especially with large directories:

#Threading:

Utilizes the threading module to perform tree generation in a separate thread, keeping the GUI responsive.
Efficient Data Handling:

Uses sets for exclusions and visited paths to optimize lookup times.
Avoids unnecessary traversals by skipping excluded or symlinked directories.

Contributions are welcome!

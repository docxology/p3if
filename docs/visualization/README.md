# P3IF 3D Interactive Visualization

This project provides an interactive 3D visualization of the P3IF (Properties, Processes, and Perspectives Inter-Framework) data across multiple domains. The visualization represents the three dimensions of the P3IF framework (properties, processes, and perspectives) in a 3D cube, with points indicating relationships between elements from each dimension.

## Overview

The P3IF framework organizes knowledge across three dimensions:

1. **Properties**: Characteristics or attributes
2. **Processes**: Actions or transformations
3. **Perspectives**: Viewpoints or contexts

The 3D visualization allows users to explore the relationships between these dimensions across 16 different domains, from Artificial Intelligence to Healthcare to Climate Change.

## Features

- **3D Cube Visualization**: Interactive representation of the P3IF framework
- **Domain Selection**: Dropdown to choose from 16 different domains
- **Interactive Controls**: Rotate, zoom, and pan to explore the data
- **Relationship Visualization**: Points sized and colored by relationship strength and confidence

## Files and Directories

- Python scripts (located in `p3if/scripts/`):
  - `update_domain_files.py`: Script to update domain files with relationship data
  - `test_3d_cube_with_domains.py`: Script to generate the visualization website
  - `view_p3if_website.py`: Helper script to open the website in a browser
- Documentation (located in `docs/visualization/`):
  - `technical_documentation.md`: Comprehensive technical documentation
  - `user_guide.md`: Step-by-step user guide
- Output directory (`output/`):
  - `p3if_full_website.html`: The main visualization website
  - `README.md`: Information about the output directory

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### Generating the Website

1. Update domain files with relationship data:
   ```bash
   python3 p3if/scripts/update_domain_files.py
   ```

2. Generate the website:
   ```bash
   python3 p3if/scripts/test_3d_cube_with_domains.py
   ```

3. View the website:
   ```bash
   python3 p3if/scripts/view_p3if_website.py
   ```
   Or manually open `output/p3if_full_website.html` in your browser.

## Using the Visualization

1. **Navigate**: Click and drag to rotate, scroll to zoom, Shift+drag to pan
2. **Select Domains**: Use the dropdown at the top to switch between domains
3. **Explore**: Look for clusters and patterns in the relationships
4. **Interpret**: Larger, brighter points indicate stronger relationships

For detailed instructions, refer to the `user_guide.md` in this directory.

## Available Domains

The visualization includes data from 16 domains:

- Artificial Intelligence
- Healthcare
- Blockchain
- William Blake Poetry and Life
- Climate Change
- Immigration
- Government Accessibility
- National Security
- Math Education
- Power Grid
- Science Research
- Video Chat
- Quantum Computing
- ATM Withdrawal
- Active Inference Grant Proposal
- Pipette Use in Wet Lab

## Technical Details

The visualization is implemented using:

- **Three.js**: JavaScript library for 3D graphics
- **P3IF Framework**: Core data structure for the pattern relationships
- **Web Technologies**: HTML, CSS, and JavaScript

For more technical information, see the detailed documentation in `technical_documentation.md` in this directory.

## Future Enhancements

Planned future enhancements include:

- Filtering capabilities for relationships
- Additional visualization types
- Search functionality
- Comparison views for multiple domains
- Data export features

## Troubleshooting

If you encounter issues:

1. Ensure all Python dependencies are installed
2. Check that JavaScript is enabled in your browser
3. Try a different browser if visualization performance is slow
4. Consult the user guide for common issues and solutions

## Documentation

- `technical_documentation.md`: Comprehensive technical documentation (in this directory)
- `user_guide.md`: Step-by-step user guide (in this directory)
- `output/README.md`: Information about the output directory

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
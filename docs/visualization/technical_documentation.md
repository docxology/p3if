# P3IF Interactive Visualization Website Documentation

## Overview

The P3IF (Properties, Processes, and Perspectives Inter-Framework) interactive visualization website provides an intuitive 3D visualization of the P3IF framework data across multiple domains. The website features a 3D cube visualization that represents the three dimensions of the P3IF framework (properties, processes, and perspectives) and allows users to select different datasets/domains through a dropdown menu.

## Features

### 1. 3D Cube Visualization

The core of the website is a 3D interactive cube visualization that represents:
- Properties (X-axis)
- Processes (Y-axis)
- Perspectives (Z-axis)

Each point within the cube represents a relationship between a property, process, and perspective. The size and color of the points indicate the strength and confidence of the relationships.

### 2. Domain Selection

Users can select different domains from the dropdown menu at the top of the visualization. The available domains include:

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

When a domain is selected, the visualization updates to display the relationships specific to that domain.

### 3. Interactive Controls

The 3D cube can be manipulated using:
- Rotation: Click and drag to rotate the cube
- Zoom: Use the scroll wheel to zoom in and out
- Pan: Hold shift while clicking and dragging to pan the view

### 4. Information Panel

An information panel displays details about the visualization, including a legend explaining what the colors and sizes represent.

## Technical Implementation

### Data Structure

Each domain dataset is stored in a JSON file with the following structure:

```json
{
  "domain": "DomainName",
  "version": "1.0",
  "properties": ["Property1", "Property2", ...],
  "processes": ["Process1", "Process2", ...],
  "perspectives": ["Perspective1", "Perspective2", ...],
  "patterns": {
    "properties": [
      {"id": "uuid", "name": "Property1", "type": "property", "domain": "DomainName"},
      ...
    ],
    "processes": [
      {"id": "uuid", "name": "Process1", "type": "process", "domain": "DomainName"},
      ...
    ],
    "perspectives": [
      {"id": "uuid", "name": "Perspective1", "type": "perspective", "domain": "DomainName"},
      ...
    ]
  },
  "relationships": [
    {
      "id": "uuid",
      "property_id": "property_uuid",
      "process_id": "process_uuid",
      "perspective_id": "perspective_uuid",
      "strength": 0.85,
      "confidence": 0.92
    },
    ...
  ],
  "metadata": {...}
}
```

### Visualization Technology

The 3D cube visualization is implemented using Three.js, a JavaScript library for creating 3D graphics in the web browser. The data is loaded into the visualization using the following process:

1. The domain data is loaded into a P3IFFramework object
2. The InteractiveVisualizer class processes the framework data into a format suitable for visualization
3. The visualization is generated as an HTML file with embedded JavaScript for the Three.js visualization

### Website Components

The website consists of the following components:

1. **HTML Structure**: Defines the layout of the visualization and user interface elements
2. **CSS Styling**: Provides responsive design and visual styling
3. **JavaScript**: Handles the interactive functionality of the visualization
4. **Three.js**: Renders the 3D cube visualization
5. **Dataset Selector**: Allows users to switch between different domain datasets

## How to Generate the Website

The website can be generated using the provided Python script:

```bash
python3 test_3d_cube_with_domains.py
```

This script:
1. Loads domain data from the JSON files in the `p3if/data/domains` directory
2. Creates a P3IFFramework object for each domain
3. Generates the interactive visualization using the InteractiveVisualizer class
4. Outputs the full website to the `output` directory as `p3if_full_website.html`

### Generating a Single Domain Visualization

To generate a visualization for a specific domain:

```bash
python3 test_3d_cube_with_domains.py domain_id
```

Replace `domain_id` with the ID of the domain you want to visualize (e.g., `artificialintelligence`).

## Viewing the Website

The generated website can be viewed by opening the HTML file in a web browser:

```bash
open output/p3if_full_website.html
```

## Future Enhancements

Potential future enhancements for the website include:

1. **Filtering Capabilities**: Allow users to filter relationships based on strength, confidence, or specific patterns
2. **Additional Visualizations**: Add alternative visualization options such as force-directed graphs or heatmaps
3. **Search Functionality**: Enable users to search for specific patterns across domains
4. **Comparison View**: Allow users to compare multiple domains side by side
5. **Data Export**: Add functionality to export visualization data in various formats

## Troubleshooting

### Common Issues

1. **Visualization not loading**: Ensure that JavaScript is enabled in your browser
2. **Domain selector not working**: Check the browser console for any JavaScript errors
3. **Slow performance**: Reduce the number of points displayed by filtering out low-strength relationships

### Browser Compatibility

The visualization has been tested and works on the following browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Conclusion

The P3IF interactive visualization website provides a powerful tool for exploring the relationships between properties, processes, and perspectives across different domains. The 3D cube visualization and domain selection capabilities make it easy for users to gain insights into the P3IF framework data. 
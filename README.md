# Model Performance Comparison Tool

## Overview

This Python tool creates an HTML report that visualizes model performance for document review tasks, showing which models provide the best balance of review efficiency and important item detection.

## Repository Structure

- `three_graphs.py` - Main Python script that generates performance visualizations
- `model_performance.html` - The HTML output file with visualizations
- `javascript_graphs/` - Reference React code for graph styling (not runnable)
- `archive/` - Contains previous Python implementation

## Usage

```bash
python three_graphs.py
```

This will:
1. Generate three visualization types
2. Create an model_performance.html file

## Customization

To visualize your own model performance, modify the model data in the `three_graphs.py` script.

## Requirements

- Python 3.6+
- Web browser to view the HTML output
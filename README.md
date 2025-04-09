# Model Performance Comparison Tool

## Overview

This Python tool creates an HTML report that visualizes model performance for document review tasks, showing which models provide the best balance of review efficiency and important item detection.

## Repository Structure

- `model_visualizer.py` - Main Python script that generates performance visualizations
- `template.html` - Jinja2 HTML template for the visualization
- `test.json` - Configuration file with model performance data
- `model_performance.html` - The generated HTML output file with visualizations
- `javascript_graphs/` - Reference React code for graph styling (not runnable)
- `three_graphs.py` - Original Python script (maintained for reference)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python model_visualizer.py --config model_config.json --template template.html --output model_performance.html
```

### Command Line Arguments

- `--config`: Path to JSON configuration file (default: model_config.json)
- `--template`: Path to HTML template file (default: template.html)
- `--output`: Output HTML file path (default: model_performance.html)

### Example Configuration (model_config.json)

```json
{
  "high_priority_total": 15,
  "recommended_model": "Model A",
  "models": [
    {
      "name": "Model A",
      "coverage": 82,
      "flagged": 12.5
    },
    {
      "name": "Model B",
      "coverage": 69,
      "flagged": 16.2
    },
    {
      "name": "Model C",
      "coverage": 54,
      "flagged": 32.5
    }
  ]
}
```

## Data Definitions

- **Coverage**: Percentage of important items the model can find
- **Flagged**: Percentage of documents the model flags for review
- **Review Savings**: Percentage of documents that can be skipped (calculated as 100 - flagged)
- **High Priority Total**: Total number of important items in the dataset

## Requirements

- Python 3.6+
- Jinja2 package
- Web browser to view the HTML output
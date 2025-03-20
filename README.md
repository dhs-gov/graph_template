# Model Performance Comparison Tool

## Overview

This Python tool creates an HTML report that compares different model performances for classifying "High Priority" items. The report displays side-by-side bar charts showing each model's prediction rate and detection rate (recall) compared to a baseline.

## Features

- **Performance Comparison**: Shows multiple models with color-coded horizontal bar charts
- **Two Key Metrics**: 
  - **Prediction Rate**: The percentage of all samples each model classified as "High Priority"
  - **Detection Rate**: The percentage of actual "High Priority" items each model correctly identified
- **Baseline Comparison**: Metrics displayed against random guessing (the baseline frequency of the category)
- **Color Coding**: Green, yellow, and red indicators for performance levels
- **HTML Output**: Self-contained HTML file viewable in any browser

## How It Works

The tool:
1. Generates performance metrics for model variations
2. Creates an HTML report with bar charts 
3. Outputs an HTML file viewable in web browsers

## Performance Metrics

- **Prediction Rate**: Lower is better - below baseline means the model is more selective
- **Detection Rate**: Higher is better - above baseline means the model finds more relevant items
- **Best Model**: Has low prediction rate and high detection rate

## Usage

```bash
python main.py
```

Optional arguments:
- `--output PATH`: Specify custom output path (default: `category_performance.html`)

## Example Output

The example data shows three model variations:
- **Model A**: Most selective (predicts fewer items as High Priority) with highest detection rate
- **Model B**: Less selective but with good detection capabilities
- **Model C**: Over-predicts High Priority items yet has the lowest detection rate

## Requirements

- Python 3.6+
- No external libraries required

## Customization

To visualize your own model performance:
1. Modify the `generate_dummy_data()` function to include your actual model metrics
2. Adjust category names, baselines, and model names as needed
3. Run the script to generate your custom visualization
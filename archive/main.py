import argparse
import json
from pathlib import Path

def generate_dummy_data():
    """Generate dummy metrics data for demonstration purposes."""
    variations = ["model_A_prompt1_temp0.1", "model_B_prompt1_temp0.3", "model_C_prompt2_temp0.5"]
    categories = ["High Priority"]
    
    metrics_data = {}
    
    # For each variation, create more realistic metrics
    category = "High Priority"
    baseline = 15.0  # 15% of samples are high priority
    sample_count = 200  # total sample count
    
    # Model A: Good model - lower prediction rate (selective) but high recall
    metrics_data["model_A_prompt1_temp0.1"] = {
        category: {
            "baseline": baseline,
            "prediction_rate": 12.5,  # Predicts fewer samples as high priority (selective)
            "prediction_diff": -2.5,  # Below baseline (good)
            "recall": 82.0,  # But finds most of the actual high priority items
            "recall_diff": 67.0,  # Well above baseline
            "sample_count": sample_count
        }
    }
    
    # Model B: Average model - prediction rate close to baseline, decent recall
    metrics_data["model_B_prompt1_temp0.3"] = {
        category: {
            "baseline": baseline,
            "prediction_rate": 16.2,  # Slightly above baseline
            "prediction_diff": 1.2,
            "recall": 68.5,  # Good but not great recall
            "recall_diff": 53.5,
            "sample_count": sample_count
        }
    }
    
    # Model C: Poor model - high prediction rate (not selective) and low recall
    metrics_data["model_C_prompt2_temp0.5"] = {
        category: {
            "baseline": baseline,
            "prediction_rate": 32.5,  # Predicts many samples as high priority (not selective)
            "prediction_diff": 17.5,  # Well above baseline (bad)
            "recall": 54.0,  # Lower recall despite being less selective
            "recall_diff": 39.0,
            "sample_count": sample_count
        }
    }
    
    return metrics_data, categories

def create_category_performance_html(metrics_data, categories):
    """
    Generate HTML for the High Priority category performance comparison.
    """
    # We're only using the High Priority category
    category = categories[0]
    
    # Start building the HTML
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Model Performance Comparison</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2, h3, h4 {
                color: #2c3e50;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <h1>Model Performance Comparison</h1>
    """
    
    # Category Performance Section
    html += """
    <div class="section">
        <h2>High Priority Category Performance vs. Random Guessing</h2>
        <div id="categoryChartsContainer">
    """
    
    # Create chart for High Priority category
    html += f'<div id="chart_{category}">\n'
    
    # Create two-column layout
    html += '<div style="display: flex; justify-content: space-between;">\n'
    
    # Left column - Prediction Rate
    html += '<div style="width: 48%;">\n'
    html += f'<h3 style="font-size: 24px; margin-bottom: 15px;">Prediction Rate</h3>\n'
    html += f'<p style="margin-bottom: 20px; color: #666;">What percentage of all samples did the model label as {category}?</p>\n'
    
    # Get data for this category
    variations = []
    prediction_rates = []
    prediction_diffs = []
    baseline = 0
    
    # Collect data for all variations that have this category
    for variation_name, var_data in metrics_data.items():
        if category in var_data:
            variations.append(variation_name)
            prediction_rates.append(var_data[category]["prediction_rate"])
            prediction_diffs.append(var_data[category]["prediction_diff"])
            baseline = var_data[category]["baseline"]  # Should be the same across variations
    
    # Add the baseline bar
    html += '<div style="margin-bottom: 20px;">\n'
    html += '<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">\n'
    html += '<span style="font-weight: bold;">Baseline (Majority Class)</span>\n'
    html += f'<span>{baseline}%</span>\n'
    html += '</div>\n'
    html += '<div style="width: 100%; background-color: #f0f0f0; height: 20px; border-radius: 10px;">\n'
    bar_width = max(2, min(100, baseline))  # Ensure visible but not over 100%
    html += f'<div style="width: {bar_width}%; background-color: #FFD700; height: 100%; border-radius: 10px;"></div>\n'
    html += '</div>\n'
    html += '</div>\n'
    
    # Add bars for each variation
    for i, variation in enumerate(variations):
        rate = prediction_rates[i]
        diff = prediction_diffs[i]
        
        # For prediction rate, REVERSED color scheme
        if abs(diff) < 5:  # Close to baseline is yellow
            bar_color = "#FFD700"
            diff_color = "#808080"  # neutral gray for small differences
        elif diff < 0:  # Below baseline is green (good - more selective)
            bar_color = "#4CAF50"
            diff_color = "#4CAF50"
        else:  # Above baseline is red (bad - less selective)
            bar_color = "#FF5252" if diff > 20 else "#FFA07A"
            diff_color = "#FF5252"
        
        html += '<div style="margin-bottom: 20px;">\n'
        html += '<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">\n'
        html += f'<span style="font-weight: bold;">{variation}</span>\n'
        html += f'<span>{rate}% <span style="color: {diff_color};">({diff:+}%)</span></span>\n'
        html += '</div>\n'
        html += '<div style="width: 100%; background-color: #f0f0f0; height: 20px; border-radius: 10px;">\n'
        bar_width = max(2, min(100, rate))  # Ensure visible but not over 100%
        html += f'<div style="width: {bar_width}%; background-color: {bar_color}; height: 100%; border-radius: 10px;"></div>\n'
        html += '</div>\n'
        html += '</div>\n'
    
    html += '</div>\n'  # End left column
    
    # Right column - Detection Rate (Recall)
    html += '<div style="width: 48%;">\n'
    html += f'<h3 style="font-size: 24px; margin-bottom: 15px;">Detection Rate</h3>\n'
    html += f'<p style="margin-bottom: 20px; color: #666;">What percentage of actual {category} cases did the model find?</p>\n'
    
    # Reset arrays for recall data
    recall_values = []
    recall_diffs = []
    
    # Collect data for all variations
    for variation_name, var_data in metrics_data.items():
        if category in var_data:
            recall_values.append(var_data[category]["recall"])
            recall_diffs.append(var_data[category]["recall_diff"])
    
    # Add the baseline bar
    html += '<div style="margin-bottom: 20px;">\n'
    html += '<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">\n'
    html += '<span style="font-weight: bold;">Baseline (Majority Class)</span>\n'
    html += f'<span>{baseline}%</span>\n'
    html += '</div>\n'
    html += '<div style="width: 100%; background-color: #f0f0f0; height: 20px; border-radius: 10px;">\n'
    bar_width = max(2, min(100, baseline))  # Ensure visible but not over 100%
    html += f'<div style="width: {bar_width}%; background-color: #FFD700; height: 100%; border-radius: 10px;"></div>\n'
    html += '</div>\n'
    html += '</div>\n'
    
    # Add bars for each variation
    for i, variation in enumerate(variations):
        recall = recall_values[i]
        diff = recall_diffs[i]
        
        # For recall, normal color scheme: higher is better
        bar_color = "#4CAF50" if recall >= 75 else "#FFD700" if recall >= 60 else "#FF5252"
        diff_color = "#4CAF50" if diff > 0 else "#FF5252"
        
        html += '<div style="margin-bottom: 20px;">\n'
        html += '<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">\n'
        html += f'<span style="font-weight: bold;">{variation}</span>\n'
        html += f'<span>{recall}% <span style="color: {diff_color};">({diff:+}%)</span></span>\n'
        html += '</div>\n'
        html += '<div style="width: 100%; background-color: #f0f0f0; height: 20px; border-radius: 10px;">\n'
        bar_width = max(2, min(100, recall))  # Ensure visible but not over 100%
        html += f'<div style="width: {bar_width}%; background-color: {bar_color}; height: 100%; border-radius: 10px;"></div>\n'
        html += '</div>\n'
        html += '</div>\n'
    
    html += '</div>\n'  # End right column
    
    html += '</div>\n'  # End two-column layout
    
    # Add sample count info
    sample_count = None
    for variation_name, var_data in metrics_data.items():
        if category in var_data:
            sample_count = var_data[category]["sample_count"]
            break
            
    if sample_count is not None:
        html += f'<div style="font-size: 14px; color: #666; margin-top: 20px;">Based on {sample_count} samples ({baseline:.1f}% of dataset)</div>\n'
    
    html += '</div>\n'  # End chart div
    
    html += """
        </div>
        
        <div style="margin-top: 20px; font-size: 14px;">
            <p><strong>Note:</strong> Baseline is random guessing, which for High Priority would have prediction rate and detection rate equal to its frequency in the dataset (15%). Lower prediction rates with higher detection rates indicate better selectivity.</p>
            <p><strong>Interpretation:</strong></p>
            <ul>
                <li><strong>Model A</strong> is the most selective (predicts fewer items as High Priority) while maintaining the highest detection rate.</li>
                <li><strong>Model B</strong> is less selective but still has good detection.</li>
                <li><strong>Model C</strong> over-predicts High Priority items (less selective) yet still has the lowest detection rate.</li>
            </ul>
        </div>
    </div>
    </body>
    </html>
    """
    
    return html

def main():
    parser = argparse.ArgumentParser(description="Generate Category Performance Graph")
    parser.add_argument("--output", type=str, default="category_performance.html",
                        help="Path to save the output HTML file")
    args = parser.parse_args()
    
    # Generate dummy data
    metrics_data, categories = generate_dummy_data()
    
    # Create the HTML chart
    html = create_category_performance_html(metrics_data, categories)
    
    # Save to file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Category performance chart generated at: {output_path}")

if __name__ == "__main__":
    main()
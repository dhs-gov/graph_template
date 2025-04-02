import json
import argparse
import os
from jinja2 import Environment, FileSystemLoader

# === Global formatting control ===
PERCENT_PRECISION = 0  # Change to 1 for decimals like 87.5%

def format_percent(value, precision=PERCENT_PRECISION):
    return f"{round(value, precision):.{precision}f}%"

def process_model_data(data):
    """
    Process model data from the JSON file and compute derived metrics.
    """
    processed_data = []
    
    for model in data["models"]:
        # Calculate review savings from flagged percentage
        review_savings = 100 - model["flagged"]
        
        processed_data.append({
            "name": model["name"],
            "review_savings": round(review_savings, PERCENT_PRECISION),
            "coverage": round(model["coverage"], PERCENT_PRECISION),
            "flagged": round(model["flagged"], PERCENT_PRECISION),
        })
    
    return processed_data

def render_template(chart_data, config_data, template_path, output_file):
    """
    Render the HTML template using Jinja2
    """
    # Set up Jinja2 environment
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Add custom filter for percentage formatting
    env.filters['format_percent'] = format_percent
    
    # Load the template
    template = env.get_template(template_file)
    
    # Find the recommended model from config
    recommended_model_name = config_data["recommended_model"]
    recommended_model = next((model for model in chart_data if model["name"] == recommended_model_name), chart_data[0])
    
    # Calculate summary values
    most_savings = max(chart_data, key=lambda x: x['review_savings'])
    most_coverage = max(chart_data, key=lambda x: x['coverage'])
    
    # Recommendation visual representation data
    total_documents = 100
    high_priority_count = config_data["high_priority_total"]
    found_count = round((recommended_model['coverage'] / 100) * high_priority_count)
    flagged_count = round(recommended_model['flagged'])
    review_count = flagged_count  # Number of documents to review
    
    # JavaScript for tooltips
    tooltips = {
        'savings': """
        function(model) { 
            return "Can skip " + model.review_savings.toFixed(1) + "% of documents"; 
        }
        """,
        'coverage': """
        function(model) { 
            return "Finds " + model.coverage + "% of important items"; 
        }
        """,
        'scatter': """
        function(context) {
            const point = context.raw;
            const model = context.dataset.label;
            return model + ": Finds " + point.y + "%, Skips " + point.x.toFixed(1) + "%";
        }
        """
    }
    
    # Prepare context for the template
    context = {
        'chart_data': chart_data,
        'json_chart_data': json.dumps(chart_data),
        'recommended_model': recommended_model,
        'most_savings': most_savings,
        'most_coverage': most_coverage,
        'high_priority_count': high_priority_count,
        'found_count': found_count,
        'flagged_count': flagged_count,
        'review_count': review_count,
        'tooltips': tooltips
    }
    
    # Render the template
    html_content = template.render(**context)
    
    # Write the HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML chart created: {output_file}")
    
    # Return the file path
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate model performance chart as HTML')
    parser.add_argument('--config', default='model_config.json',
                      help='Path to JSON configuration file')
    parser.add_argument('--template', default='template.html',
                      help='Path to HTML template file')
    parser.add_argument('--output', default='model_performance.html',
                      help='Output HTML file path')
    
    args = parser.parse_args()
    
    # Load data from JSON file
    print(f"Loading configuration from {args.config}...")
    try:
        with open(args.config, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Configuration file '{args.config}' contains invalid JSON.")
        return
    
    # Check if template exists
    if not os.path.exists(args.template):
        print(f"Error: Template file '{args.template}' not found.")
        return
    
    # Process the data
    print("Processing model performance data...")
    chart_data = process_model_data(config_data)
    
    # Render template
    render_template(chart_data, config_data, args.template, args.output)
    
    print(f"Open {args.output} in your web browser to view the charts")
    print("Done!")

if __name__ == "__main__":
    main()
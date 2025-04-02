import json
import argparse
import os

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

def create_simple_html(chart_data, config_data, output_file):
    """
    Create a simple HTML file with charts using Chart.js
    """
    # Find the recommended model from config
    recommended_model_name = config_data["recommended_model"]
    recommended_model = next((model for model in chart_data if model["name"] == recommended_model_name), chart_data[0])
    
    # Calculate summary values
    most_savings = max(chart_data, key=lambda x: x['review_savings'])
    most_coverage = max(chart_data, key=lambda x: x['coverage'])
    
    # Format the data for Chart.js
    labels = [item['name'] for item in chart_data]
    review_savings_data = [item['review_savings'] for item in chart_data]
    coverage_data = [item['coverage'] for item in chart_data]
    flagged_data = [item['flagged'] for item in chart_data]
    
    # Recommendation visual representation data
    total_documents = 100
    high_priority_count = config_data["high_priority_total"]  # From JSON config
    found_count = round((recommended_model['coverage'] / 100) * high_priority_count)
    flagged_count = round(recommended_model['flagged'])
    review_count = flagged_count  # Number of documents to review
    
    # JavaScript for tooltips (defined separately to avoid Python syntax issues)
    savings_tooltip = """
    function(model) { 
        return "Can skip " + model.review_savings.toFixed(1) + "% of documents"; 
    }
    """
    
    coverage_tooltip = """
    function(model) { 
        return "Finds " + model.coverage + "% of important items"; 
    }
    """
    
    scatter_tooltip = """
    function(context) {
        const point = context.raw;
        const model = context.dataset.label;
                        return model + ": Finds " + point.y + "%, Skips " + point.x.toFixed(1) + "%";
    }
    """
    
    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Performance Comparison</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.1.0/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .main-title {{
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 24px;
        }}
        .chart-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
            margin-bottom: 40px;
        }}
        .first-container {{
            padding-bottom: 80px; /* Increased padding for the first container */
        }}
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        .charts-wrapper {{
            display: flex;
            gap: 24px;
            margin-bottom: 40px;
        }}
        .chart-box {{
            flex: 1;
            height: 300px;
        }}
        .chart-header {{
            font-size: 20px; /* Increased size to match main titles */
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .chart-description {{
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }}
        .chart-note {{
            font-size: 13px;
            color: #444;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid #eee;
            text-align: center;
        }}
        .scatter-box {{
            height: 400px;
            margin-top: 30px;
        }}
        .description-text {{
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }}
        .description-text p {{
            margin-bottom: 8px;
        }}
        strong {{
            font-weight: 600;
        }}
        
        /* Recommendation Component Styles */
        .recommendation-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }}
        .recommendation-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: rgba(100, 149, 237, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
        }}
        .recommendation-title {{
            font-size: 20px;
            font-weight: 700;
        }}
        .alert-box {{
            background-color: rgba(100, 149, 237, 0.1);
            border-left: 4px solid #6495ED;
            padding: 12px;
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 20px;
        }}
        .metric-section-title {{
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 12px;
        }}
        .progress-container {{
            margin-bottom: 16px;
        }}
        .progress-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            font-size: 14px;
        }}
        .progress-bar {{
            width: 100%;
            height: 12px;
            background-color: #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 6px;
        }}
        .progress-fill-model {{
            background-color: #6495ED; /* Will be replaced dynamically */
        }}
        .progress-caption {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        .document-grid {{
            display: grid;
            grid-template-columns: repeat(20, 1fr);
            gap: 2px;
            margin-bottom: 12px;
            width: fit-content;

        }}
        .document-box {{
            width: 10px;
            height: 10px;
            border-radius: 2px;
        }}
        .document-legend {{
            display: flex;
            font-size: 12px;
            color: #666;
            margin-top: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-right: 12px;
        }}
        .legend-color {{
            width: 10px;
            height: 10px;
            margin-right: 4px;
        }}
        .summary-footer {{
            font-size: 14px;
            color: #444;
            border-top: 1px solid #eee;
            padding-top: 12px;
            margin-top: 12px;
        }}
    </style>
</head>
<body>
    <!-- Main title outside containers -->
    <h1 class="main-title">Model Performance</h1>
    
    <!-- Recommendation Component (MOVED TO TOP) -->
    <div class="chart-container">
        <div class="recommendation-header">
            <div class="recommendation-icon" id="model-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="#6495ED">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
            </div>
            <h2 class="recommendation-title">Recommended: {recommended_model['name']}</h2>
        </div>
        
        <div class="alert-box" id="model-alert">
            <p style="font-size: 14px;">
                <strong>Bottom line:</strong> Find {found_count} out of {high_priority_count} important items
                while only needing to review {review_count} documents instead of 100.
            </p>
        </div>
        
        <div class="metrics-grid">
            <!-- Key metrics -->
            <div>
                <h3 class="metric-section-title">Key Metrics</h3>
                
                <!-- Coverage (Moved to top) -->
                <div class="progress-container">
                    <div class="progress-header">
                        <span>Coverage</span>
                        <span><strong>{format_percent(recommended_model['coverage'])}</strong></span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill progress-fill-model" id="coverage-bar" style="width: {recommended_model['coverage']}%"></div>
                    </div>
                    <p class="progress-caption">Higher is better - finds more important content</p>
                </div>
                
                <!-- Review Savings -->
                <div class="progress-container">
                    <div class="progress-header">
                        <span>Review Savings</span>
                        <span><strong>{format_percent(recommended_model['review_savings'])}</strong></span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill progress-fill-model" id="savings-bar" style="width: {recommended_model['review_savings']}%"></div>
                    </div>
                    <p class="progress-caption">Higher is better - less content to review</p>
                </div>
            </div>
            
            <!-- Visual representation -->
            <div>
                <h3 class="metric-section-title">Document Analysis Visualization</h3>
                
                <div class="document-grid" id="document-grid"></div>
                
                <div class="document-legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #4CAF50;"></div>
                        <span>Found ({found_count})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #FF7F7F;"></div>
                        <span>Missed ({high_priority_count - found_count})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #A9A9A9;"></div>
                        <span>False positives ({flagged_count - found_count})</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Summary metrics - No footer summary since we moved it to the top alert box -->

    </div>
    
    <!-- First chart container (Bar charts) -->
    <div class="chart-container first-container">
        <div class="charts-wrapper">
            <div class="chart-box">
                <h3 class="chart-header">Coverage</h3>
                <p class="chart-description">% of important items found</p>
                <canvas id="coverageChart"></canvas>
                <p class="chart-note">
                    <strong>{most_coverage['name']}</strong> finds {format_percent(most_coverage['coverage'])} of important items.
                </p>
            </div>
            <div class="chart-box">
                <h3 class="chart-header">Review Savings</h3>
                <p class="chart-description">% of documents that can be skipped</p>
                <canvas id="savingsChart"></canvas>
                <p class="chart-note">
                    <strong>{most_savings['name']}</strong> allows skipping {format_percent(most_savings['review_savings'])} of documents.
                </p>
            </div>
        </div>
    </div>
    
    <!-- Second chart container (Scatter chart) -->
    <div class="chart-container">
        <h2 class="chart-title">Coverage vs. Review Savings</h2>
        <div class="scatter-box">
            <canvas id="scatterChart"></canvas>
        </div>
        <div class="description-text">
            <p><strong>Better models</strong> appear higher and to the right: they find more important items while requiring less review.</p>
            <p><strong>For example:</strong> {recommended_model['name']} finds {format_percent(recommended_model['coverage'])} of important items while allowing you to skip {format_percent(recommended_model['review_savings'])} of content.</p>
        </div>
    </div>

    <script>
        // Class for creating consistent charts
        class ModelPerformanceChart {{
            constructor(options = {{}}) {{
                // Define color palette for up to 6+ models
                this.colors = {{
                    // Main palette - distinguishable neutral colors
                    palette: [
                        'rgba(100, 149, 237, 0.7)',  // Cornflower Blue
                        'rgba(106, 90, 205, 0.7)',   // Slate Blue
                        'rgba(72, 209, 204, 0.7)',   // Medium Turquoise
                        'rgba(147, 112, 219, 0.7)',  // Medium Purple
                        'rgba(65, 105, 225, 0.7)',   // Royal Blue
                        'rgba(0, 128, 128, 0.7)',    // Teal
                        'rgba(123, 104, 238, 0.7)',  // Medium Slate Blue
                        'rgba(30, 144, 255, 0.7)'    // Dodger Blue
                    ],
                    // Border colors (darker versions of the palette)
                    border: [
                        'rgba(100, 149, 237, 1)',
                        'rgba(106, 90, 205, 1)',
                        'rgba(72, 209, 204, 1)',
                        'rgba(147, 112, 219, 1)',
                        'rgba(65, 105, 225, 1)',
                        'rgba(0, 128, 128, 1)',
                        'rgba(123, 104, 238, 1)',
                        'rgba(30, 144, 255, 1)'
                    ],
                    // Fixed colors for the document visualization
                    documentGrid: {{
                        found: '#4CAF50',       // Green
                        missed: '#FF7F7F',      // Soft Red
                        falsePositive: '#A9A9A9', // Dark Gray
                        normal: '#e0e0e0'       // Light Gray
                    }}
                }};
                
                this.fontFamily = options.fontFamily || 
                    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif';
                
                // Set the recommended model's color in the UI
                this.setRecommendedModelColor();
            }}
            
            // Set the recommended model's color in the UI
            setRecommendedModelColor() {{
                // Get the recommended model's index
                const recommendedModelName = '{recommended_model['name']}';
                const modelIndex = chartData.findIndex(model => model.name === recommendedModelName);
                const modelColor = this.colors.palette[modelIndex >= 0 ? modelIndex : 0];
                const modelBorderColor = this.colors.border[modelIndex >= 0 ? modelIndex : 0];
                
                // Update icon background and SVG fill
                const iconElem = document.getElementById('model-icon');
                if (iconElem) {{
                    iconElem.style.backgroundColor = modelColor.replace('0.7', '0.2');
                    const svgElem = iconElem.querySelector('svg');
                    if (svgElem) svgElem.setAttribute('fill', modelBorderColor);
                }}
                
                // Update alert box
                const alertElem = document.getElementById('model-alert');
                if (alertElem) {{
                    alertElem.style.backgroundColor = modelColor.replace('0.7', '0.1');
                    alertElem.style.borderLeftColor = modelBorderColor;
                }}
                
                // Update progress bars
                const savingsBar = document.getElementById('savings-bar');
                const coverageBar = document.getElementById('coverage-bar');
                if (savingsBar) savingsBar.style.backgroundColor = modelBorderColor;
                if (coverageBar) coverageBar.style.backgroundColor = modelBorderColor;
            }}
            
            // Create a bar chart for review savings or coverage
            createBarChart(ctx, chartData, options = {{}}) {{
                const labels = chartData.map(item => item.name);
                const data = chartData.map(item => item[options.dataKey]);
                
                // Set colors based on palette
                const backgroundColor = chartData.map((item, index) => 
                    this.colors.palette[index % this.colors.palette.length]
                );
                
                const borderColor = chartData.map((item, index) => 
                    this.colors.border[index % this.colors.border.length]
                );
                
                return new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: options.label || 'Data',
                            data: data,
                            backgroundColor: backgroundColor,
                            borderColor: borderColor,
                            borderWidth: 1,
                            borderRadius: 4,
                            barPercentage: 0.7
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }}
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        let label = context.dataset.label || '';
                                        if (label) {{
                                            label += ': ';
                                        }}
                                        label += context.parsed.y + '%';
                                        return label;
                                    }},
                                    afterLabel: function(context) {{
                                        return options.tooltipAfterLabel(chartData[context.dataIndex]);
                                    }}
                                }}
                            }}
                        }},
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
            
            // Create a scatter chart for model performance
            createScatterChart(ctx, chartData) {{
                // Create datasets with colors from palette
                const datasets = chartData.map((item, index) => {{
                    const color = this.colors.palette[index % this.colors.palette.length];
                    const borderColor = this.colors.border[index % this.colors.border.length];
                    
                    return {{
                        label: item.name,
                        data: [{{
                            x: item.review_savings,
                            y: item.coverage
                        }}],
                        backgroundColor: color,
                        borderColor: borderColor,
                        borderWidth: 1,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    }};
                }});
                
                return new Chart(ctx, {{
                    type: 'scatter',
                    data: {{
                        datasets: datasets
                    }},
                    options: {{
                        scales: {{
                            x: {{
                                type: 'linear',
                                position: 'bottom',
                                min: 50,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: 'Review Savings (%)',
                                    font: {{
                                        size: 14
                                    }}
                                }}
                            }},
                            y: {{
                                min: 0,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: 'Coverage (%)',
                                    font: {{
                                        size: 14
                                    }}
                                }},
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }}
                                }}
                            }}
                        }},
                        plugins: {{
                            tooltip: {{
                                callbacks: {{
                                    label: {scatter_tooltip}
                                }}
                            }}
                            // Removed annotation plugin with diagonal line
                        }},
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            }}
            
            // Create document grid visualization
            createDocumentGrid(containerId, options) {{
                const container = document.getElementById(containerId);
                const totalDocuments = options.totalDocuments || 100;
                const highPriorityCount = options.highPriorityCount || 15;
                const foundCount = options.foundCount || 12;
                const flaggedCount = options.flaggedCount || 20;
                
                // Clear any existing content
                container.innerHTML = '';
                
                // Create document boxes
                for (let i = 0; i < totalDocuments; i++) {{
                    const box = document.createElement('div');
                    box.className = 'document-box';
                    
                    // Color logic: found (green), missed important (soft red), false positives (gray), normal (light gray)
                    if (i < foundCount) {{
                        box.style.backgroundColor = this.colors.documentGrid.found;  // Found
                    }} else if (i < highPriorityCount) {{
                        box.style.backgroundColor = this.colors.documentGrid.missed;  // Missed important
                    }} else if (i < flaggedCount) {{
                        box.style.backgroundColor = this.colors.documentGrid.falsePositive;  // False positives
                    }} else {{
                        box.style.backgroundColor = this.colors.documentGrid.normal;  // Normal
                    }}
                    
                    container.appendChild(box);
                }}
            }}
        }}

        // Initialize data
        const chartData = {json.dumps(chart_data)};
        
        // Initialize the chart class
        const chartManager = new ModelPerformanceChart();
        
        // Create review savings chart
        const savingsCtx = document.getElementById('savingsChart').getContext('2d');
        chartManager.createBarChart(savingsCtx, chartData, {{
            dataKey: 'review_savings',
            label: 'Review Savings',
            tooltipAfterLabel: {savings_tooltip}
        }});
        
        // Create coverage chart
        const coverageCtx = document.getElementById('coverageChart').getContext('2d');
        chartManager.createBarChart(coverageCtx, chartData, {{
            dataKey: 'coverage',
            label: 'Coverage',
            tooltipAfterLabel: {coverage_tooltip}
        }});
        
        // Create scatter chart
        const scatterCtx = document.getElementById('scatterChart').getContext('2d');
        chartManager.createScatterChart(scatterCtx, chartData);
        
        // Create document grid visualization
        chartManager.createDocumentGrid('document-grid', {{
            totalDocuments: 100,
            highPriorityCount: {high_priority_count},
            foundCount: {found_count},
            flaggedCount: {flagged_count}
        }});
        
        // Update the recommendation section colors
        chartManager.setRecommendedModelColor();
    </script>
</body>
</html>
"""
    
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
    
    # Process the data
    print("Processing model performance data...")
    chart_data = process_model_data(config_data)
    
    # Create HTML chart
    create_simple_html(chart_data, config_data, args.output)
    
    print(f"Open {args.output} in your web browser to view the charts")
    print("Done!")

if __name__ == "__main__":
    main()
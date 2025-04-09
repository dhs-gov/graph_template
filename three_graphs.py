import json
import argparse
import os
from jinja2 import Environment, FileSystemLoader
import subprocess
import tempfile
import sys
import time

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
def export_to_png(html_file, output_png=None):
    """
    Export HTML file to PNG using a headless browser with a file-focused approach
    """
    if output_png is None:
        # Use the same filename but with .png extension
        output_png = os.path.splitext(html_file)[0] + '.png'
    
    print(f"Starting PNG export to: {output_png}")
    
    # Record the initial state of the file
    initial_stat = None
    if os.path.exists(output_png):
        initial_stat = {
            'size': os.path.getsize(output_png),
            'mtime': os.path.getmtime(output_png)
        }
        print(f"Existing PNG file detected: {output_png}")
        print(f"  Size: {initial_stat['size']} bytes")
        print(f"  Last modified: {time.ctime(initial_stat['mtime'])}")
    
    try:
        # Check if we have Chrome or Chromium available
        browser_paths = [
            # Linux paths
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            # macOS paths
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            # Windows paths
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        browser_path = None
        for path in browser_paths:
            if os.path.exists(path):
                browser_path = path
                print(f"Using browser: {browser_path}")
                break
        
        if browser_path is None:
            print("Error: Could not find Chrome or Chromium browser.")
            print("Required for PNG export: Chrome or Chromium browser")
            return None
        
        # Create a temporary directory for browser data
        temp_dir = tempfile.mkdtemp()
        
        # Prepare Chrome arguments for headless screenshot
        html_file_absolute = os.path.abspath(html_file)
        html_url = f"file://{html_file_absolute}"
        png_path = os.path.abspath(output_png)
        
        # Command to capture screenshot with optimized settings
        cmd = [
            browser_path,
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={temp_dir}",
            "--disable-dev-shm-usage", 
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=1200,1600",
            f"--screenshot={png_path}",
            html_url
        ]
        
        # Start Chrome as a non-blocking subprocess
        print(f"Launching Chrome (non-blocking)...")
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for file to be created or updated
        start_time = time.time()
        max_wait_time = 10  # Only wait 10 seconds max
        check_interval = 0.5  # Check every 0.5 seconds
        success = False
        
        print(f"Watching for file changes...")
        while time.time() - start_time < max_wait_time:
            # Sleep a bit before checking
            time.sleep(check_interval)
            
            # Check if process completed
            if process.poll() is not None:
                print(f"Chrome process completed with return code: {process.returncode}")
                # Get any output
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"Chrome stderr: {stderr.decode('utf-8')}")
                break
            
            # Check if file exists and has been modified
            if os.path.exists(output_png):
                current_size = os.path.getsize(output_png)
                current_mtime = os.path.getmtime(output_png)
                
                # Check if file was created or updated since we started
                file_is_new = initial_stat is None
                file_was_modified = (initial_stat is not None and 
                                     (current_size != initial_stat['size'] or 
                                      current_mtime > initial_stat['mtime']))
                
                if file_is_new or file_was_modified:
                    elapsed = time.time() - start_time
                    print(f"PNG file detected after {elapsed:.2f} seconds")
                    print(f"  Size: {current_size} bytes")
                    if file_was_modified:
                        print(f"  Size changed: {initial_stat['size']} → {current_size} bytes")
                    success = True
                    break
        
        # Final check on results
        elapsed_time = time.time() - start_time
        if success:
            print(f"PNG export completed successfully in {elapsed_time:.2f} seconds")
            
            # Try to terminate Chrome since we got what we wanted
            if process.poll() is None:
                print("Terminating Chrome process (we have our PNG)")
                process.terminate()
            
            return output_png
        else:
            print(f"No PNG file changes detected after {elapsed_time:.2f} seconds")
            
            # File might still exist from before
            if os.path.exists(output_png) and os.path.getsize(output_png) > 0:
                print(f"Using existing PNG file: {output_png}")
                return output_png
            
            # Kill Chrome if it's still running
            if process.poll() is None:
                print("Terminating Chrome process")
                process.terminate()
            
            print("PNG export failed - no file detected")
            return None
    
    except Exception as e:
        print(f"Error during PNG export: {str(e)}")
        return None
    finally:
        # Clean up temp directory
        if 'temp_dir' in locals():
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description='Generate model performance chart as HTML')
    parser.add_argument('--config', default='model_config.json',
                      help='Path to JSON configuration file')
    parser.add_argument('--template', default='template.html',
                      help='Path to HTML template file')
    parser.add_argument('--output', default='model_performance.html',
                      help='Output HTML file path')
    parser.add_argument('--static', action='store_true',
                      help='Generate a static PNG image in addition to HTML')
    parser.add_argument('--png-output', 
                      help='Output PNG file path (only used with --static)')
    
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
    html_file = render_template(chart_data, config_data, args.template, args.output)
    
    # Handle static PNG export if requested
    if args.static:
        print("\nNote: For PNG export, you need Chrome or Chromium installed.")
        
        png_output = args.png_output if args.png_output else None
        png_file = export_to_png(html_file, png_output)
        
        # Simplified success/failure message - rely on export_to_png for detailed messages
        if png_file:
            print("\nPNG export completed successfully.")
        else:
            print("\nPNG export failed. See error messages above for details.")
    else:
        print(f"Open {args.output} in your web browser to view the charts")
    
    print("Done!")

if __name__ == "__main__":
    main()
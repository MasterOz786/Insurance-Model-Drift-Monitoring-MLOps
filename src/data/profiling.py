"""
Data Profiling Module
Generates data quality and feature summary reports using ydata-profiling
"""

import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_data_profile(data_path: str, output_path: str) -> str:
    """
    Generate a data profiling report using ydata-profiling
    
    Args:
        data_path: Path to the CSV file to profile
        output_path: Path where the HTML report should be saved
    
    Returns:
        str: Path to the generated report
    """
    try:
        # Try to import ydata-profiling
        try:
            from ydata_profiling import ProfileReport
            use_ydata = True
        except ImportError:
            logger.warning("ydata-profiling not available, using basic pandas describe")
            use_ydata = False
        
        # Load data
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if use_ydata:
            # Generate profile report with ydata-profiling
            logger.info("Generating profile report with ydata-profiling...")
            profile = ProfileReport(
                df,
                title="Data Profile Report",
                minimal=False,
                explorative=True
            )
            profile.to_file(output_path)
            logger.info(f"Profile report saved to {output_path}")
        else:
            # Fallback: Generate a simple HTML report
            logger.info("Generating basic profile report...")
            html_content = f"""
            <html>
            <head><title>Data Profile Report</title></head>
            <body>
                <h1>Data Profile Report</h1>
                <h2>Dataset Shape</h2>
                <p>Rows: {len(df)}, Columns: {len(df.columns)}</p>
                <h2>Summary Statistics</h2>
                {df.describe().to_html()}
                <h2>Data Types</h2>
                {df.dtypes.to_frame('Type').to_html()}
                <h2>Missing Values</h2>
                {df.isnull().sum().to_frame('Missing Count').to_html()}
            </body>
            </html>
            """
            with open(output_path, 'w') as f:
                f.write(html_content)
            logger.info(f"Basic profile report saved to {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate data profile: {str(e)}")
        raise


if __name__ == "__main__":
    # For testing
    import sys
    if len(sys.argv) >= 3:
        generate_data_profile(sys.argv[1], sys.argv[2])
    else:
        print("Usage: profiling.py <data_path> <output_path>")

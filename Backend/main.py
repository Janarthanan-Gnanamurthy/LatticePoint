from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy import stats
import os
import re
import google.generativeai as genai
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors
from dotenv import load_dotenv
from agents import analyze_prompt_intent, get_chart_config, get_transformation_code, get_statistical_code

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Spark
spark = SparkSession.builder.appName("DataTransformation").getOrCreate()


class ChartConfig(BaseModel):
    x_axis: str
    y_axis: str
    aggregation: str
    chart_type: str
    title: str


def process_chart_data(data: List[Dict], config: Dict) -> Dict:
    """Process data according to chart configuration, handling large numbers."""
    print(f"Processing chart data with config: {config}")
    df = pd.DataFrame(data)

    # Apply aggregation if specified
    if config['aggregation'] != 'none':
        if config['aggregation'] == 'sum':
            df = df.groupby(config['x_axis'])[config['y_axis']].sum().reset_index()
        elif config['aggregation'] == 'average':
            df = df.groupby(config['x_axis'])[config['y_axis']].mean().reset_index()
        elif config['aggregation'] == 'count':
            df = df.groupby(config['x_axis'])[config['y_axis']].count().reset_index()

    print(f"Aggregated data: {df}")

    # **KEY CHANGE: Convert numeric values to strings before creating the chart config**
    df[config['y_axis']] = df[config['y_axis']].astype(str)  # Convert y-axis to string
    df[config['x_axis']] = df[config['x_axis']].astype(str)  # Convert x-axis to string (if numeric)


    chart_config = {
        'type': config['chart_type'],
        'data': {
            'labels': df[config['x_axis']].tolist(),
            'datasets': [{
                'label': config['y_axis'],
                'data': df[config['y_axis']].tolist(),  # Data is already strings now
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
                ],
                'borderColor': '#36A2EB',
                'fill': 'true'
            }]
        },
        'options': {
            'responsive': 'true',
            'plugins': {
                'title': {
                    'display': 'true',
                    'text': config['title']
                },
                'legend': {
                    'display': 'true'
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': 'true',
                    'title': {
                        'display': 'true',
                        'text': config['y_axis']
                    }
                },
                'x': {
                    'title': {
                        'display': 'true',
                        'text': config['x_axis']
                    }
                }
            }
        }
    }

    print(f"Chart configuration generated: {chart_config}")
    return chart_config


def execute_transformation(code: str, df) -> pd.DataFrame:
    """Execute PySpark transformation code."""
    print(f"Executing transformation code:\n{code}")
    try:
        # Create a restricted global environment
        allowed_globals = {
            'spark': spark,
            'F': F,
            'df': df,
            'datetime': datetime
        }
        
        # Execute the transformation code
        exec(code, allowed_globals)
        transformed_df = allowed_globals.get('transformed_df')
        
        if transformed_df is None:
            raise ValueError("Transformation did not produce a result")
        
        print("Transformation successful, resulting DataFrame:")
        transformed_df.show()
        return transformed_df.toPandas()
    except Exception as e:
        print(f"Error executing transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing transformation: {str(e)}")


@app.post("/process")
async def process_data(files: List[UploadFile] = File(...), prompt: str = Form(...)):
    """
    Process multiple CSV files and a prompt.
    The files are read, cleaned, and then combined (via a unionByName).
    The prompt is analyzed to decide whether to perform visualization,
    statistical analysis, or data transformation on the combined data.
    """
    temp_paths = []
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        df_list = []
        # Process each uploaded file
        for file in files:
            extension = os.path.splitext(file.filename)[-1].lower()
            
            # Create a unique temporary file path
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{file.filename}"
            temp_paths.append(temp_path)
            print(f"Saving file {file.filename} to temporary path: {temp_path}")
            
            # Read the file content and save it
            file_content = await file.read()
            with open(temp_path, "wb+") as f:
                f.write(file_content)
            
            # Load the CSV file into a Spark DataFrame
            if extension == '.csv':
                part_df = spark.read.csv(temp_path, header=True, inferSchema=True)
            elif extension in ['.xlsx', '.xls']:
                pandas_df = pd.read_excel(temp_path)
                part_df = spark.createDataFrame(pandas_df)
            elif extension == '.json':
                part_df = spark.read.json(temp_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            print(f"Loaded DataFrame from {file.filename} with columns: {part_df.columns}")
            
            # Clean column names
            for old_col in part_df.columns:
                new_col = re.sub(r'[^\w\s]', '', old_col).strip().lower().replace(' ', '_')
                part_df = part_df.withColumnRenamed(old_col, new_col)
            print(f"Cleaned columns for {file.filename}: {part_df.columns}")
            df_list.append(part_df)
        
        # Combine all DataFrames using unionByName (allowing missing columns)
        combined_df = df_list[0]
        for part_df in df_list[1:]:
            combined_df = combined_df.unionByName(part_df, allowMissingColumns=True)
        
        print(f"Combined DataFrame columns: {combined_df.columns}")
        
        # Optionally, if you want your agents to know that the data comes from multiple sources,
        # you can modify the prompt or add extra context here. For example:
        if len(files) > 1:
            prompt = f"(Combined multiple CSV files) {prompt}"
        
        # Analyze the prompt intent (visualization, statistical, transformation, etc.)
        intent_analysis = await analyze_prompt_intent(prompt)
        print(f"Intent analysis result: {intent_analysis['intent']}")
        columns = combined_df.columns
        
        # Process according to the intent
        if intent_analysis['intent'] == 'visualization':
            # Generate visualization configuration based on the prompt and columns
            chart_config = await get_chart_config(prompt, columns)
            pandas_df = combined_df.toPandas()
            visualization = process_chart_data(pandas_df.to_dict('records'), chart_config)
            print(f"Visualization configuration generated: {visualization}")
            
            response = {
                "type": "visualization",
                # "data": pandas_df.to_dict('records'),
                "visualization": visualization,
                "config": chart_config
            }

            print(f"Visualization response: {response}")
        elif intent_analysis['intent'] == 'statistical':
            # Generate and execute statistical analysis code
            statistical_code = await get_statistical_code(prompt, columns)
            
            allowed_globals = {
                'spark': spark,
                'F': F,
                'df': combined_df,
                'np': np,
                'stats': stats,
                'VectorAssembler': VectorAssembler,
                'Correlation': Correlation
            }
            
            exec(statistical_code, allowed_globals)
            stat_df = allowed_globals.get('stat_df')
            
            if stat_df is None:
                raise ValueError("Statistical analysis did not produce a result")
            
            result_df = stat_df.toPandas()
            response = {
                "type": "statistical",
                "data": result_df.to_dict('records'),
                "statistical_type": intent_analysis.get('statistical_type', None)
            }
        else:
            # Default to data transformation based on the prompt
            transformation_code = await get_transformation_code(prompt, columns)
            transformed_df = execute_transformation(transformation_code, combined_df)
            response = {
                "type": "transformation",
                "data": transformed_df.to_dict('records'),
                "columns": transformed_df.columns.tolist(),
                "rows": len(transformed_df)
            }
        
        return response
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Remove all temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Temporary file removed: {temp_path}")

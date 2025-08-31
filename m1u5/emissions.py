import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 

### 
# Aviation Emissions Analysis Script
# This script analyzes and visualizes aviation CO₂ emissions data from a CSV file.
# It provides functionality to load, clean, analyze, and visualize emissions data
# over time for different countries.
# The script expects a CSV file with the following columns:
# - Entity (renamed to Country): The name of the country
# - Code: The ISO country code
# - Year: The year of the emission data
# - Total annual CO₂ emissions from aviation (renamed to Emissions): Emission values
# Usage:
#     python emissions.py <filename>
# Functions:
#     loadData(filePath): Loads and preprocesses the CSV file
#     cleanData(df): Cleans the data by removing incomplete and aggregated records
#     analyzeData(df): Displays summary statistics for the emissions data
#     visualizeData(df): Creates a line plot of emissions over time
#     main(): Entry point of the script
# Dependencies:
#     - pandas
#     - matplotlib
#     - seaborn
#     - sys
# Example:
#     python emissions.py aviation_emissions.csv
#
# Data used for this work is freely available at https://ourworldindata.org/grapher/annual-co-emissions-from-aviation?tab=table
# The comments for this code are generated using the GitHub Copilot. 
# This work does not contain any other uses of generative AI.


def loadData(filePath):
    """
    Reads a CSV file containing aviation emissions data and returns a pandas DataFrame.

    The function renames columns for clarity:
        - 'Entity' is renamed to 'Country'
        - 'Annual CO₂ emissions from aviation (million tonnes)' is renamed to 'Emissions'

    Args:
        filePath (str): Path to the CSV file.

    Returns:
        pandas.DataFrame: DataFrame with renamed columns.
    """
    df = pd.read_csv(filePath)
    # Rename columns to make more sense
    df = df.rename(columns={
        'Entity': 'Country',
        'Total annual CO₂ emissions from aviation': 'Emissions'
        })
    return df

def cleanData(df):
    """
    Cleans the aviation emissions DataFrame by removing incomplete and aggregated data.

    - Drops rows where 'Emissions' is missing or not greater than zero.
    - Removes rows where 'Country' is 'World' to exclude global aggregates.
    - Removes rows with missing 'Code' to exclude regions and keep only countries.

    Args:
        df (pandas.DataFrame): Raw emissions DataFrame.

    Returns:
        pandas.DataFrame: Cleaned DataFrame containing only country-level data with valid emissions.
    """
    # Basic cleaning: drop rows with missing information
    df = df.dropna(subset=['Emissions'])
    df = df[df['Emissions'] > 0]

    # Remove aggregated data for world and regions 
    # because it skews the calculations.
    # Regions have NULL ISO code
    df_no_world = df[df["Country"] != "World"].copy()
    df_countries = df_no_world[df_no_world["Code"].notna()].copy()

    return df_countries


def analyzeData(df):
    """
    Displays summary statistics and yearly emissions statistics for the aviation emissions DataFrame.

    - Prints basic descriptive statistics for all columns.
    - Calculates and prints per-year statistics for 'Emissions', including mean, median, and count.

    Args:
        df (pandas.DataFrame): Cleaned aviation emissions DataFrame.

    Returns:
        None
    """
    print(df.describe())
    print("\n")
    per_year_stats = (
        df.groupby("Year")["Emissions"]
        .agg(mean="mean", median="median", count="size")
        .reset_index()
    )

    print("Emissions per year statistics:")
    print(per_year_stats)


def visualizeData(df):
    """
    Plots a line chart of aviation emissions over time using Seaborn and Matplotlib.

    - Displays emissions ('Emissions') for each year ('Year') in the DataFrame.
    - Sets figure size and axis labels for clarity.

    Args:
        df (pandas.DataFrame): Cleaned aviation emissions DataFrame.

    Returns:
        None
    """
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Year', y='Emissions')
    plt.title('Emissions Over Time')
    plt.xlabel('Year')
    plt.ylabel('Emissions')
    plt.show()


def main():
    """
    Main entry point for the aviation emissions analysis script.

    - Checks for correct command-line usage and prints usage instructions if needed.
    - Sets global pandas display options for float formatting.
    - Loads aviation emissions data from the provided CSV file.
    - Cleans the data to remove incomplete and aggregated records.
    - Analyzes the cleaned data and prints summary statistics.
    - Visualizes emissions data over time with a line chart.

    Args:
        None

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: python emissions.py <filename>")
        return

    # Set global format output from Pandas
    pd.set_option("display.float_format", "{:.2f}".format)

    filename = sys.argv[1]
    df = loadData(filename)
    df = cleanData(df)
    analyzeData(df)
    visualizeData(df)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
A command-line utility to convert temperature from Fahrenheit to Celsius.

This script takes a temperature value in Fahrenheit as a command-line argument
and prints the corresponding value in Celsius.

It handles numeric inputs, including floating-point numbers, and provides
user-friendly error messages for invalid inputs.

Usage:
python3 convert_temp.py

Example:
$ python3 convert_temp.py 77
77.0°F is equivalent to 25.0°C

$ python3 convert_temp.py -40
-40.0°F is equivalent to -40.0°C
"""

import argparse
import sys

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Converts a temperature from Fahrenheit to Celsius.

    The conversion formula used is: C = (F - 32) * 5 / 9.

    Args:
        fahrenheit (float): The temperature in degrees Fahrenheit.

    Returns:
        float: The equivalent temperature in degrees Celsius.
    """
    return (fahrenheit - 32.0) * 5.0 / 9.0
def main():
    """
    Parses command-line arguments, performs the conversion, and prints the result.
    """
    parser = argparse.ArgumentParser(
        description="Convert a temperature from Fahrenheit to Celsius.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n %(prog)s 32 # Outputs 0.0°C"
    )

    parser.add_argument(
        "fahrenheit",
        type=float,
        help="The temperature in degrees Fahrenheit (must be a number)."
    )

    try:
        args = parser.parse_args()
        fahrenheit_temp = args.fahrenheit
        celsius_temp = fahrenheit_to_celsius(fahrenheit_temp)

        # Print the result formatted to one decimal place for clarity
        print(f"{fahrenheit_temp:.1f}°F is equivalent to {celsius_temp:.1f}°C")

    except Exception as e:
        # This block catches potential unforeseen errors, although argparse
        # handles most input validation before this point.
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "main":
    main()
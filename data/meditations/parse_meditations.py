#!/usr/bin/env python3
"""
Parse Meditations full_book.txt and extract quotes into individual files.
Each quote file contains the book title, quote number, and the quote text.
"""

import re
import os
from pathlib import Path

def parse_meditations(input_file, output_dir="quotes"):
    """
    Parse the full_book.txt file and extract quotes into individual files.
    
    Args:
        input_file (str): Path to the full_book.txt file
        output_dir (str): Directory to save the quote files
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into lines to process line by line
    lines = content.split('\n')
    
    current_book = None
    current_quote_num = None
    current_quote_lines = []
    quote_counter = 1
    
    # Book title pattern
    book_pattern = r'^THE\s+(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+BOOK$'
    # Quote number pattern (Roman numerals followed by period)
    quote_pattern = r'^([IVX]+)\.\s+(.*)$'
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this line is a book title
        book_match = re.match(book_pattern, line_stripped)
        if book_match:
            # Save previous quote if we have one
            if current_book and current_quote_num and current_quote_lines:
                save_quote(output_dir, current_book, current_quote_num, current_quote_lines, quote_counter)
                quote_counter += 1
            
            current_book = book_match.group(1)
            current_quote_num = None
            current_quote_lines = []
            print(f"Found book: THE {current_book} BOOK")
            continue
        
        # Check if this line starts a new quote
        quote_match = re.match(quote_pattern, line_stripped)
        if quote_match and current_book:
            # Save previous quote if we have one
            if current_quote_num and current_quote_lines:
                save_quote(output_dir, current_book, current_quote_num, current_quote_lines, quote_counter)
                quote_counter += 1
            
            # Start new quote
            current_quote_num = quote_match.group(1)
            current_quote_lines = [quote_match.group(2)]  # The text after the roman numeral
            continue
        
        # If we're in a quote and this is not an empty line, add to current quote
        if current_book and current_quote_num and line_stripped:
            current_quote_lines.append(line_stripped)
    
    # Save the last quote
    if current_book and current_quote_num and current_quote_lines:
        save_quote(output_dir, current_book, current_quote_num, current_quote_lines, quote_counter)
        quote_counter += 1
    
    return quote_counter - 1  # Return total number of quotes

def save_quote(output_dir, book_name, quote_num, quote_lines, quote_counter):
    """Save a quote to a file."""
    # Join all lines into one text, removing extra whitespace
    quote_text = ' '.join(' '.join(quote_lines).split())
    
    # Create filename with zero-padded counter
    filename = f"quote_{quote_counter:03d}.txt"
    filepath = Path(output_dir) / filename
    
    # Write the quote to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Book: THE {book_name} BOOK\n")
        f.write(f"Quote: {quote_num}\n")
        f.write(f"Text: {quote_text}\n")
    
    print(f"Created {filename}: THE {book_name} BOOK, Quote {quote_num}")

def main():
    """Main function to run the parser."""
    
    # Default paths
    input_file = "full_book.txt"
    output_dir = "quotes"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please make sure the full_book.txt file exists in the data/meditations/ directory.")
        return
    
    print(f"Parsing '{input_file}'...")
    print(f"Output directory: '{output_dir}'")
    print()
    
    try:
        total_quotes = parse_meditations(input_file, output_dir)
        print()
        print("Parsing completed successfully!")
        print(f"Quotes saved to '{output_dir}' directory.")
        print(f"Total quotes extracted: {total_quotes}")
        
    except Exception as e:
        print(f"Error occurred during parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
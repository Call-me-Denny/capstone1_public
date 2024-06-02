import re
import argparse
from jiwer import wer
from difflib import SequenceMatcher

def clean_transcript(transcript):
    # Remove timestamps and names, and line breaks
    cleaned_lines = []
    lines = transcript.split('\n')
    for line in lines:
        # Use regex to remove the timestamp and name
        cleaned_line = re.sub(r'\[\d{2}:\d{2}:\d{2}\] [^:]+: ', '', line)
        cleaned_lines.append(cleaned_line.strip())
    return ' '.join(cleaned_lines)  # Join lines into a single string

def calculate_wer(reference, hypothesis):
    cleaned_reference = clean_transcript(reference)
    cleaned_hypothesis = clean_transcript(hypothesis)
    error_rate = wer(cleaned_reference, cleaned_hypothesis)
    return error_rate

def calculate_cer(reference, hypothesis):
    cleaned_reference = clean_transcript(reference)
    cleaned_hypothesis = clean_transcript(hypothesis)

    # Calculate CER
    matcher = SequenceMatcher(None, cleaned_reference, cleaned_hypothesis)
    cer = 1 - matcher.ratio()

    return cer

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    parser = argparse.ArgumentParser(description='Calculate WER and CER for given transcripts.')
    parser.add_argument('reference', type=str, help='Path to the reference transcript file')
    parser.add_argument('hypothesis', type=str, help='Path to the hypothesis transcript file')
    args = parser.parse_args()

    reference_transcript = read_file(args.reference)
    hypothesis_transcript = read_file(args.hypothesis)

    wer_result = calculate_wer(reference_transcript, hypothesis_transcript)
    cer_result = calculate_cer(reference_transcript, hypothesis_transcript)
    
    print(f'WER: {wer_result}')
    print(f'CER: {cer_result}')

if __name__ == '__main__':
    main()

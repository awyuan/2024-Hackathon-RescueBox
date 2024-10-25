###
#   Basic script which uses EasyOCR to extract text from images in a given file directory
###

import os
import json
from PIL import Image
import easyocr
import easyocr.utils as utils
import argparse
import csv
from polyglot.text import Text

def main():

    # Debug flag
    debug = args.debug

    # Storage Paths
    save_path = 'tool-suite/text_scraper/downloads/'

    # Load languages
    lang_vals = args.lang.split(',')

    # Load EasyOCR model
    reader = easyocr.Reader(lang_vals, model_storage_directory=f'{save_path}/models', user_network_directory=f'{save_path}/user_networks')

    # Get list of images in input directory
    images = [f for f in os.listdir(args.input_dir) if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.JPG')]

    # Extract text from each image
    for image in images:
        if debug:
            print('Reading: ', image)
        # Load image
        img = Image.open(os.path.join(args.input_dir, image))

        # Extract text
        text = reader.readtext(img)
        # Filter out low confidence text:
        text = [t for t in text if t[2] >= args.conf]
        read_dir = 'rtl' if args.lang in ["ar","fa","ur","ug"] else 'ltr'
        paragraphed_text = utils.get_paragraph(text, x_ths=0.1, y_ths=0.5, mode=read_dir)
        # Convert text into a list of dicts
        scraped_texts = []
        for tuple in paragraphed_text:
            text_dict = {}
            # convert coordinates to int values
            for i in range(4):
                tuple[0][i][0] = int(tuple[0][i][0])
                tuple[0][i][1] = int(tuple[0][i][1])
            text_dict['coordinates'] = tuple[0]
            text_dict['text'] = tuple[1]
            # text_dict['confidence'] = float(tuple[2])
            scraped_texts.append(text_dict)

        # # Save extracted text to output directory
        # with open(os.path.join(args.output_dir, image.split('.')[0] + '.json'), 'w') as f:
        #     f.write(json.dumps(output_list)) 
        output_dicts = []
        for row in scraped_texts:
            raw_text = row["text"].strip()
            if raw_text == "":
                continue

            text = Text(raw_text)
            output_dict = {
                "text": row["text"],
                "lang": text.language.code,
                "lang_name": text.language.name,
            }
            if text.language.code == "en":
                    output_dict["entities"] = text.entities
            output_dicts.append(output_dict)
        with open(os.path.join(args.output_dir, image.split('.')[0] + '.json'), 'w') as f:
            f.write(json.dumps(output_dicts))

            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract text from images in a given directory. Keywords: OCR, Text Extraction, TrOCR, Text Scraping, Scraping, Image Input')
    parser.add_argument('input_dir', type=str, help='Directory containing images to extract text from')
    parser.add_argument('output_dir', type=str, help='Directory to save extracted text to')
    parser.add_argument('--lang', type=str, help='Language(s) to extract text in. Pass in as a comma-separated string. Default is "en" for English. For the list of pairs that funciton, you may need to read easyocr.py source code.', default='en')
    parser.add_argument('--conf', type=float, help='Minimum confidence level for text extraction. Default is 0.5', default=0.5)
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    args = parser.parse_args()
    main()
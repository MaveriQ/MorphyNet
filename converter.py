import pandas as pd
import os, pdb, sys
from tqdm import tqdm
import argparse

sys.setrecursionlimit(100)
langs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and not d.startswith('.') and len(d)==3]

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, default='eng',choices=langs+['all'])
    parser.add_argument('--output_dir', type=str, default='./processed')

    tmp = "--lang deu --output_dir ./".split()
    args = parser.parse_args()
    return args


def load_data(lang):
    deriv = pd.read_csv(f'{lang}/{lang}.derivational.v1.tsv',sep='\t',names=['source_word','target_word','source_pos','target_pos','morpheme','type'])
    # infl = pd.read_csv(f'{lang}/{lang}.inflectional.v1.tsv',sep='\t',names=['lemma','inflected_form','morph_feat','morph_seg'])
    return deriv#,infl

def get_segment(deriv,source_word):
    # pdb.set_trace()
    result = deriv.query(f"target_word=='{source_word}'")
    if len(result)==0:
        return (source_word,)
    else:
        source_word = result.source_word.values[0]
        morpheme = result.morpheme.values[0]
        typ = result.type.values[0]
        
        previous_segment = get_segment(deriv,source_word)
        
        if typ=='prefix':
            return morpheme+'#',*previous_segment
        elif typ=='suffix':
            return *previous_segment,'#'+morpheme
        
def process_lang(lang):
    deriv = load_data(lang)
    segments={}
    errors = 0
    for row in tqdm(deriv.iterrows(),total=len(deriv)):
        index = row[0]
        try:
            seg = get_segment(deriv,row[1].target_word)
            segments[index]=seg
        except Exception as e:
            segments[index]=e
            errors += 1

    print(f'Errors: {errors}/{len(deriv)}')
    deriv['segments']=pd.Series(segments)
    return deriv

def main():
    args = get_args()
    os.makedirs(args.output_dir,exist_ok=True)

    if args.lang=='all':
        for idx,lang in enumerate(langs):
            if os.path.exists(f'{args.output_dir}/{lang}.derivational.v1.csv'):
                print(f'{lang} already processed. Skipping...')
                continue
            print(f'Processing {lang} ({idx+1}/{len(langs)})')
            deriv = process_lang(lang)
            deriv.to_csv(f'{args.output_dir}/{lang}.derivational.v1.csv',index=False)
    else:
        deriv = process_lang(args.lang)
        deriv.to_csv(f'{args.output_dir}/{args.lang}.derivational.v1.csv',index=False)

if __name__ == '__main__':
    main()
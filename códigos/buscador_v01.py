from nltk.corpus        import stopwords
from nltk.tokenize      import word_tokenize
from nltk.stem.porter   import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.probability   import FreqDist

from os       import listdir
from os.path  import isfile, join
from math     import log2
from datetime import datetime as dt

import re
import numpy  as np
import pandas as pd



def log(tx):
    print(dt.now() , tx)

#------------------------------------------------------------------------------
def get_doc(file):
    docs = {} 

    ab = False
    abkey = ""
    abvalue = ""

    for line in open(file):

        if(ab):
            if (line[:2] == "  "):
                abvalue += line[2:]
            else:
                ab = False
                docs[abkey.replace(" ","")] = abvalue.replace("\n","").lower()
        else:
            if (line[:2] == "RN"):
                abkey = line[2:].rstrip()
            
            elif (line[:2] == "AB"):
                abvalue = line[2:]
                ab = True
    return docs
    
#------------------------------------------------------------------------------
def get_all_docs(path_files):
    
    all_files = [f for f in listdir(path_files) if isfile(join(path_files, f))]
    
    all_docs = {}
    
    for file in all_files:
        all_docs.update(get_doc(join(path_files,file)))
        
    return all_docs
   
#------------------------------------------------------------------------------
def token_treated(tx):
    sw = set(stopwords.words('english'))
    sb = SnowballStemmer("english")
    ps = PorterStemmer()
    
    # removing all characters different of a-zA-Z
    tx = re.sub('[^a-zA-Z]',' ',tx)
    
    words = word_tokenize(tx)

    wf = []
    # removing stopwords and applying stemming
    for w in words:
        
        w = sb.stem(w)
        w = ps.stem(w)
        
        if w not in sw:
            wf.append(w)
   
    return wf

#------------------------------------------------------------------------------
def main():
    
    log("starting process...")
    
    path_files = 'D:\\git\\infnet-criando-um-buscador\\dados'
    
    inverted_index = {}
    
    docs = get_all_docs(path_files)
    
    key_docs = []

    log("concating all text of all docs in just one")
    all_text = ''
    for key, value in docs.items():
        all_text += value + " "
        key_docs.append(key)

    log("building all possible tokens")
    all_words = token_treated(all_text)

    # cleaning the memory
    del all_text

    log("building all possible keys")
    for w in all_words:
        inverted_index[w] = []

    # cleaning the memory
    del all_words

    log("listing all docs and append to de main dict...")
    for key, value in docs.items():
        
        # building tokens of document
        aw = token_treated(value)
        
        # add the document on inverted index
        for w in aw:
            inverted_index[w].append(key)

    log("sorting the lists to build the df...")
    ixs = sorted(key_docs)
    cols = sorted(list(inverted_index.keys()))
    
    log("building the idf's values...")
    idf = {}
    for key, value in inverted_index.items():
        idf[key] = log2(len(key_docs) / float(len(value)))
    
    log("preparing the shape of df...")
    shape = (len(ixs),len(cols))
    zeros = np.zeros(shape, dtype=int)
    
    log("building df...")
    df = pd.DataFrame(data=zeros,index=ixs,columns=cols)
    
    log("calculating the values of tf * idf...")
    for i in ixs:
        for j in cols:
            fd = FreqDist(inverted_index[j])
            df.loc[i,j] = fd[i] * float(idf[j])
    
    log("end process...")
    
    print(df.head())

#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
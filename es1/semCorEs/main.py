import nltk
from nltk.corpus import semcor
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import random
from tqdm import tqdm
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('semcor')

tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english'))


def lesk_algorithm(word, sentence):
    senses_list = wn.synsets(word)
    best_sense = senses_list[0]
    max_overlap = 0
    context = sentence  # list of words
    for sense in senses_list:
        signature = get_signature(sense)
        overlap = compute_overlap(signature, context)
        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense
    return best_sense


def get_signature(s):
    definition = s.definition()
    examples = ' '.join(s.examples())
    signature = definition + examples
    word_tokens = tokenizer.tokenize(signature)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence


def compute_overlap(signature, context):
    overlap = 0
    for a_signature in signature:
        for a_context in context:
            if a_signature.lower() == a_context.lower():
                overlap += 1
    return overlap


def get_sentence_file(path):
    res = []
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.replace('\n', "").replace('-', "").strip()
            if not line.startswith('#') and not line == '':
                sp = line.split('**')
                sentence = ' '.join(sp)
                token_sentence = tokenizer.tokenize(sentence)
                filtered_sentence = [
                    w for w in token_sentence if not w in stop_words]
                res.append((sp[1], filtered_sentence))
    return res


def get_brown(list_sentences):
    final_list = list(map(lambda s: ' '.join(s), list_sentences))
    return final_list


def get_random_word_brown():
    sentences = get_brown(semcor.sents('brown2/tagfiles/br-n12.xml'))
    list1 = semcor.tagged_chunks('brown2/tagfiles/br-n12.xml', 'pos')
    list2 = semcor.tagged_chunks('brown2/tagfiles/br-n12.xml', 'sem')

    random_word = []
    temp_buffer = []
    i = 0
    for t in tuple(zip(list1, list2)):
        pos = t[0].label()
        lemma = t[0][0]

        if pos == "NN" and hasattr(t[1], 'label'):
            if hasattr(t[1].label(), 'synset'):
                synset = t[1].label().synset()
                if hasattr(synset, 'name'):
                    temp_buffer.append((synset.name(), lemma))

        s = sentences[i]
        eof = s[-1:]
        if lemma == eof:
            if len(temp_buffer) != 0:
                random_word.append(random.choice(temp_buffer))
            else:
                random_word.append((' ', ' '))
            temp_buffer = []
            i += 1
    return zip(random_word, sentences)


# PARTE 1
sentences = get_sentence_file('sentences.txt')
for s in sentences:
    print(' '.join(s[1]))
    print(f'Best Sense for {s[0]}: {lesk_algorithm(s[0], s[1]).definition()}')
    print('-------------------\n')

print("\n###########################\n\n")

# PARTE 2
sentences = get_random_word_brown()
acc_score = 0
for i, s in enumerate(sentences):
    s_split = s[1].split()
    if not s[0] == (' ', ' ') and i < 50:
        target = s[0][0]
        print(f'Sentence: {s[1]}')
        res = lesk_algorithm(s[0][1], s_split)
        print(f'Best sense for **{s[0][1]}**: {res.definition()}')
        print(f'Target Sense: {target}, Find Sense: {res.name()}')
        if target == res.name():
            acc_score = acc_score + 1
        print('-------------------\n')
print(f'SemCor Accuracy Results: {acc_score}/50')
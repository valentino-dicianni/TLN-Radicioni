from nltk.corpus import semcor
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random


def lesk_algorithm(word, sentence):
    senses_list = wn.synsets(word)
    best_sense = senses_list[0]
    max_overlap = 0
    context = sentence  # lista di parole
    for sense in senses_list:
        signature = get_signature(sense)
        overlap = compute_overlap(signature, context)

        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense
    return best_sense


def get_signature(s):
    stop_words = set(stopwords.words('english'))
    definition = s.definition()
    examples = ' '.join(s.examples())
    signature = definition + examples
    word_tokens = word_tokenize(signature)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence


def compute_overlap(signature, context):
    overlap = 0
    for a_signature in signature:
        for a_context in context:
            if a_signature == a_context:
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
                sentence = list(filter(None, (sp[0] + " " + sp[1] + " " + sp[2]).replace("  ", " ").split(" ")))
                res.append((sp[1], sentence))
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

        # cerca l'end of sentence (non sempre è il punto '.'TODO: fix it)
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
for i, s in enumerate(sentences):
    s_split = s[1].split()
    if not s[0] == (' ', ' ') and i < 50:
        target = s[0][0]
        print(f'Sentence: {s[1]}')
        res = lesk_algorithm(s[0][1],s_split)
        print(f'Best sense for **{s[0][1]}**: {res.definition()}')
        print(f'Target Sense: {target}, Find Sense: {res}')
        print('-------------------\n')

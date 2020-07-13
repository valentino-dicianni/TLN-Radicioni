import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import numpy as np
import math
import csv
from tqdm import tqdm

# depth_max = max(max(len(hyp_path) for hyp_path in ss.hypernym_paths()) for ss in wn.all_synsets())
depth_max = 20


def get_lines(path):
    res = []
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for index, row in enumerate(csv_reader):
            if index > 0:
                res.extend([(row[0], row[1], row[2])])

    return res


def map_range(value, min, max):
    return (value - min) / (max - min) * 10


def similarity(w1, w2, measure):
    synset1 = wn.synsets(w1, pos=wn.NOUN)
    synset2 = wn.synsets(w2, pos=wn.NOUN)
    res = []
    score = 0.0

    if len(synset1) != 0 and len(synset2) != 0:
        for s1 in synset1:
            for s2 in synset2:
                if measure == 1:
                    score = wp_similarity(s1, s2)

                elif measure == 2:
                    score = sp_similarity(s1, s2)

                elif measure == 3:
                    score = lc_similarity(s1, s2)

                ######## FOR TESTING ############
                elif measure == 4:
                    score = s1.wup_similarity(s2)

                elif measure == 5:
                    score = s1.lch_similarity(s2)

                elif measure == 6:
                    score = s1.path_similarity(s2)
                #################################

                res.append(score)
        return max(res)

    # if there are no senses for words
    return 0.0


def wp_similarity(s1, s2):
    lcs = s1.lowest_common_hypernyms(s2)
    if len(lcs) > 0:
        n = 2 * lcs[0].max_depth()
        d = s1.max_depth() + s2.max_depth()
        return map_range(n / d, 0, 1)
    else:
        return 0


def sp_similarity(s1, s2):
    len = get_len(s1, s2)
    res = 2 * depth_max - len
    return map_range(res, 0, 2 * depth_max)


def lc_similarity(s1, s2):
    len = get_len(s1, s2)
    if len == 0:
        result = -1 * math.log(1 / (2 * depth_max + 1))
    else:
        result = -1 * math.log(len / (2 * depth_max))
    return map_range(result, 0, math.log(2 * depth_max + 1))


def distance(from_s, to_s):
    paths = from_s.hypernym_paths()
    d = 0
    for path in paths:
        if to_s in set(path):
            index = path.index(to_s)
            d = len(path[index:])
            break
    return d


def get_len(s1, s2):
    result = 0

    # if they are the same sense
    if s1 == s2:
        return result

    lcs = s1.lowest_common_hypernyms(s2)
    # if they have a common hyperonyms
    if len(lcs) > 0:
        d1 = distance(s1, lcs[0])
        d2 = distance(s2, lcs[0])
        result = d1 + d2 - 1

    return result


def pearson_correlation(target_score, actual_score):
    t = list(map(lambda x: float(x), target_score))
    a = list(map(lambda x: float(x), actual_score))

    return np.cov(t, a)[0][1] / (np.std(t) * np.std(a))


def spearmanCoefficient(target_score, actual_score):
    r_ts = rank_array(target_score)
    r_as = rank_array(actual_score)
    return np.cov(r_ts, r_as)[0][1] / (np.std(r_as) * np.std(r_ts))


def rank_array(a):
    array = np.array(a)
    order = array.argsort()
    ranks = order.argsort()
    return list(map(lambda x: float(x + 1), ranks))

couples = get_lines('WordSim353.csv')
wuAndPalmer = []
shortestPath = []
leakcockChodorow = []

t_wuAndPalmer = []
t_shortestPath = []
t_leakcockChodorow = []

target = []

for c in tqdm(couples):
    wuAndPalmer.append(similarity(c[0], c[1], 1))
    shortestPath.append(similarity(c[0], c[1], 2))
    leakcockChodorow.append(similarity(c[0], c[1], 3))
    target.append(c[2])

    t_wuAndPalmer.append(similarity(c[0], c[1], 4))
    t_shortestPath.append(similarity(c[0], c[1], 5))
    t_leakcockChodorow.append(similarity(c[0], c[1], 6))

print(f'# Pearson Correlation coefficient for Wu & Palmer: {pearson_correlation(target, wuAndPalmer)}, '
      f'target_nltk: {pearson_correlation(target, t_wuAndPalmer)}')
print(f'# Pearson Correlation coefficient for Leakcock & Chodorow: {pearson_correlation(target, leakcockChodorow)}, '
      f'target_nltk: {pearson_correlation(target, t_leakcockChodorow)}')
print(f'# Pearson Correlation coefficient for Shortest Path: {pearson_correlation(target, shortestPath)}, '
      f'target_nltk: {pearson_correlation(target, t_shortestPath)}')

print('----------------------------------------------------')

print(f'# Spearmans rank correlation coefficient for Wu & Palmer: {spearmanCoefficient(target, wuAndPalmer)}, '
      f'target_nltk: {spearmanCoefficient(target, t_shortestPath)}')
print(f'# Spearmans rank correlation coefficient for Leakcock & Chodorow: {spearmanCoefficient(target, leakcockChodorow)}, '
      f'target_nltk: {spearmanCoefficient(target, t_leakcockChodorow)}')
print(f'# Spearmans rank correlation coefficient for Shortest Path: {spearmanCoefficient(target, shortestPath)}, '
      f'target_nltk: {spearmanCoefficient(target, t_shortestPath)}')


import itertools

# # Helper function
# def process_vocab_products(subjects: list[str],objects: list[str]) -> list[list[str]]:
#     nouns = list(set(subjects + objects))
#     all_permutations = list(itertools.permutations(nouns,2)) # returns tuple, so convert to mutable list
#     clean_permutations=[]
#     for item in all_permutations:
#         if item[0] != item[1]:
#             clean_permutations.append(item)
#     return clean_permutations


def process_vocab_products(subjects: list[str], objects: list[str]) -> list[list[str]]:
    nouns = list(set(subjects + objects))
    return [list(pair) for pair in itertools.combinations(nouns, 2)]

if __name__ == "__main__":

    subs = ['I','you']
    obs = ['I','cat']

    clean = process_vocab_products(subs,obs)
    print(clean)

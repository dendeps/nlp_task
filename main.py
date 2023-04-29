from flask import Flask, jsonify, request
from nltk.tree import Tree
from itertools import permutations

NODE_COMMA = Tree.fromstring("(, ,)")
NODE_OR = Tree.fromstring("(CC )")


def dump_trees(trees):
    out_list = []
    for t in trees:
        out_list.append({"tree": " ".join(str(t).split())})
    return out_list


def is_swappable(subtree):
    """Checks if nodes in the subtree are swappable."""
    if NODE_COMMA not in subtree and NODE_OR not in subtree:
        return False
    allowed_labels = {',', 'CC', 'NP'}
    for node in subtree:
        if node.label() not in allowed_labels:
            return False
    return True


def permutate_np(subtree):
    """Create all possible permutations for the NP subtree."""
    mutable_indexes = []
    for i, n in enumerate(subtree):
        if n.label() == 'NP':
            mutable_indexes.append(i)

    res = []
    for permutation in permutations(mutable_indexes):
        copy = subtree.copy()
        for old_idx, new_idx in zip(mutable_indexes, permutation):
            copy[old_idx] = subtree[new_idx]
        res.append(copy)
    return res


def make_parmutations(in_tree):
    """Recursive function to make permutations on tree nodes."""
    # If the list has only one element, return it as a single permutation
    if len(in_tree) == 1:
        return [in_tree]

    # If the list is swappable, use a specialized function to generate permutations
    if is_swappable(in_tree):
        return permutate_np(in_tree)

    # Create a copy of the input list to store the permutations
    permutations = [in_tree.copy()]

    # Iterate over the list and its sub-lists
    for i, sub_list in enumerate(in_tree):
        # Generate all possible permutations for the sub-list
        sub_permutations = make_parmutations(sub_list)

        # Generate all possible combinations of the sub-permutations with the existing permutations
        new_permutations = []
        for permutation in permutations:
            for sub_permutation in sub_permutations:
                # Create a new permutation by replacing the sub-list with its sub-permutation
                new_permutation = permutation.copy()
                new_permutation[i] = sub_permutation
                new_permutations.append(new_permutation)

        # Store the new permutations for the next iteration
        permutations = new_permutations

    return permutations


app = Flask(__name__)


@app.route('/paraphrase', methods=['GET'])
def paraphrase_endpoint():
    data = request.args.get('tree')
    return jsonify(paraphrase(data))


def paraphrase(data):
    # create Tree and process
    tree = Tree.fromstring(data)
    out_trees = dump_trees(make_parmutations(tree))
    return {'paraphrase': out_trees}


if __name__ == '__main__':
    app.run(debug=True)



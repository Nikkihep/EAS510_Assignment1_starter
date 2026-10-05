"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).
"""

import rules
import numpy as np
import cv2

# The rules’ point weights must still sum to 100 so the Final Score stays on a /100 scale
# Since we are adding a rule, we need to adjust the weights of rules 1-3
# Rule 1 = 25 points
# Rule 2 = 25 points
# Rule 3 = 40 points
# Rule 4 = 10 points

def rule1_metadata_v2(target, input_path):
    result = rules.rule1_metadata(target, input_path)
    result["score"] = round(result["score"] * 25/30)
    result["out_of"] = 25
    return result

def rule2_histogram_v2(target, input_path):
    result = rules.rule2_histogram(target, input_path)
    result["score"] = round(result["score"] * 25/30)
    result["out_of"] = 25
    return result

def rule3_template_v2(target, input_path):
    result = rules.rule3_template(target, input_path)
    result["out_of"] = 40
    return result

#: Import the original rules and append your new one.
RULES = ("rule1_metadata_v2", "rule2_histogram_v2", "rule3_template_v2", "rule4_edges")

def rule4_edges(target, input_path):
    """TODO: replace with your Phase 2 rule that fixes the V1 weakness.

    Starter returns a no-op so the pipeline still runs before you implement it.
    Parity with rules.py rule dict: rule/name/fired/score/out_of/note/metric.
    """
    out = {
      "rule": 4,
      "name": "Edges",
      "fired": False,
      "score": 0,
      "out_of": 10,
      "note": "Edge similarity 0.00",
      "metric": 0.0,
    }

    # target["path"]: the path to the registered original
    src = cv2.imread(target["path"], cv2.IMREAD_GRAYSCALE)
    # input_path: the modified/hard image we are trying to identifty
    suspect = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    if src is None or suspect is None:
         return out

    # Create the edge maps
    # cv2.Canny() looks for sharp changes in brightness (normally corresponding to edges)
    src_edges = cv2.Canny(src, 100, 200) # edges from the original image
    suspect_edges = cv2.Canny(suspect, 100, 200) # edges from the image we are trying to identify

    # Ensure that both edge maps are the same size
    src_edges = cv2.resize(src_edges, (256, 256))
    suspect_edges = cv2.resize(suspect_edges, (256,256))

    # Compare the two edge maps
    # cv2.absdiff() compares the two edge images pixel-by-pixel
    difference = cv2.absdiff(src_edges, suspect_edges) # if edges are very similar, the difference is small
    similarity = 1.0 - (np.mean(difference) / 255.0) # higher result means the images are more similar

    similarity = max(0.0, min(1.0, float(similarity))) # ensures similarity is between 0 and 1

    if similarity >= 0.5:
         score = int(round(10 * similarity)) # coverts similarity into 10-point score
    else:
         score = 0

    out["metric"] = round(similarity, 3)
    out["note"] = f"Edge similarity {similarity:.2f}"

    if similarity >= 0.5:
         out["fired"] = True
         out["score"] = score
    
    return out
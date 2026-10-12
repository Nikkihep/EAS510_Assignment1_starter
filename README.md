# EAS 510 - Assignment 1: Digital Forensics Apprentice

A rule-based expert system that matches modified images back to their originals.

This is the **starter repository** for Project 1. Two repositories matter:

| Repository | Role |
|------------|------|
| `delveccj/EAS510_Assignment1_starter` (this repo) | Your **code** lives here. You will fork it, work in your fork, and push your final submission here. |
| `delveccj/EAS510_Assignment1` | The **dataset** (read-only). Clone it for the images; never commit it to your fork. |

## Setup on your Codio box

```bash
# 1. Fork this repo on GitHub, then in your box:
git clone https://github.com/YOUR-USERNAME/EAS510_Assignment1_starter.git
cd EAS510_Assignment1_starter

# 2. Clone the read-only dataset as a sibling folder (images live there):
cd ~/workspace
git clone https://github.com/delveccj/EAS510_Assignment1.git

# 3. Install dependencies:
cd ~/workspace/EAS510_Assignment1_starter
python3 -m pip install -r requirements.txt

# 4. Point this box at YOUR fork (run once):
./setup_git.sh
```

## Repository layout

```
forensics_detective.py   SimpleDetector: register targets + find_best_match
rules.py                 Rule functions (Rule 1: Metadata, Rule 2: Histogram, Rule 3: Template)
test_system.py           Runs the detector over the data folders and writes results_*.txt
scripts/check_output_format.py   Validates a results file against the required format
setup_git.sh, submit.sh  One-time setup + commit/push helper ("backup button")
```

## The task in one paragraph

Implement three interpretable rules (metadata, color histogram, template matching)
that combine into a 0-100 confidence score. Run your system on `modified_images/`
and `random/` and save the full output as `results_v1.txt`. In Phase 2, run on
`hard/`, diagnose a systematic failure, add a **Rule 4**, and save
`results_v1_hard.txt` and `results_v2.txt`. Full instructions are in the Codio guide
and in the assignment PDF in UBLearns.

## Running

```bash
# Phase 1 (easy + random) -> results_v1.txt
python3 test_system.py --modified --random --output results_v1.txt

# Phase 1 on hard cases -> results_v1_hard.txt
python3 test_system.py --hard --output results_v1_hard.txt

# Phase 2 (everything) -> results_v2.txt
python3 test_system.py --modified --hard --random --output results_v2.txt

# Validate any results file against the required format:
python3 scripts/check_output_format.py results_v1.txt
```

The data folders are resolved from a sibling clone of `EAS510_Assignment1`.
If your data is elsewhere, pass `--data-dir /path/to/EAS510_Assignment1`.

## Output format (do not alter)

```
Processing: modified_image_01.jpg
Rule 1 (Metadata): FIRED - Size ratio 0.85 -> 20/30 points
Rule 2 (Histogram): FIRED - Correlation 0.92 -> 25/30 points
Rule 3 (Template): FIRED - Match score 0.76 -> 30/40 points
Final Score: 75/100 -> MATCH to original_03.jpg
```

## Backup doctrine

Your Codio box can be reset at any time. **Your fork on GitHub is the only safe
copy.** After every milestone run `./submit.sh "describe what you did"`. A box
restart never touches GitHub.

## License

Apache 2.0. See `LICENSE`.

## Observed weakness in V1: what failed and why
After analyzing the Rules, Rule 1 detects file size and pixel dimensions, Rule 2 detects distribution of pixel colors, and Rule 3 detects patterns physically lining up inside the original. The original rules detected 32 images correctly out of the 75 total images. The majority of those failed images were cropped, so we needed to determine which rules had the most effect on detecting those correctly. The cropped images receive the majority score from Rule 2 with some additional points from Rule 1. Since Rule 2 carries most of the weight for the cropped images, we don't want to edit Rule 2 in case we hurt the score that it is currently contributing. Therefore, we should instead adjust Rule 1.  We don't want to directly increase if out["metric"] >= 0.6, since that could incorrectly classify the random images as correct. Cropping changes the dimension size of the images, with both width and height, so adding code to the metric that includes dimension size could improve accuracy for the cropped images. The addition of dimension sizing only increased accuracy to 38 images correctly guessed. Editing Rule 1 did not make a huge impact on accuracy and since Rule 2 already performs well, we should turn our attention to Rule 3.

Rule 3 determines whether a pattern physically lines up inside the original which is especially beneficial for the cropped images. However, template matching can struggle when an image is resized because the size of its patterns change. To address this, I modified RUle 3 to scale both images by a common facor before performing the template mathching so patterns are easier to detect. After modifying Rule 3, the number of correctly detected images increases from 38 to 58 out of 75. However, the rules struggled with the majority of 25% and 50% crops. After running the hard cases on version 1, 47 out of the 60 images passed. The images that were rejected failed for Rule 3, so the template matching is still struggling to detect images correctly. The images that fail for the hard cases are once again crops and resized images.

## Design decision for V2: what Rule 4 is and why you chose it
Since Rule 3 still struggled with some cropped images, I wanted to add a different method of comparing images rather than relying solely on template matching. SIFT/ORB compares distinctive local features between images, while multi-scale template matching compares pixel patterns at different sizes. I decided to start with Canny edge detection because I wanted to test whether comparing image outlines would improve the overall accuracy for cropped and resized images. Canny edge detection turns the image to grayscale and uses changes in the brightness to identify edges and boundaries. The generated edge maps are then used to compare the outlines of the original and modified images. I choose this method in hope that important edges might still be recognizable even when an image has been cropped, resized, or compressed. Rule 4 only contributes 10 points to the overall score, so with more tuning of Rule 3, the addition of Rule 4 could push an image over the 50 point threshold.

## Effect of the change: accuracy before/after on easy vs hard
One of the requirements for the project was that all 15 of the random images were rejected. Both Version 1 and Version 2 successfully rejected all 15 random random images. For the 60 "easy" modified images, Version 1 detected 58 images, while Version 2 detected 59 images. This means that Rule 4 improved detection by one image in the easy modified set. For the hard set of images, Version 1 detected 47 out of the 60 images, while Version 2 detected 50 out of the 60 images. Once again, Rule 4 improved detection by three images. Overall, Version 1 correctly identified 105 out of 135 images, giving an accuracy of 77.8%. Version 2 correctly classified 109 out of 135 images, giving an accuracy of 80.7%. Rule 4 showed some improvement by increasing overall accuracy by approximately 3 percent. Rule 4 proved to be most beneficial towards the hard cases, but the overall improvement was relatively small.

## Trade-offs: what new costs or risks did Rule 4 introduce
All 15 random images were rejected overall. However, Rule 4 assigned high edge-similarity scores to unrelated random images. All 15 random images received a passing score from Rule 4. The random noise images scored 6/10, while the other random images scored 10/10. This suggests that unrelated images images can have similar outlines or edge patterns to the original images. Keeping Rule 4 weighted at 10 points is important to ensure that edge similarity does not dominate the final score, especially since all the random images received a pass. Rule 4 also introduced additional image-processing operations, including Canny edge detection, resizing, and edge-map comparison. These operations require additional computation for each image. Although Rule 4 improved overall accuracy by approximately 3 percent, it only produced four additional correct classifications. It helped more with the hard set than with the easy modified images, but edge detection did not completely solve the original problem with cropped and resized images.

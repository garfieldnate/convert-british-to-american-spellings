"""python convert_to_json.py lib/Words/AmericanBritish/
outputs lib/Words/AmericanBritish/british_to_american_A.json, etc.
prints warnings for data integrity issues (in terms of the British -> American conversion task)
"""
from distutils.log import warn
import json
import sys
from pathlib import Path


def main(dir):

    all_uk = set()
    all_us = set()

    for child in Path(dir).iterdir():
        us_to_uk = extract_american_to_british(child)
        uk_to_us = reverse_direction(us_to_uk)

        all_us |= set(us_to_uk.keys())
        all_uk |= set(uk_to_us.keys())

        child.name
        letter = child.stem[-1]
        with (child.parent / f"en_normalized_{letter}.json").open("w") as f:
            json.dump(uk_to_us, f, indent=2)
    
    spellings_in_both = sorted(list(all_us & all_uk))
    if spellings_in_both:
        warn(f"{len(spellings_in_both)} spellings in both US and UK: {spellings_in_both}")
        warn("Above warning must be manually fixed")

def reverse_direction(us_to_uk):
    uk_to_us = {}
    warning_count = 0
    for us, uk_list in us_to_uk.items():
        for uk in uk_list:
            if uk == us:
                # no use converting "sopovov" to "sopovov", etc.
                continue
            elif uk in uk_to_us:
                warning_count += 1
                warn(f"{uk} mapped to both {uk_to_us[uk]} and to {us}")
            else:
                uk_to_us[uk] = us
    if warning_count:
        warn(f"above {warning_count} warnings must be manually fixed")
    return uk_to_us

def extract_american_to_british(file):
    words = {}
    for line in file.open():
        if "=>" in line:
            american_raw, british_raw = line.split("=>")
            american = extract_word(american_raw)
            british = extract_word_list(british_raw)
            if len(set(british)) != len(british):
                warn(f"\033[41mFix in source:\033[0m duplicates found in {british}")
            words[american] = british
    return words

def extract_word_list(raw):
    stripped = raw.strip().strip("[],")
    return [extract_word(w) for w in stripped.split(",")]

def extract_word(raw):
    return raw.strip().strip("'").replace("\\", "")

if __name__ == "__main__":
    main(sys.argv[1])

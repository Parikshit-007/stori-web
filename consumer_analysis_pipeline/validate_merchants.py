"""
Validator for merchant_keywords.json
Run this after adding new keywords to check for errors
"""

import json
import sys
from pathlib import Path


def validate_merchant_keywords():
    """Validate the merchant keywords JSON file"""
    json_path = Path(__file__).parent / "merchant_keywords.json"
    
    print("\n" + "="*80)
    print("MERCHANT KEYWORDS VALIDATION")
    print("="*80)
    
    # Step 1: Check if file exists
    if not json_path.exists():
        print(f"\n❌ ERROR: {json_path} not found!")
        return False
    
    print(f"\n[OK] File exists: {json_path}")
    
    # Step 2: Try to parse JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("[OK] JSON format is valid")
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON ERROR at line {e.lineno}, column {e.colno}:")
        print(f"   {e.msg}")
        print("\n   Common fixes:")
        print("   - Check for missing commas between items")
        print("   - Check for extra comma after last item")
        print("   - Make sure all strings are in \"quotes\"")
        return False
    except Exception as e:
        print(f"\n❌ ERROR reading file: {e}")
        return False
    
    # Step 3: Validate structure
    categories_found = 0
    total_keywords = 0
    all_keywords = []
    duplicates = []
    
    for category, content in data.items():
        if category.startswith("_"):
            continue  # Skip metadata
        
        if not isinstance(content, dict):
            print(f"\n[WARNING] Category '{category}' is not a dictionary")
            continue
        
        keywords = content.get("keywords", [])
        if not keywords:
            print(f"\n[WARNING] Category '{category}' has no keywords")
            continue
        
        categories_found += 1
        total_keywords += len(keywords)
        
        # Check for duplicates within category
        seen = set()
        for kw in keywords:
            kw_upper = kw.upper()
            if kw_upper in seen:
                duplicates.append(f"'{kw}' in {category}")
            seen.add(kw_upper)
            all_keywords.append((kw_upper, category))
    
    print(f"[OK] Found {categories_found} categories")
    print(f"[OK] Total keywords: {total_keywords}")
    
    # Step 4: Check for duplicate keywords across categories
    global_seen = {}
    global_duplicates = []
    for kw, cat in all_keywords:
        if kw in global_seen:
            global_duplicates.append(f"'{kw}' in both {global_seen[kw]} and {cat}")
        else:
            global_seen[kw] = cat
    
    # Step 5: Report results
    print("\n" + "="*80)
    if duplicates:
        print("[WARNING] DUPLICATES WITHIN CATEGORIES:")
        for dup in duplicates[:10]:  # Show first 10
            print(f"   - {dup}")
        if len(duplicates) > 10:
            print(f"   ... and {len(duplicates) - 10} more")
    
    if global_duplicates:
        print("\n[WARNING] KEYWORDS IN MULTIPLE CATEGORIES:")
        for dup in global_duplicates[:10]:
            print(f"   - {dup}")
        if len(global_duplicates) > 10:
            print(f"   ... and {len(global_duplicates) - 10} more")
        print("\n   Note: This is usually OK if keyword belongs in both categories")
    
    # Step 6: List categories
    print("\n" + "="*80)
    print("CATEGORIES FOUND:")
    for category in sorted(data.keys()):
        if category.startswith("_"):
            continue
        kw_count = len(data[category].get("keywords", []))
        desc = data[category].get("description", "No description")
        print(f"  {category:25} : {kw_count:3} keywords - {desc}")
    
    print("\n" + "="*80)
    if not duplicates and not global_duplicates:
        print("[SUCCESS] VALIDATION PASSED - No issues found!")
    else:
        print("[SUCCESS] VALIDATION PASSED - See warnings above")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = validate_merchant_keywords()
    sys.exit(0 if success else 1)

